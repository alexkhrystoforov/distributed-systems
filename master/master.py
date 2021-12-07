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
# servers_ports = ["localhost:50052", "localhost:50053"] # for local run
servers_ports = ["node1:50052", "node2:50053"]  # for docker run
servers_health = {servers_ports[0]: False, servers_ports[1]: False}

quorum = math.ceil(len(servers_ports) + 1 // 2)
quorum_status = False
delay_time = [math.exp(x) for x in range(10)]


class UserServicer(user_pb2_grpc.UserServiceServicer):
    def append(self, request, context):

        if not quorum_check():
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


def quorum_check():
    if sum(servers_health.values()) >= quorum-1:
        return True
    else:
        return False


def single_heartbeat(port, server_health_history, i=0):
    try:
        with grpc.insecure_channel(port) as channel:
            stub = health_pb2_grpc.HealthStub(channel)
            response = stub.Check(health_pb2.HealthCheckRequest(service=''))

            server_health_history.append(True)
            servers_health.update({port: True})

            # check if 3 last single heartbeats were successful => server_health - alive
            if sum(server_health_history[-3:]) == 3:
                return True

            # only 0.5 second sleep if received single heartbeat just now
            time.sleep(delay_time[0]//2)
            single_heartbeat(port, server_health_history)

    except grpc._channel._InactiveRpcError:
        print(f'after attempt №{i} server {port} - NOT AVAILABLE')
        server_health_history.append(False)
        servers_health.update({port: False})
        return False


def heartbeat(port):
    server_health_history = []
    i = 0
    while True:
        time.sleep(3)
        if single_heartbeat(port, server_health_history, i):
            print(f'received 3 heartbeats from {port} => AVAILABLE')
        else:
            i += 1


def replicate_method(request_msg, cur_id, port, latch):
    if servers_health.get(port):
        with grpc.insecure_channel(port) as channel:
            print(f'Start replication to secondary with port {port} \n')
            stub = master_to_secondary_pb2_grpc.MasterServiceStub(channel)
            response = stub.replicate(master_to_secondary_pb2.ReplicateRequest(msg=request_msg, id=cur_id))
            print(f'replicated to {port}, response ', response)
            latch.count_down()
    else:
        time.sleep(3)
        replicate_method(request_msg, cur_id, port, latch)


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
            self.lock.notify_all()
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

    # run hearbeats in a threads
    for port in servers_ports:
        t = threading.Thread(target=heartbeat, args=[port])
        t.start()

    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logging.debug('GRPC stop')
        server.stop(0)


if __name__ == '__main__':
    grpc_server()