# distributed-systems

#### Master server:

POST method - appends a message into the in-memory list (only after get ACK from each Secondary) 

GET method - returns all messages from the in-memory list



#### Secondaries:

GET method - returns all replicated messages from the in-memory list

Master-Secondary communication - gRPC.

## How to run:

### locally
all works perfect, just run master.py , secondary2.py, secondary.py and interact with them via client.py

### docker

inside each folder run the respective commands:

docker build -t secondary2 .
docker run -p 50053:50053 secondary2

docker build -t secondary .
docker run -p 50052:50052 secondary

docker build -t master .
docker run -p 50051:50051 master

docker build -t client .
docker run -ti client


### Problem with ports

if run each server from docker - client cannot connect to master server, however, if secondaries were run from docker and client and master locally - all works fine
