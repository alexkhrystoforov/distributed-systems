import grpc
import user_pb2, user_pb2_grpc
import os


if os.environ.get('https_proxy'):
    del os.environ['https_proxy']
if os.environ.get('http_proxy'):
    del os.environ['http_proxy']



def post_method():
    with grpc.insecure_channel(servers_ports[0]) as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)
        name = str(input('enter your name:'))
        w = int(input('write concern:'))
        response = stub.append(user_pb2.UserPostRequest(name=name, write_concern=w))
        print('response is', response.success)
        channel.close()


def get_method(server_port):
    with grpc.insecure_channel(server_port) as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)
        response = stub.get(user_pb2.UserGetRequest(get=True))
        print('response is:', response)


def select_method():
    selected_method = input('Print 1 or 2 or 3.\n'
                            'options: \n'
                            '1 = POST \n'
                            '2 = GET \n'
                            '3 = Stop \n')

    return selected_method


def select_server():
    selected_server = input('server for GET method:\n'
                              '1 = master\n'
                              '2 = secondary1\n'
                              '3 = secondary2\n')

    return selected_server


# 51 - master, 52-53 - secondaries. POST only for master, GET for any
servers_ports = ["localhost:50051", "localhost:50052", "localhost:50053"] # failed connect grpc_status=14
# servers_ports = ["127.0.0.1:50051", "localhost:50052", "localhost:50053"] # failed connect grpc_status=14
# servers_ports = ["172.17.0.2:50051", "localhost:50052", "localhost:50053"] # failed connect grpc_status=14
# servers_ports = [":50051", "localhost:50052", "localhost:50053"] #DNS error
# servers_ports = ['50051']


def run():
    method_key = select_method()

    if method_key == '1':
        post_method(), run()

    elif method_key == '2':
        server_key = select_server()
        if server_key == '1':
            get_method(servers_ports[0]), run()

        elif server_key == '2':
            get_method(servers_ports[1]), run()

        elif server_key == '3':
            get_method(servers_ports[2]), run()

    elif method_key == '3':
        print('STOP client')
    else:
        print('wrong input')


if __name__ == '__main__':
    run()
