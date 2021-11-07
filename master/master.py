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
if os.environ.get('https_proxy'):
    del os.environ['https_proxy']
if os.environ.get('http_proxy'):
    del os.environ['http_proxy']


ACK_statuses = []
all_id = []
all_names = []
all_time = []


class UserServicer(user_pb2_grpc.UserServiceServicer):
    def append(self, request, context):

        # save request in-memory
        print('request is', request)
        save(request)

        # parallelism for replication
        Parallel(n_jobs=2, require='sharedmem')(delayed(replicate_method)(port) for port in servers_ports)

        if sum(ACK_statuses) >= request.write_concern - 1:
            return user_pb2.UserPostResponse(success=f'SUCCESS: {request}')
        else:
            delete_last_save()
            return user_pb2.UserPostResponse(success='Sorry, POST method was failed.'
                                                     f'write concern is {request.write_concern},'
                                                     f'number of ACK from secondaries is {sum(ACK_statuses)}')

    def get(self, request, context):
        if request.get:
            print("Process get request...")
            return user_pb2.UserGetResponse(id=all_id,
                                                name=all_names,
                                                time=all_time)


# def ACK2client(request):
#     while True:
#         if sum(ACK_statuses) >= request.write_concern - 1:
#             return True, user_pb2.UserPostResponse(success=f'SUCCESS: {request}')


def replicate_method(port):
    with grpc.insecure_channel(port) as channel:
        if grpc_server_on(channel):
            print(f'Replication to secondary with port {port}')
            stub = master_to_secondary_pb2_grpc.MasterServiceStub(channel)
            response = stub.replicate(master_to_secondary_pb2.ReplicateRequest(id=all_id[-1:],
                                                                            name=all_names[-1:],
                                                                            time=all_time[-1:]))

            print(f'ACK from port {port}', response.ACK)
            global ACK_statuses
            ACK_statuses.append(response.ACK)
        else:
            print(f'server {port} is dead')
            ACK_statuses.append(False)


def delete_last_save():
    if all_id:
        del all_id[-1]
        del all_names[-1]
        del all_time[-1]


def save(request):
    if not all_id:
        current_id = 1
    else:
        current_id = all_id[-1] + 1

    now = datetime.now()
    current_user_time = now.strftime("%d/%m/%Y %H:%M:%S")

    all_id.append(current_id)
    all_names.append(request.name)
    all_time.append(current_user_time)
    print('Save new data:', all_id, all_names, all_time)

    return all_id, all_names, all_time


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
