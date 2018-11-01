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

    let deposit = {}, withdraw = {};
    
    const pastFundingEvents = await JobContract.getPastEvents('JobFunded', this.FULL_SCAN_OPTIONS);
    if (Array.isArray(pastFundingEvents) && pastFundingEvents.length > 0) {
      const event             = pastFundingEvents[0];
      const fundingReference  = event.transactionHash;
      const fundingBlock      = event.blockNumber;
      deposit = { ...deposit, hash: fundingReference, block: fundingBlock };
      
      const pastCompletedEvents = await JobContract.getPastEvents('JobCompleted', { fromBlock: fundingBlock - 1 , toBlock: 'latest' });
      if (Array.isArray(pastCompletedEvents) && pastCompletedEvents.length > 0) {
        const completedReference  = pastCompletedEvents[0].transactionHash;
        const completedBlock      = pastCompletedEvents[0].blockNumber;
        withdraw = { ...withdraw, hash: completedReference, block: completedBlock };
      }
    }

    //const [depositReference, depositTimestamp]  = await this.getTxHashByEvent(JobContract, 'JobFunded');
    //const [withdrawReference, withdrawTimestamp]  = await this.getTxHashByEvent(JobContract, 'JobCompleted');

    const Output =  {
      value,
      consumer,
      agent: agentAddress,
      owner: ownerAddress,
      state: Object.keys(this.STATE)[jobState],
      deposit,
      withdraw
    };

    return Output;
  }
} 

module.exports = SnetEscrow;