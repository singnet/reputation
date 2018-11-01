const grpc = require('grpc');
const { getProtoDefinition } = require('./lib/utils');
const { fetchEscrowData, recoverSignature }    = require('./lib/repository');

const protobuf = getProtoDefinition(__dirname + '/service.proto');

/**
 * Implements the Submit RPC method.
 */
function Submit(call, callback) {
  //TODO do here all the stuff before returning the response
  const { job_address, rating, signature } = call.request;
  const jobAddress = job_address;

  fetchEscrowData(jobAddress)
    .then(output => {
      let success = false;

      const message = jobAddress + rating;
      const signer  = recoverSignature(message, signature);
      if (signer === output.consumer) {
        success = true;
      }

      return success;
    })
    .then(success => {
      if (!success)
        callback('Signature do not match', null);

      callback(null, { success: true, message: "Thank you! Added " + jobAddress });
    })
    .catch(error => callback(error, null))

}

/**
 * Starts an RPC server that receives requests for the service at the
 * sample server port
 */
function main() {
  const server = new grpc.Server();
  server.addService(protobuf.Rating.service, { Submit: Submit });
  server.bind('0.0.0.0:50051', grpc.ServerCredentials.createInsecure());
  server.start();
}

main();