import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { createReadStream, existsSync } from 'node:fs';
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const frontendDir = path.join(rootDir, 'frontend');
const outputRoot = path.join(rootDir, 'store', 'screenshots');

const mimeTypes = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.js', 'application/javascript; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.png', 'image/png'],
  ['.jpg', 'image/jpeg'],
  ['.jpeg', 'image/jpeg'],
  ['.svg', 'image/svg+xml'],
]);

const browserCandidates = [
  process.env.CHROME_PATH,
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium-browser',
  '/usr/bin/chromium',
].filter(Boolean);

const profiles = [
  {
    name: 'app-store',
    width: 430,
    height: 932,
    deviceScaleFactor: 3,
    files: [
      'ios-01-app-1290x2796.png',
      'ios-02-app-1290x2796.png',
      'ios-03-app-1290x2796.png',
      'ios-04-app-1290x2796.png',
      'ios-05-privacidade-1290x2796.png',
    ],
  },
  {
    name: 'google-play',
    width: 360,
    height: 640,
    deviceScaleFactor: 3,
    files: [
      'android-01-app-1080x1920.png',
      'android-02-app-1080x1920.png',
      'android-03-app-1080x1920.png',
      'android-04-app-1080x1920.png',
      'android-05-privacidade-1080x1920.png',
    ],
  },
];

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function findBrowser() {
  const browser = browserCandidates.find((candidate) => candidate && existsSync(candidate));
  if (!browser) {
    throw new Error('Chrome ou Edge nao encontrado. Defina CHROME_PATH para gerar screenshots.');
  }
  return browser;
}

async function freePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      server.close(() => resolve(port));
    });
  });
}

function startStaticServer() {
  const server = createServer((request, response) => {
    const url = new URL(request.url || '/', 'http://127.0.0.1');
    const requestedPath = url.pathname === '/' ? '/index.html' : url.pathname;
    const decodedPath = decodeURIComponent(requestedPath);
    const filePath = path.resolve(frontendDir, `.${decodedPath}`);

    if (!filePath.startsWith(frontendDir)) {
      response.writeHead(403);
      response.end('Forbidden');
      return;
    }

    if (!existsSync(filePath)) {
      response.writeHead(404);
      response.end('Not found');
      return;
    }

    response.setHeader('Content-Type', mimeTypes.get(path.extname(filePath)) || 'application/octet-stream');
    createReadStream(filePath).pipe(response);
  });

  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      resolve({ server, port: server.address().port });
    });
  });
}

async function waitForJson(url, timeoutMs = 10000) {
  const started = Date.now();
  let lastError;

  while (Date.now() - started < timeoutMs) {
    try {
      const response = await fetch(url);
      if (response.ok) return response.json();
      lastError = new Error(`HTTP ${response.status}`);
    } catch (error) {
      lastError = error;
    }
    await delay(150);
  }

  throw lastError || new Error(`Timeout esperando ${url}`);
}

class CdpClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.nextId = 1;
    this.pending = new Map();
    this.eventWaiters = new Map();
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.socket = new WebSocket(this.wsUrl);
      this.socket.addEventListener('open', resolve, { once: true });
      this.socket.addEventListener('error', reject, { once: true });
      this.socket.addEventListener('message', (event) => this.handleMessage(event));
    });
  }

  handleMessage(event) {
    const message = JSON.parse(event.data);

    if (message.id && this.pending.has(message.id)) {
      const { resolve, reject } = this.pending.get(message.id);
      this.pending.delete(message.id);
      if (message.error) {
        reject(new Error(message.error.message));
      } else {
        resolve(message.result || {});
      }
      return;
    }

    const waiters = this.eventWaiters.get(message.method);
    if (!waiters?.length) return;
    const waiter = waiters.shift();
    clearTimeout(waiter.timer);
    waiter.resolve(message.params || {});
  }

  send(method, params = {}) {
    const id = this.nextId++;
    this.socket.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
    });
  }

  waitFor(method, timeoutMs = 10000) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`Timeout esperando evento ${method}`));
      }, timeoutMs);
      const waiters = this.eventWaiters.get(method) || [];
      waiters.push({ resolve, reject, timer });
      this.eventWaiters.set(method, waiters);
    });
  }

  close() {
    this.socket?.close();
  }
}

