# Public service

This is the front-facing layer that exposes to clients as `gRPC` methods a set of APIs to interact with Reputation agency via Protocol Buffers over HTTP/2

They can be a set of request/response and/or stream socket connection.

# Services

* **Rating**


# Endpoints

* **Submit**
  * RatingRequest 
    * job_address
    * rating
    * signature
  * RatingReply
    * success
    * message


# Example

```js
  const protoLoader = require('@grpc/proto-loader');
  const packageDefinition = protoLoader.loadSync(PROTO_PATH);
  const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);

  
  
  const client = new protoDescriptor.snet.service.Rating('localhost:50051', grpc.credentials.createInsecure());

  client.Submit({
    job_address: "0x123...", 
    rating: 5, 
    signature: "0x01"
  }, console.log)
```