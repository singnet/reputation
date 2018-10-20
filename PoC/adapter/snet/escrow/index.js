const Adapter = require('../../index');
const fs      = require('fs');

const Web3      = require('web3');
const JobAbi    = require('singularitynet-platform-contracts/abi/Job.json');
const AgentAbi  = require('singularitynet-platform-contracts/abi/Agent.json');


class SnetEscrow extends Adapter {
  constructor(props) {
    super(props);

    if (!this.validateNetwork(props.network))
      throw "Missing network"
    this.network  = props.network;
    this.web3     = new Web3(new Web3.providers.HttpProvider(`https://${props.network}.infura.io`));

    this.STATE = {
      "PENDING"   : 0,
      "FUNDED"    : 1,
      "COMPLETED" : 2
    };

    this.FULL_SCAN_OPTIONS = {
      fromBlock: 0,
      toBlock: 'latest'
    };
  }

  validateNetwork(network) {
    if (network === 'kovan' || network === 'mainnet' || network === 'rinkeby' || network === 'ropsten') {
      return true;
    } else {
      return false;
    }
  }

  async getTxHashByEvent(contract, eventName) {
    //We assume only one event exists, if present, so the take the 0 element
    const events = (await contract.getPastEvents(eventName, this.FULL_SCAN_OPTIONS));
    const event  = Array.isArray(events) && events.length > 0 && events[0];
    const block  = event && event.blockNumber && await this.web3.eth.getBlock(event.blockNumber);
    
    const timestamp = block && block.timestamp;
    
    const result    = timestamp ? [event.transactionHash, timestamp] : [undefined, undefined];

    return result;
  }

  async process(Input) {
    const jobAddress = Input.job_address;

    if (!jobAddress) 
      throw "Missing jobAddress";
    
      const JobContract = new this.web3.eth.Contract(JobAbi, jobAddress)
      const jobState    = await JobContract.methods.state().call();
      
    if (Number(jobState) !== this.STATE.COMPLETED)
      throw "Job not finished yet";
      
    const value         = await JobContract.methods.jobPrice().call(),
          consumer      = await JobContract.methods.consumer().call(),
          agentAddress  = await JobContract.methods.agent().call(),
          AgentContract = new this.web3.eth.Contract(AgentAbi, agentAddress),
          ownerAddress  = await AgentContract.methods.owner().call();

    const [depositReference, depositTimestamp]  = await this.getTxHashByEvent(JobContract, 'JobFunded');
    const [withdrawReference, withdrawTimestamp]  = await this.getTxHashByEvent(JobContract, 'JobCompleted');

    const Output =  {
      value,
      consumer,
      agent: agentAddress,
      owner: ownerAddress,
      state: Object.keys(this.STATE)[jobState],
      deposit: {
        hash: depositReference,
        timestamp: depositTimestamp
      },
      withdraw: {
        hash: withdrawReference,
        timestamp: withdrawTimestamp
      }
    };

    return Output;
  }
} 

module.exports = SnetEscrow;