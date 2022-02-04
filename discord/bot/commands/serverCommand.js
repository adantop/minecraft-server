const axios = require('axios');
const config = require('../config/default');


const WAIT_TIME_MS = 15000;


const actionsMap = new Map();
actionsMap.set("status", statusServer);
actionsMap.set("start", startServer);
actionsMap.set("stop", stopServer);


async function serverCommand(args) {
  console.log(`Ran serverCommand with args: ${args}`)
  const [action, ..._] = args;

  if (!actionsMap.has(action)) {
    return `Available actions are ${Array.from(actionsMap.keys())}`;
  }

  let message;
  try {
    message = await actionsMap.get(action)();
  } catch (err) {
    message = `Oops, ${err}`;
  }

  return message;
}


async function statusServer() {
    const res = await axios.post(config.MANAGE_SERVER, config.STATUS_MESSAGE);
    vm = res.data;
    const message = `Server is ${vm.status} and has IP ${vm.ip}`
    return message;
}


async function startServer() {
    let res = await axios.post(config.MANAGE_SERVER, config.START_MESSAGE);
    
    await sleep(WAIT_TIME_MS);
    res = await axios.post(config.MANAGE_SERVER, config.STATUS_MESSAGE);
    const vm = res.data;

    if (!vm.hasOwnProperty("ip") || vm.ip === null) {
        return 'Could not verify if server started, check status after some time';
    }

    return `Server is ${vm.status} and has IP ${vm.ip}`;
}


async function stopServer() {
    let res = await axios.post(config.MANAGE_SERVER, config.STOP_MESSAGE);
    
    await sleep(WAIT_TIME_MS);
    res = await axios.post(config.MANAGE_SERVER, config.STATUS_MESSAGE);
    const vm = res.data;

    if (!vm.hasOwnProperty("ip") || vm.ip !== null) {
        return 'Could not verify if server stopped, check status after some time';
    }

    return `Server is ${vm.status}`;
}

function sleep(ms) {
    return new Promise((resolve) => {
      setTimeout(resolve, ms);
    });
}

module.exports = serverCommand;