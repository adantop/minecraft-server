/**
 * Responds to any HTTP request.
 *
 * @param {!express:Request} req HTTP request context.
 * @param {!express:Response} res HTTP response context.
 * 
 * {"action": null, "name": "minecraft-server"} | base64
 * {"message": "eyJhY3Rpb24iOiBudWxsLCAibmFtZSI6ICJtaW5lY3JhZnQtc2VydmVyIn0K"}
 *
 * {"action": "start", "name": "minecraft-server"} | base64
 * {"message": "eyJhY3Rpb24iOiAic3RhcnQiLCAibmFtZSI6ICJtaW5lY3JhZnQtc2VydmVyIn0K"}
 *
 * {"action": "stop", "name": "minecraft-server"} | base64
 * {"message": "eyJhY3Rpb24iOiAic3RvcCIsICJuYW1lIjogIm1pbmVjcmFmdC1zZXJ2ZXIifQo="}
 * 
 */
 exports.manageServer = async (req, res, next) => {
  const Compute = require('@google-cloud/compute');
  const compute = new Compute();

  const PROJECT_ID = 'us-central1-c';
  const NO_MESSAGE = 'NO_MESSAGE';
  const INVALID_MESSAGE = 'INVALID_MESSAGE';
  const NO_COMPUTE_CLIENT = 'NO_COMPUTE_CLIENT';
  const INSTANCE_NOT_FOUND = 'INSTANCE_NOT_FOUND';
  const ACTION_START = 'start';
  const ACTION_STOP = 'stop';

  if (!compute) {
    throw new Error(NO_COMPUTE_CLIENT);
  }
  
  const message = req.query.message || req.body.message || NO_MESSAGE;
  if (message === NO_MESSAGE) {
    throw new Error(NO_MESSAGE);
  }

  let payload;
  try {
    payload = JSON.parse(Buffer.from(message, 'base64').toString());
  } catch (err) {
    throw new Error(INVALID_MESSAGE);
  }
  if (!payload.hasOwnProperty("action") || !payload.hasOwnProperty("name")) {
    throw new Error(INVALID_MESSAGE);
  }

  const zone = compute.zone(PROJECT_ID);
  let vm = zone.vm(payload.name);

  if (!vm) {
    throw new Error(INSTANCE_NOT_FOUND);
  }

  let [metadata] = await vm.getMetadata();

  if (payload.action === ACTION_START) {
    await vm.start();
  } else if (payload.action === ACTION_STOP) {
    await vm.stop();
  }

  res.status(200).send({
    name: metadata.name,
    status: metadata.status,
    ip: metadata.networkInterfaces[0].accessConfigs[0].natIP ?? null
  });
};