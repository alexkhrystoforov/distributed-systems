import user_pb2_grpc as user_pb2_grpc
import user_pb2 as user_pb2

import master_to_secondary_pb2_grpc as master_to_secondary_pb2_grpc
import master_to_secondary_pb2 as master_to_secondary_pb2

from concurrent import futures
import threading
import multiprocessing
import time
import os
import grpc
import logging

if os.environ.get('https_proxy'):
 del os.environ['https_proxy']
if os.environ.get('http_proxy'):
 del os.environ['http_proxy']


_ONE_DAY_IN_SECONDS = 60 * 60 * 24

ACK_counter = {}
stop_threads = False
all_msg = []


class UserServicer(user_pb2_grpc.UserServiceServicer):
    def append(self, request, context):
        global ACK_counter

        save(request)

        t2 = threading.Thread(target=replicate_method, args=[request.msg, servers_ports[0], ])
        t3 = threading.Thread(target=replicate_method, args=[request.msg,servers_ports[1], ])

        t2.start()
        t3.start()


        n = 0
        # wait for ACK for 3sec
        while n <= 3:

            if sum(ACK_counter.values()) >= request.write_concern - 1:
                print('START ACK TO CLIENT')
                return user_pb2.UserPostResponse(success=f'SUCCESS: {request}')
            time.sleep(0.5)
            n += 1

        else:
            # stop replication
            # global stop_threads
            # stop_threads = True
            # for t in [t2,t3]:
            #     if t.is_alive():
            #         t.join()

            delete_last_save()
            delete_secondary_last_save()

            return user_pb2.UserPostResponse(success='Sorry, POST method was failed.'
                                                     f'write concern is {request.write_concern},'
                                                     f'number of ACK from secondaries is {sum(ACK_counter.values())}')

    def get(self, request, context):
        if request.get:
            print("Process get request...")
            return user_pb2.UserGetResponse(msg=all_msg)

#
# def stop_thread():
#     global stop_threads
#     stop_threads = True


def replicate_method(request_msg, port):

    with grpc.insecure_channel(port) as channel:

        if grpc_server_on(channel):
            print(f'Replication to secondary with port {port}')
            print(f'name for {port}', request_msg)
            stub = master_to_secondary_pb2_grpc.MasterServiceStub(channel)
            response = stub.replicate(master_to_secondary_pb2.ReplicateRequest(msg=request_msg))
            channel.close()
            print(f'ACK from port {port}', response.ACK)
            global ACK_counter
            ACK_counter[port] = response.ACK

        else:
            print(f'server {port} is dead')
            ACK_counter[port] = False


def delete_last_save():
    if all_msg:
        print('Delete data:', all_msg[-1])
        del all_msg[-1]


def delete_secondary_last_save():
    # get all ports with successful replication
    ports = list(port for port, ACK_status in ACK_counter.items() if ACK_status == True)

    for port in ports:
        with grpc.insecure_channel(port) as channel:
            if grpc_server_on(channel):
                stub = master_to_secondary_pb2_grpc.MasterServiceStub(channel)
                response = stub.deletelastmsg(master_to_secondary_pb2.DeleteLastMsgRequest(delete=True))
                print(f'deleted last replicated msg on secondary with port {port}', response.delete)
                channel.close()


def save(request):
    all_msg.append(request.msg)
    print('Save new data:', all_msg)


def grpc_server_on(channel) -> bool:
    TIMEOUT_SEC = 1
    try:
        grpc.channel_ready_future(channel).result(timeout=TIMEOUT_SEC)
        return True
    except grpc.FutureTimeoutError:
        return False


servers_ports = ["localhost:50052", "localhost:50053"]


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
