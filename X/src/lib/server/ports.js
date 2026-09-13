import net from 'node:net';

export function portAvailable(port, host = '0.0.0.0') {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.unref();
    server.once('error', () => resolve(false));
    server.listen({ port, host, exclusive: true }, () => server.close(() => resolve(true)));
  });
}

export async function allocatePort(config, preferred = 3000, exceptId = '') {
  const reserved = new Set((config.apps || []).filter((app) => app.id !== exceptId).map((app) => Number(app.port)));
  let port = Math.max(1024, Math.min(65535, Number(preferred) || 3000));
  for (let checked = 0; checked < 64512; checked += 1) {
    if (!reserved.has(port) && await portAvailable(port)) return port;
    port = port === 65535 ? 1024 : port + 1;
  }
  throw new Error('No free TCP port is available on the Home Assistant host.');
}
