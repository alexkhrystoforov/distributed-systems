import master_to_secondary_pb2_grpc as master_to_secondary_pb2_grpc
import master_to_secondary_pb2 as master_to_secondary_pb2
import user_pb2_grpc as user_pb2_grpc
import user_pb2 as user_pb2

from concurrent import futures
import time
import argparse
import grpc
import logging

import sys, os
_ONE_DAY_IN_SECONDS = 60 * 60 * 24

all_msg = []
all_id = []
delay = 0


class UserServicer(user_pb2_grpc.UserServiceServicer):
    def get(self, request, context):
        last_ordered_msg = 0
        print("Process get request...")

        if len(all_id) == 1 and all_id[0] == 1:
            return user_pb2.UserGetResponse(msg=all_msg)

        #  find priority list python

        elif len(all_id) > 2:
            for x in all_id:
                if x == all_id[-1] and x - all_id[all_id.index(x) - 1] == 1:
                    last_ordered_msg = x + 1
                elif x - all_id[all_id.index(x) + 1] == -1:
                    last_ordered_msg = x + 1
                else:
                    if x == 1 and x - all_id[all_id.index(x) + 1] != -1:
                        last_ordered_msg = 1
                        break
                    else:
                        break

            return user_pb2.UserGetResponse(msg=all_msg[:last_ordered_msg])

        else:
            return user_pb2.UserGetResponse(msg=[])


class MasterServicer(master_to_secondary_pb2_grpc.MasterServiceServicer):
    def replicate(self, request, context):
        global delay
        global all_msg
        global all_id

        time.sleep(delay)
        all_msg.append(request.msg)
        all_id.append(request.id)

        all_id.sort()
        all_msg = [x for _, x in sorted(zip(all_id, all_msg))]

        print('replication was succeed: ')
        print('all msgs: ', all_msg)
        print('all ids ', all_id)

        return master_to_secondary_pb2.ReplicateResponse(ACK=True)


def grpc_server(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Register Master service
    master_to_secondary_serve = MasterServicer()
    master_to_secondary_pb2_grpc.add_MasterServiceServicer_to_server(master_to_secondary_serve, server)

    # Register User service
    user_serve = UserServicer()
    user_pb2_grpc.add_UserServiceServicer_to_server(user_serve, server)

    logging.info('GRPC running')
    server.add_insecure_port('localhost:'+port)
    server.start()
    print(f'server {port} is started')
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logging.debug('GRPC stop')
        server.stop(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='client')
    parser.add_argument('--port', help='server port')
    parser.add_argument('--sleep', help='call post method', required=False)
    args = parser.parse_args()
    if args.sleep:
        delay = int(args.sleep)

    grpc_server(args.port)


