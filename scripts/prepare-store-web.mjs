import { cp, mkdir, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const sourceDir = path.join(rootDir, 'frontend');
const targetDir = path.join(rootDir, 'build', 'store-web');

const excludedNames = new Set([
  'Dockerfile',
  'payment-snippets.md',
  'd20eb7b81b91056eb97ceb22171c8952.txt',
  'input.css',
]);

function shouldCopy(source) {
  const name = path.basename(source);
  if (excludedNames.has(name)) return false;
  if (name.endsWith('.log')) return false;
  if (name.endsWith('.err')) return false;
  if (name.endsWith('.err.log')) return false;
  return true;
}

await rm(targetDir, { recursive: true, force: true });
await mkdir(targetDir, { recursive: true });
await cp(sourceDir, targetDir, {
  recursive: true,
  filter: shouldCopy,
});

console.log(`Store web assets prepared at ${path.relative(rootDir, targetDir)}`);
