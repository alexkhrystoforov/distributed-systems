import grpc
import user_pb2, user_pb2_grpc
import argparse


def post_method(msg, w):
    with grpc.insecure_channel("0.0.0.0:50051") as channel:
        if grpc_server_on(channel):
            stub = user_pb2_grpc.UserServiceStub(channel)
            response = stub.append(user_pb2.UserPostRequest(msg=msg, write_concern=w))
            print('response is', response.success)
            channel.close()
        else:
            print('master server is not available')


def get_method(server_port):
    with grpc.insecure_channel('0.0.0.0:'+server_port) as channel:
        if grpc_server_on(channel):
            stub = user_pb2_grpc.UserServiceStub(channel)
            response = stub.get(user_pb2.UserGetRequest(get=True))
            print('response is:', response)
        else:
            print('0.0.0.0:'+server_port, 'is not available')


def grpc_server_on(channel) -> bool:
    TIMEOUT_SEC = 1
    try:
        grpc.channel_ready_future(channel).result(timeout=TIMEOUT_SEC)
        return True
    except grpc.FutureTimeoutError:
        return False


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='client')
    parser.add_argument('--get', help='call get method', required=False)
    parser.add_argument('--post', help='call post method', required=False)
    parser.add_argument('--w', help='your write concern', required=False)
    parser.add_argument('--msg', help='your msg', required=False)
    parser.add_argument('--port', help='server port', required=False)

    args = parser.parse_args()

    if args.get:
        get_method(args.port)
    elif args.post:
        post_method(args.msg, int(args.w))
    else:
        print('nothing')