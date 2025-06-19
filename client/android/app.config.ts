// sort-imports-ignore
import 'ts-node/register'

import type { ConfigContext, ExpoConfig } from 'expo/config'

export default function createConfig(_: ConfigContext) {
  return {
    name: 'Sleepy Rework Android Client',
    slug: 'sleepy-rework-client-android',
    version: '0.1.0',
    platforms: ['android'],
    orientation: 'portrait',
    icon: './assets/icon.png',
    userInterfaceStyle: 'automatic',
    newArchEnabled: true,
    splash: {
      image: './assets/splash-icon.png',
      resizeMode: 'contain',
      backgroundColor: '#ffffff',
    },
    android: {
      package: 'top.lgc2333.sleepy_rework.client.android',
      versionCode: 1,
      permissions: [
        'android.permission.INTERNET',
        // foreground
        'android.permission.FOREGROUND_SERVICE',
        'android.permission.FOREGROUND_SERVICE_DATA_SYNC',
        'android.permission.WAKE_LOCK',
        // auto start
        'android.permission.RECEIVE_BOOT_COMPLETED',
      ],
      adaptiveIcon: {
        foregroundImage: './assets/adaptive-icon.png',
        backgroundColor: '#ffffff',
      },
      edgeToEdgeEnabled: true,
    },
    plugins: ['./plugins/prebuild.plugin.ts'],
  } satisfies Partial<ExpoConfig>
}
