import user_pb2_grpc as user_pb2_grpc
import user_pb2 as user_pb2
import master_to_secondary_pb2_grpc as master_to_secondary_pb2_grpc
import master_to_secondary_pb2 as master_to_secondary_pb2

from concurrent import futures
import threading
import time
import grpc
import logging


_ONE_DAY_IN_SECONDS = 60 * 60 * 24

all_msg = []
all_id = []
server_down = False
servers_ports = ["localhost:50052", "localhost:50053"]


class UserServicer(user_pb2_grpc.UserServiceServicer):
    def append(self, request, context):

        if request.write_concern > len(servers_ports)+1:
            return user_pb2.UserPostResponse(success='Post request is declined.'
                                                         'write concern is too big,'
                                                         f'the biggest possible w={len(servers_ports)+1}')

        # if server_down and request.write_concern == len(servers_ports) + 1:
        #     return user_pb2.UserPostResponse(success='Post request is declined.'
        #                                              'something wrong with servers')

        save(request)
        latch = CountDownLatch(request.write_concern - 1)

        for port in servers_ports:
            t = threading.Thread(target=replicate_method, args=[request.msg, port, latch])
            t.start()

        latch.a_wait()

        return user_pb2.UserPostResponse(success=f'SUCCESS: {request}')

    def get(self, request, context):
        if request.get:
            print("Process get request...")
            return user_pb2.UserGetResponse(msg=all_msg)


def replicate_method(request_msg, port, latch):
    global all_id
    global server_down

    with grpc.insecure_channel(port) as channel:
        if grpc_server_on(channel):
            print(f'Start replication to secondary with port {port}')
            stub = master_to_secondary_pb2_grpc.MasterServiceStub(channel)
            response = stub.replicate(master_to_secondary_pb2.ReplicateRequest(msg=request_msg, id=all_id[-1]))
            if response.ACK:
                print(f'replicated to {port}')
                latch.count_down()
        # else:
        #     print(f'server with port {port} is not available')
        #     latch.count_down()
        #     server_down = True


def save(request):
    global all_id
    global all_msg

    all_msg.append(request.msg)
    if not all_id:
        all_id.append(1)
    else:
        all_id.append(all_id[-1] + 1)
    print('Save new data:', all_msg, all_id)


def grpc_server_on(channel) -> bool:
    TIMEOUT_SEC = 1
    try:
        grpc.channel_ready_future(channel).result(timeout=TIMEOUT_SEC)
        return True
    except grpc.FutureTimeoutError:
        return False


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
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))

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
