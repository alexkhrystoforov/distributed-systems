FROM python

COPY protobuf/ /client_app/protobuf/
COPY requirements.txt /client_app/requirements.txt
COPY . .

WORKDIR .

RUN python -m pip install --upgrade pip
RUN python -m pip install -r /client_app/requirements.txt
RUN python -m grpc_tools.protoc -I protobuf --python_out=. --grpc_python_out=. protobuf/user.proto


EXPOSE 50055
#ENTRYPOINT [ "python", "client.py", "--host=0.0.0.0"]
CMD [ "python", "client.py"]
