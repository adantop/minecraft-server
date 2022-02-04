const { Intents } = require('discord.js');
const { serverCommand } = require('../commands');

const {
  DIRECT_MESSAGES,
  GUILD_MESSAGES,
  GUILDS,
} = Intents.FLAGS;

const botIntents = [
  DIRECT_MESSAGES,
  GUILD_MESSAGES,
  GUILDS,
];


const prefix = '/';


const commands = {
  'server': serverCommand,
};

console.log(commands);

module.exports = { botIntents, prefix, commands };