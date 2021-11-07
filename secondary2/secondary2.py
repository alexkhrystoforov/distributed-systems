import master_to_secondary_pb2_grpc as master_to_secondary_pb2_grpc
import master_to_secondary_pb2 as master_to_secondary_pb2

import user_pb2_grpc as user_pb2_grpc
import user_pb2 as user_pb2


from concurrent import futures
import time
import grpc
import logging
_ONE_DAY_IN_SECONDS = 60 * 60 * 24


all_id = []
all_names = []
all_time = []


class UserServicer(user_pb2_grpc.UserServiceServicer):

    def get(self, request, context):
        if request.get:
            print("Process get request...")
            return user_pb2.UserGetResponse(id=all_id,
                                                name=all_names,
                                                time=all_time)


class MasterServicer(master_to_secondary_pb2_grpc.MasterServiceServicer):
    def replicate(self, request, context):
        # time.sleep(60)
        all_id.append(request.id[0])
        all_names.append(request.name[0])
        all_time.append(request.time[0])
        print('replication was succeed: ')

        print(all_id)
        print(all_names)
        print(all_time)

        return master_to_secondary_pb2.ReplicateResponse(ACK=True)


def grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Register Master service
    master_to_secondary_serve = MasterServicer()
    master_to_secondary_pb2_grpc.add_MasterServiceServicer_to_server(master_to_secondary_serve, server)

    # Register User service
    user_serve = UserServicer()
    user_pb2_grpc.add_UserServiceServicer_to_server(user_serve, server)

    logging.info('GRPC running')
    server.add_insecure_port('[::]:50053')
    server.start()
    print('server 50053 is started')
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logging.debug('GRPC stop')
        server.stop(0)


if __name__ == '__main__':
    grpc_server()