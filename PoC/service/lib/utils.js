const grpc = require('grpc');
const protoLoader = require('@grpc/proto-loader');


function getProtoDefinition(filePath) {
  //ProtoBuf definition
  const PROTO_PATH = filePath || __dirname + '/service.proto';
  // Suggested options for similarity to existing grpc.load behavior
  const packageDefinition = protoLoader.loadSync(
    PROTO_PATH,
    {
      keepCase: true,
      longs: String,
      enums: String,
      defaults: true,
      oneofs: true
    });
  const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);
  // The protoDescriptor object has the full package hierarchy
  const service = protoDescriptor.snet.service;

  return service;
}

module.exports.getProtoDefinition = getProtoDefinition;