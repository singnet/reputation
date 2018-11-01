const fs          = require('fs');
const path        = require("path");

const SnetEscrow  = require('../../adapter/snet/escrow');
const proto       = fs.readFileSync(path.resolve(__dirname + '../../../adapter/snet/escrow/adapter.snet.escrow.proto'));
const Web3        = require('web3');
const web3        = new Web3();

async function fetchEscrowData(jobAddress) {
  const adapter     = new SnetEscrow({ proto: proto, network: "kovan" });
  let output
  try {
    output      =  await adapter.process({ job_address: jobAddress });
  } catch (e) {
    throw e;
  }

  return output;
}

function recoverSignature(message, signature) {
  return web3.eth.accounts.recover(message, signature);
}


module.exports = {
  fetchEscrowData,
  recoverSignature
}