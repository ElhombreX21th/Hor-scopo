import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const errors = [];

const requiredTextChecks = [
  ['capacitor.config.ts', "appId: 'br.blog.seufuturo'"],
  ['capacitor.config.ts', "appName: 'SeuFuturo'"],
  ['capacitor.config.ts', "process.env.CAPACITOR_WEB_DIR || 'frontend'"],
  ['package.json', 'scripts/prepare-store-web.mjs'],
  ['frontend/index.html', "PUBLIC_APP_URL = 'https://seufuturo.blog.br'"],
  ['frontend/index.html', 'isStoreBuild'],
  ['frontend/index.html', 'activePlanos'],
  ['frontend/index.html', "document.body.dataset.distribution = 'store'"],
  ['frontend/index.html', "if (!isStoreBuild && 'serviceWorker' in navigator)"],
  ['frontend/index.html', 'styles/tailwind.css'],
  ['frontend/service-worker.js', '/styles/tailwind.css'],
  ['vercel.json', 'frontend/styles/$1'],
  ['android/app/build.gradle', 'applicationId "br.blog.seufuturo"'],
  ['android/app/build.gradle', "rootProject.file('key.properties')"],
  ['android/app/src/main/AndroidManifest.xml', 'android:screenOrientation="portrait"'],
  ['ios/App/App/Info.plist', '<string>UIInterfaceOrientationPortrait</string>'],
];

const requiredFiles = [
  'package-lock.json',
  'frontend/styles/input.css',
  'frontend/styles/tailwind.css',
  'android/app/src/main/AndroidManifest.xml',
  'android/key.properties.example',
  'ios/App/App.xcodeproj/project.pbxproj',
  'store/app-store/build-and-submit.md',
  'store/google-play/build-and-submit.md',
  'store/privacy/data-safety-and-app-privacy.md',
  'scripts/prepare-store-web.mjs',
  'scripts/cap-sync-store.mjs',
  'scripts/build-android-bundle.ps1',
];

const expectedPngs = [
  ['store/assets/app-icon-1024.png', 1024, 1024],
  ['store/assets/google-play-icon-512.png', 512, 512],
  ['store/assets/feature-graphic-1024x500.png', 1024, 500],
  ['store/screenshots/app-store/ios-01-app-1290x2796.png', 1290, 2796],
  ['store/screenshots/app-store/ios-02-app-1290x2796.png', 1290, 2796],
  ['store/screenshots/app-store/ios-03-app-1290x2796.png', 1290, 2796],
  ['store/screenshots/app-store/ios-04-app-1290x2796.png', 1290, 2796],
  ['store/screenshots/app-store/ios-05-privacidade-1290x2796.png', 1290, 2796],
  ['store/screenshots/google-play/android-01-app-1080x1920.png', 1080, 1920],
  ['store/screenshots/google-play/android-02-app-1080x1920.png', 1080, 1920],
  ['store/screenshots/google-play/android-03-app-1080x1920.png', 1080, 1920],
  ['store/screenshots/google-play/android-04-app-1080x1920.png', 1080, 1920],
  ['store/screenshots/google-play/android-05-privacidade-1080x1920.png', 1080, 1920],
];

const ignoredDirs = new Set([
  '.git',
  '.pytest_cache',
  '__pycache__',
  '.vercel',
  'node_modules',
  'build',
  'dist',
  '.gradle',
  'Pods',
  'DerivedData',
]);

function file(pathname) {
  return path.join(rootDir, pathname);
}

function fail(message) {
  errors.push(message);
}

function readText(pathname) {
  const fullPath = file(pathname);
  if (!existsSync(fullPath)) return '';
  return readFileSync(fullPath, 'utf8');
}

function pngDimensions(pathname) {
  const fullPath = file(pathname);
  if (!existsSync(fullPath)) return null;
  const buffer = readFileSync(fullPath);
  const pngSignature = '89504e470d0a1a0a';
  if (buffer.subarray(0, 8).toString('hex') !== pngSignature) return null;
  return {
    width: buffer.readUInt32BE(16),
    height: buffer.readUInt32BE(20),
  };
}

function walk(dir, visit) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (ignoredDirs.has(entry.name)) continue;
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(fullPath, visit);
      continue;
    }
    visit(fullPath);
  }
}

for (const pathname of requiredFiles) {
  if (!existsSync(file(pathname))) {
    fail(`Arquivo obrigatorio ausente: ${pathname}`);
  }
}

for (const [pathname, expected] of requiredTextChecks) {
  const text = readText(pathname);
  if (!text.includes(expected)) {
    fail(`Texto esperado nao encontrado em ${pathname}: ${expected}`);
  }
}

if (readText('frontend/index.html').includes('cdn.tailwindcss.com')) {
  fail('frontend/index.html ainda usa Tailwind CDN.');
}

if (readText('ios/App/App/Info.plist').includes('Landscape')) {
  fail('Info.plist ainda permite orientacao landscape.');
}

const storeWebDir = file('build/store-web');
if (existsSync(storeWebDir)) {
  const forbiddenStoreAssets = [];
  walk(storeWebDir, (fullPath) => {
    const name = path.basename(fullPath);
    if (
      name === 'Dockerfile' ||
      name === 'payment-snippets.md' ||
      name.endsWith('.log') ||
      name.endsWith('.err.log')
    ) {
      forbiddenStoreAssets.push(path.relative(rootDir, fullPath));
    }
  });
  if (forbiddenStoreAssets.length) {
    fail(`Arquivos internos encontrados no build store-web: ${forbiddenStoreAssets.join(', ')}`);
  }
}

for (const [pathname, width, height] of expectedPngs) {
  const dimensions = pngDimensions(pathname);
  if (!dimensions) {
    fail(`PNG invalido ou ausente: ${pathname}`);
    continue;
  }
  if (dimensions.width !== width || dimensions.height !== height) {
    fail(`${pathname} deveria ter ${width}x${height}, mas tem ${dimensions.width}x${dimensions.height}.`);
  }
}

const oldDomainHits = [];
const oldDomain = ['hypersecit', 'com', 'br'].join('.');
walk(rootDir, (fullPath) => {
  if (statSync(fullPath).size > 2_000_000) return;
  const ext = path.extname(fullPath).toLowerCase();
  if (['.png', '.jpg', '.jpeg', '.ico', '.db', '.zip', '.aab', '.apk', '.pyc'].includes(ext)) return;
  const text = readFileSync(fullPath, 'utf8');
  if (text.includes(oldDomain)) {
    oldDomainHits.push(path.relative(rootDir, fullPath));
  }
});

if (oldDomainHits.length) {
  fail(`Dominio antigo encontrado em: ${oldDomainHits.join(', ')}`);
}

if (errors.length) {
  console.error('Store readiness: falhou');
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exit(1);
}

console.log('Store readiness: OK');
console.log(`Verificados ${requiredFiles.length} arquivos, ${requiredTextChecks.length} contratos e ${expectedPngs.length} imagens.`);
