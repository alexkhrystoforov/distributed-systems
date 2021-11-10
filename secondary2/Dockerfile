FROM python

COPY protobuf/ /secondary2/protobuf/
COPY requirements.txt /secondary2/requirements.txt
COPY . .

WORKDIR .

RUN python -m pip install --upgrade pip
RUN python -m pip install -r /secondary2/requirements.txt
RUN python -m grpc_tools.protoc -I protobuf --python_out=. --grpc_python_out=. protobuf/master_to_secondary.proto
RUN python -m grpc_tools.protoc -I protobuf --python_out=. --grpc_python_out=. protobuf/user.proto


EXPOSE 50053
#ENTRYPOINT [ "python", "secondary2.py" ]
ENTRYPOINT [ "python", "secondary2.py" , "--host", "127.0.0.1", "--port", "50053"]
