import master_to_secondary_pb2_grpc as master_to_secondary_pb2_grpc
import master_to_secondary_pb2 as master_to_secondary_pb2
import user_pb2_grpc as user_pb2_grpc
import user_pb2 as user_pb2
import health_pb2_grpc as health_pb2_grpc
import health_pb2 as health_pb2

from concurrent import futures
import time
import argparse
import grpc
import logging
import sys

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

data_dict = {'id': [], 'msg': []}
delay = 0

ipaddress = sys.argv[1]
host = sys.argv[2]


class UserServicer(user_pb2_grpc.UserServiceServicer):
    def get(self, request, context):
        print("Process get request...")

        last_ordered_msg = 0
        w = [x + 1 for x in range(len(data_dict.get('id')))]
        for x, y in zip(data_dict.get('id'), w):
            if x - y == 0:
                last_ordered_msg = x
            else:
                break

        return user_pb2.UserGetResponse(msg=data_dict.get('msg')[:last_ordered_msg])


class MasterServicer(master_to_secondary_pb2_grpc.MasterServiceServicer):
    def replicate(self, request, context):
        global delay
        global data_dict

        time.sleep(delay)
        if request.id not in data_dict['id']:
            data_dict['msg'].append(request.msg)
            data_dict['id'].append(request.id)

        else:
            return master_to_secondary_pb2.ReplicateResponse(ACK=True)

        # right order
        new_msg = [x for _, x in sorted(zip(data_dict.get('id'), data_dict.get('msg')))]

        data_dict.update({'id': sorted(data_dict.get('id')), 'msg': new_msg})

        print('replication was succeed: ')
        print('data: ', data_dict)

        return master_to_secondary_pb2.ReplicateResponse(ACK=True)


class HealthServicer(health_pb2_grpc.HealthServicer):
    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(status='alive')


def grpc_server(port=ipaddress+':'+host):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Register Health service
    health_serve = HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_serve, server)

    # Register Master service
    master_to_secondary_serve = MasterServicer()
    master_to_secondary_pb2_grpc.add_MasterServiceServicer_to_server(master_to_secondary_serve, server)

    # Register User service
    user_serve = UserServicer()
    user_pb2_grpc.add_UserServiceServicer_to_server(user_serve, server)

    logging.info('GRPC running')
    server.add_insecure_port(f'{port}')
    server.start()
    print(f'server {port} is started')

    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logging.debug('GRPC stop')
        server.stop(0)


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='client')
    # parser.add_argument('--port', help='server port')
    # parser.add_argument('--sleep', help='call post method', required=False)
    # args = parser.parse_args()
    # if args.sleep:
    #     delay = int(args.sleep)
    #
    # grpc_server('localhost:'+args.port)
    grpc_server()


