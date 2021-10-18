FROM python

COPY protobuf/ /master/protobuf/
COPY requirements.txt /master/requirements.txt
COPY . .

WORKDIR .

RUN python -m pip install --upgrade pip
RUN python -m pip install -r /master/requirements.txt
RUN python -m grpc_tools.protoc -I protobuf --python_out=. --grpc_python_out=. protobuf/master_to_secondary.proto
RUN python -m grpc_tools.protoc -I protobuf --python_out=. --grpc_python_out=. protobuf/user.proto


EXPOSE 50051
ENTRYPOINT [ "python", "master.py" ]
