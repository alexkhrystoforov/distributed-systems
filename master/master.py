import user_pb2_grpc as user_pb2_grpc
import user_pb2 as user_pb2
import master_to_secondary_pb2_grpc as master_to_secondary_pb2_grpc
import master_to_secondary_pb2 as master_to_secondary_pb2
import health_pb2_grpc as health_pb2_grpc
import health_pb2 as health_pb2

from concurrent import futures
import threading
import time
import grpc
import logging
import math


_ONE_DAY_IN_SECONDS = 60 * 60 * 24

data_dict = {'id': [], 'msg': []}
servers_ports = ["localhost:50052", "localhost:50053"]

quorum = math.ceil(len(servers_ports) + 1 // 2)
waiting_msg = []
waiting_id = []

heartbeats = 0
health_status = 0


def fib(n):
    def fib_help(a, b, n):
        return fib_help(b, a + b, n - 1) if n > 0 else a
    return fib_help(0, 1, n)

# delays = [fib(i)/2 for i in range(1,16)]
delays = [math.exp(x) for x in range(1,7)]


class UserServicer(user_pb2_grpc.UserServiceServicer):
    def append(self, request, context):
        quorum_status = [True]

        for port in servers_ports:
            quorum_status.append(heartbeat(port, True))

        if sum(quorum_status) < quorum:
            return user_pb2.UserPostResponse(success='there is no quorum the'
                                                     'master is switched into read-only mode')

        if request.write_concern > len(servers_ports)+1:
            return user_pb2.UserPostResponse(success='Post request is declined.'
                                                         'write concern is too big,'
                                                         f'the biggest possible w={len(servers_ports)+1}')

        _, cur_id = save(request)
        latch = CountDownLatch(request.write_concern - 1)

        for port in servers_ports:
            t = threading.Thread(target=replicate_method, args=[request.msg, cur_id, port, latch])
            t.start()

        latch.a_wait()

        return user_pb2.UserPostResponse(success=f'SUCCESS: {request}')

    def get(self, request, context):
        if request.get:
            print("Process get request...")
            return user_pb2.UserGetResponse(msg=data_dict.get('msg'))


def replicate_method(request_msg, cur_id, port, latch):
    global data_dict
    global waiting_msg

    try:
        with grpc.insecure_channel(port) as channel:
            print(f'Start replication to secondary with port {port} \n')
            stub = master_to_secondary_pb2_grpc.MasterServiceStub(channel)
            response = stub.replicate(master_to_secondary_pb2.ReplicateRequest(msg=request_msg, id=cur_id))

            if response.ACK:
                print(f'replicated to {port}')
                latch.count_down()

    except grpc._channel._InactiveRpcError:
        # waiting_msg.append(request_msg)
        # waiting_id.append(cur_id)
        # ???

        if heartbeat(port):

            global heartbeats
            global health_status

            heartbeats = 0
            health_status = 0

            replicate_method(request_msg, cur_id, port, latch)


def heartbeat(port, quorum_mode=False):
    global heartbeats
    global health_status
    global quorum_status

    if quorum_mode:
        try:
            with grpc.insecure_channel(port) as channel:
                stub = health_pb2_grpc.HealthStub(channel)
                response = stub.Check(health_pb2.HealthCheckRequest(service=''))
                return True

        except grpc._channel._InactiveRpcError:
            return False

    else:
        time.sleep(delays[heartbeats])

        while health_status < 3:
            try:
                with grpc.insecure_channel(port) as channel:
                    stub = health_pb2_grpc.HealthStub(channel)
                    response = stub.Check(health_pb2.HealthCheckRequest(service=''))
                    print(f'heartbeat from {port} - {response}')
                    health_status += 1
                    print('number of health statuses received ', health_status)
                    heartbeats -= 1
                    if health_status == 3:
                        break
                    else:
                        heartbeat(port)

            except grpc._channel._InactiveRpcError:
                heartbeats += 1
                print('heartbeat', heartbeats)
                heartbeat(port)

    return True


def save(request):
    global data_dict
    cur_id = 1

    if not data_dict['id']:
        data_dict['id'].append(1)
    else:
        data_dict['id'].append(data_dict.get('id')[-1] + 1)
        cur_id = data_dict.get('id')[-1]

    data_dict['msg'].append(request.msg)
    print('Save new data:', data_dict)

    return request.msg, cur_id


class CountDownLatch(object):
    def __init__(self, count=1):
        self.count = count
        self.lock = threading.Condition()

    def count_down(self):
        self.lock.acquire()
        self.count -= 1
        if self.count <= 0:
            self.lock.notifyAll()
        self.lock.release()

    def a_wait(self):
        self.lock.acquire()
        while self.count > 0:
            self.lock.wait()
        self.lock.release()


def grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Register user service
    user_serve = UserServicer()
    user_pb2_grpc.add_UserServiceServicer_to_server(user_serve, server)

    logging.info('GRPC running')
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logging.debug('GRPC stop')
        server.stop(0)


if __name__ == '__main__':
    grpc_server()

