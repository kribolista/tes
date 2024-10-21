const fs = require('fs');
const schedule = require('node-schedule');
const { deposit } = require('./deposit');
const { withdraw } = require('./withdraw');

// Function to load configuration
const loadConfig = () => {
  return JSON.parse(fs.readFileSync('./config.json'));
};

// Schedule job for daily execution at 07:10 WIB
schedule.scheduleJob('10 7 * * *', async () => {
  const config = loadConfig();
  for (let i = 0; i < config.iterations; i++) {
    const wrapAmount = getRandomAmount(config.amount.wrap.min, config.amount.wrap.max);
    await deposit(wrapAmount, config.gwei);
    await withdraw(config.amount.unwrap.max); // Assuming you want to unwrap the max balance
  }
});

// Function to generate random amount
const getRandomAmount = (min, max) => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};