async function launchBrowser() {
  const browserPath = findBrowser();
  const debuggingPort = await freePort();
  const userDataDir = await mkdtemp(path.join(os.tmpdir(), 'seufuturo-chrome-'));
  const browser = spawn(browserPath, [
    '--headless=new',
    '--disable-gpu',
    '--hide-scrollbars',
    '--no-first-run',
    '--no-default-browser-check',
    `--remote-debugging-port=${debuggingPort}`,
    `--user-data-dir=${userDataDir}`,
    'about:blank',
  ], { stdio: 'ignore' });

  const version = await waitForJson(`http://127.0.0.1:${debuggingPort}/json/version`);
  const targets = await waitForJson(`http://127.0.0.1:${debuggingPort}/json/list`);
  const pageTarget = targets.find((target) => target.type === 'page') || targets[0];
  const client = new CdpClient(pageTarget.webSocketDebuggerUrl || version.webSocketDebuggerUrl);
  await client.connect();
  await client.send('Page.enable');
  await client.send('Runtime.enable');

  return { browser, client, userDataDir };
}

async function evaluate(client, expression, awaitPromise = false) {
  const result = await client.send('Runtime.evaluate', {
    expression,
    awaitPromise,
    returnByValue: true,
  });

  if (result.exceptionDetails) {
    throw new Error(result.exceptionDetails.text || 'Erro avaliando pagina');
  }

  return result.result?.value;
}

async function navigate(client, url) {
  const loaded = client.waitFor('Page.loadEventFired', 15000).catch(() => undefined);
  await client.send('Page.navigate', { url });
  await loaded;
  await delay(1800);
}

async function setViewport(client, profile) {
  await client.send('Emulation.setDeviceMetricsOverride', {
    width: profile.width,
    height: profile.height,
    deviceScaleFactor: profile.deviceScaleFactor,
    mobile: true,
    screenWidth: profile.width,
    screenHeight: profile.height,
  });
}

async function capture(client, filePath) {
  const { data } = await client.send('Page.captureScreenshot', {
    format: 'png',
    fromSurface: true,
    captureBeyondViewport: false,
  });
  await writeFile(filePath, Buffer.from(data, 'base64'));
}

async function waitForForecast(client) {
  await evaluate(client, `new Promise((resolve) => {
    const ready = () => !document.getElementById('resultadoContent')?.classList.contains('hidden');
    if (ready()) return resolve(true);
    let attempts = 0;
    const timer = setInterval(() => {
      attempts += 1;
      if (ready() || attempts > 30) {
        clearInterval(timer);
        resolve(ready());
      }
    }, 250);
  })`, true);
}

async function generateForProfile(client, baseUrl, profile) {
  const outputDir = path.join(outputRoot, profile.name);
  await mkdir(outputDir, { recursive: true });
  await setViewport(client, profile);

  await navigate(client, `${baseUrl}/index.html?distribution=store`);
  await waitForForecast(client);
  await evaluate(client, `window.scrollTo(0, 0); document.body.dataset.distribution = 'store';`);
  await delay(300);
  await capture(client, path.join(outputDir, profile.files[0]));

  await evaluate(client, `document.getElementById('signosContainer').scrollIntoView({ block: 'start' }); window.scrollBy(0, -24);`);
  await delay(300);
  await capture(client, path.join(outputDir, profile.files[1]));

  await evaluate(client, `document.querySelector('[data-signo="Touro"]')?.click();`);
  await waitForForecast(client);
  await evaluate(client, `document.getElementById('resultadoContainer').scrollIntoView({ block: 'center' });`);
  await delay(500);
  await capture(client, path.join(outputDir, profile.files[2]));

  await evaluate(client, `window.scrollTo(0, 0); document.getElementById('openAuthBtn')?.click();`);
  await delay(500);
  await capture(client, path.join(outputDir, profile.files[3]));

  await navigate(client, `${baseUrl}/privacy.html`);
  await evaluate(client, `window.scrollTo(0, 0);`);
  await delay(300);
  await capture(client, path.join(outputDir, profile.files[4]));

  console.log(`Screenshots ${profile.name}: ${profile.files.join(', ')}`);
}

async function main() {
  const { server, port } = await startStaticServer();
  let browser;
  let client;
  let userDataDir;

  try {
    const launched = await launchBrowser();
    browser = launched.browser;
    client = launched.client;
    userDataDir = launched.userDataDir;

    const baseUrl = `http://127.0.0.1:${port}`;
    for (const profile of profiles) {
      await generateForProfile(client, baseUrl, profile);
    }
  } finally {
    client?.close();
    if (browser) {
      browser.kill();
      await Promise.race([
        new Promise((resolve) => browser.once('exit', resolve)),
        delay(1500),
      ]);
    }
    server.close();
    if (userDataDir) {
      try {
        await rm(userDataDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 250 });
      } catch (error) {
        console.warn(`Aviso: nao foi possivel remover temp do browser: ${error.message}`);
      }
    }
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
