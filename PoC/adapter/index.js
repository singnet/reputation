const protobuf = require('protocol-buffers');

class Adapter {

  constructor({ proto }) {
    try { 
      this.messages = protobuf(proto) 
    } catch (e) {
      throw e 
    };
  }

  decode(MessageType, InputBuffer) {
    return this.messages[MessageType].decode(InputBuffer);
  } 

  encode(MessageType, Output) {
    return this.messages[MessageType].encode(Output);
  } 
  
}

module.exports = Adapter;