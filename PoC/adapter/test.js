const fs          = require('fs');

const SnetEscrow  = require('./snet/escrow');
const proto       = fs.readFileSync('./snet/escrow/adapter.snet.escrow.proto');

const adapter       = new SnetEscrow({ proto: proto, network: "kovan" });
const InputBuffer   = adapter.encode('Input', { job_address: '0x988C8e2bc509b92960a79d4C92e6f139eEc165A4' });
const Input         = adapter.decode('Input', InputBuffer);
adapter.process(Input)
  .then(Output => {
    const OutputBuffer  = adapter.encode('Output', Output);
    const Out           = adapter.decode('Output', OutputBuffer);
    console.log(Out);
  })
  .catch(console.error)
