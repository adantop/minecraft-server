const { Client } = require('discord.js');
const { botIntents, prefix, commands } = require('./config/config');
const config = require('./config/default');


const client = new Client({
  intents: botIntents,
  partials: ['CHANNEL', 'MESSAGE'],
});

client.on('ready', () => {
  console.log('Logged in as ' + client.user.tag);
});


client.on('messageCreate', async (msg) => {
  if (msg.author.bot) return;
  if (!msg.content.startsWith(prefix)) return;

  const [cmd, ...args] = msg.content.slice(prefix.length).split(" ");

  if (commands.hasOwnProperty(cmd)) {
    await msg.reply('Working on it...');
    const res = await commands[cmd](args);
    msg.reply(res);
  } else {
    msg.reply('I do not understand your command');
  }
});

client.login(config.DISCORD_TOKEN);