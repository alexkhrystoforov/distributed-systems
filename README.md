# distributed-systems

#### Master server:

POST method - appends a message into the in-memory list (only after get ACK from each Secondary) 

GET method - returns all messages from the in-memory list



#### Secondaries:

GET method - returns all replicated messages from the in-memory list

Master-Secondary communication - gRPC.
