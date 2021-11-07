import user_pb2_grpc as user_pb2_grpc
import user_pb2 as user_pb2

import master_to_secondary_pb2_grpc as master_to_secondary_pb2_grpc
import master_to_secondary_pb2 as master_to_secondary_pb2

from concurrent import futures
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import threading

import time
from datetime import datetime
import grpc
import logging

from joblib import Parallel, delayed
import multiprocessing
import os

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

ACK_counter = []
all_msg = []


class UserServicer(user_pb2_grpc.UserServiceServicer):
    def append(self, request, context):
        global ACK_counter
        save(request)
        #Parallel(n_jobs=2, require='sharedmem')(delayed(replicate_method)(port) for port in servers_ports)

        t2 = threading.Thread(target=replicate_method, args=[request.msg, servers_ports[0]])
        t3 = threading.Thread(target=replicate_method, args=[request.msg,servers_ports[1]])
        t2.start()
        t3.start()

        while True:
            if sum(ACK_counter) >= request.write_concern - 1:
                print('START ACK TO CLIENT')
                return user_pb2.UserPostResponse(success=f'SUCCESS: {request}')
        # else:
        #     delete_last_save()
        #     return user_pb2.UserPostResponse(success='Sorry, POST method was failed.'
        #                                              f'write concern is {request.write_concern},'
        #                                              f'number of ACK from secondaries is {sum(ACK_counter)}')

    def get(self, request, context):
        if request.get:
            print("Process get request...")
            return user_pb2.UserGetResponse(msg=all_msg)


def replicate_method(request_msg,port):

    with grpc.insecure_channel(port) as channel:
        if grpc_server_on(channel):
            print(f'Replication to secondary with port {port}')

            print(f'name for {port}', request_msg)
            stub = master_to_secondary_pb2_grpc.MasterServiceStub(channel)
            response = stub.replicate(master_to_secondary_pb2.ReplicateRequest(msg=request_msg))

            print(f'ACK from port {port}', response.ACK)
            global ACK_counter
            ACK_counter.append(response.ACK)
        else:
            print(f'server {port} is dead')
            ACK_counter.append(False)


def delete_last_save():
    if all_msg:
        del all_msg[-1]


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
