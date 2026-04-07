import fs from 'fs';

const STATUS_FILE = '/data/status.json';

export function appendLog(name, message) {
  const msg = `[${new Date().toLocaleTimeString()}] ${message}`;
  const logFile = `/data/${name}.log`;

  // ensure file exists
  if (!fs.existsSync(logFile)) fs.writeFileSync(logFile, '');

  // write to file
  fs.appendFileSync(logFile, msg + '\n');

  // update status.json logs
  if (fs.existsSync(STATUS_FILE)) {
    const data = JSON.parse(fs.readFileSync(STATUS_FILE));

    if (data[name]) {
      data[name].logs = data[name].logs || [];
      data[name].logs.push(msg);

      // keep last 200 lines
      if (data[name].logs.length > 200) {
        data[name].logs = data[name].logs.slice(-200);
      }

      fs.writeFileSync(STATUS_FILE, JSON.stringify(data));
    }
  }

  // optional: HA logs
  console.log(`[${name}] ${message}`);
}