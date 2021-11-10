import master_to_secondary_pb2_grpc as master_to_secondary_pb2_grpc
import master_to_secondary_pb2 as master_to_secondary_pb2

import user_pb2_grpc as user_pb2_grpc
import user_pb2 as user_pb2


from concurrent import futures
import time
import grpc
import logging
_ONE_DAY_IN_SECONDS = 60 * 60 * 24


all_msg = []


class UserServicer(user_pb2_grpc.UserServiceServicer):

    def get(self, request, context):
        if request.get:
            print("Process get request...")
            return user_pb2.UserGetResponse(msg=all_msg)


class MasterServicer(master_to_secondary_pb2_grpc.MasterServiceServicer):
    def replicate(self, request, context):
        # time.sleep(60)
        all_msg.append(request.msg)
        print('replication was succeed: ')
        print(all_msg)

        return master_to_secondary_pb2.ReplicateResponse(ACK=True)

    def deletelastmsg(self, request, context):
        del all_msg[-1]
        print('last msg was deleted')
        return master_to_secondary_pb2.DeleteLastMsgResponse(delete=True)

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