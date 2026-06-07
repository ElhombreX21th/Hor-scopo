import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const npx = process.platform === 'win32' ? 'npx.cmd' : 'npx';

const result = spawnSync(npx, ['cap', 'sync'], {
  cwd: rootDir,
  stdio: 'inherit',
  shell: process.platform === 'win32',
  env: {
    ...process.env,
    CAPACITOR_WEB_DIR: 'build/store-web',
  },
});

if (result.error) {
  console.error(result.error.message);
}

process.exit(result.status ?? 1);
