const Web3 = require('web3');
const { abi } = require('./abi.json');
const dotenv = require('dotenv');

dotenv.config();

const web3 = new Web3(new Web3.providers.HttpProvider(process.env.NODE_URL));
const contractAddress = '0xA51894664A773981C6C112C43ce576f315d5b1B6';
const contract = new web3.eth.Contract(abi, contractAddress);

const withdraw = async (amount) => {
  const accounts = await web3.eth.getAccounts();
  const data = contract.methods.unwrap(amount).encodeABI();
  
  const tx = {
    from: accounts[0],
    to: contractAddress,
    gas: 2000000,
    data: data,
  };

  const signedTx = await web3.eth.accounts.signTransaction(tx, process.env.PRIVATE_KEY);
  return web3.eth.sendSignedTransaction(signedTx.rawTransaction)
    .on('receipt', console.log)
    .on('error', console.error);
};

module.exports = { withdraw };
