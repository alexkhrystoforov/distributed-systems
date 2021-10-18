FROM python

COPY protobuf/ /secondary/protobuf/
COPY requirements.txt /secondary/requirements.txt
COPY . .

WORKDIR .

RUN python -m pip install --upgrade pip
RUN python -m pip install -r /secondary/requirements.txt
RUN python -m grpc_tools.protoc -I protobuf --python_out=. --grpc_python_out=. protobuf/master_to_secondary.proto
RUN python -m grpc_tools.protoc -I protobuf --python_out=. --grpc_python_out=. protobuf/user.proto


EXPOSE 50052
ENTRYPOINT [ "python", "secondary1.py" ]
