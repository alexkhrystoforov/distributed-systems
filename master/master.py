import user_pb2_grpc as user_pb2_grpc
import user_pb2 as user_pb2

import master_to_secondary_pb2_grpc as master_to_secondary_pb2_grpc
import master_to_secondary_pb2 as master_to_secondary_pb2

from concurrent import futures
import time
from datetime import datetime
import grpc
import logging
_ONE_DAY_IN_SECONDS = 60 * 60 * 24


all_id = []
all_names = []
all_time = []

servers_ports = ["127.0.0.1:50052", "127.0.0.1:50053"]


class UserServicer(user_pb2_grpc.UserServiceServicer):
    def append(self, request, context):

        # save request in-memory
        print('request is', request)
        save(request)

        # check ACK statuses from each server
        ACK_statuses = []

        for port in servers_ports:
            ACK_statuses.append(replicate_method(port))
            print(f'ACK from port {port}', ACK_statuses[-1])

        if all(ACK_statuses):
            return user_pb2.UserPostResponse(success=f'SUCCESS: {request}')
        else:
            delete_last_save()
            return user_pb2.UserPostResponse(success='Sorry, POST method was failed')

    def get(self, request, context):
        if request.get:
            print("Process get request...")
            return user_pb2.UserGetResponse(id=all_id,
                                                name=all_names,
                                                time=all_time)


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


def replicate_method(sec_server_port):
    # with grpc.insecure_channel(sec_server_port, options=(('grpc.enable_http_proxy', 0),)) as channel:
    with grpc.insecure_channel(sec_server_port) as channel:
        print(f'Replication to secondary with port {sec_server_port}')
        stub = master_to_secondary_pb2_grpc.MasterServiceStub(channel)
        response = stub.replicate(master_to_secondary_pb2.ReplicateRequest(id=all_id[-1:],
                                                                        name=all_names[-1:],
                                                                        time=all_time[-1:]))
        channel.close()
        ACK_status = response.ACK

    return ACK_status


def grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))

    # Register user service
    user_serve = UserServicer()
    user_pb2_grpc.add_UserServiceServicer_to_server(user_serve, server)

    logging.info('GRPC running')
    server.add_insecure_port(f'[::]:50051')
    # server.add_insecure_port('localhost:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logging.debug('GRPC stop')
        server.stop(0)


if __name__ == '__main__':
    grpc_server()
