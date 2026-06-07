import type { CapacitorConfig } from '@capacitor/cli';

const webDir = process.env.CAPACITOR_WEB_DIR || 'frontend';

const config: CapacitorConfig = {
  appId: 'br.blog.seufuturo',
  appName: 'SeuFuturo',
  webDir,
  bundledWebRuntime: false,
  server: {
    androidScheme: 'https',
    iosScheme: 'capacitor'
  },
  plugins: {
    SplashScreen: {
      launchAutoHide: true,
      backgroundColor: '#1a0e2e'
    }
  },
  ios: {
    contentInset: 'automatic'
  }
};

export default config;
