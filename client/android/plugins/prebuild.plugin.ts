import { copyFileSync } from 'node:fs'
import path from 'node:path'

import type { ConfigPlugin } from '@expo/config-plugins'
import c from '@expo/config-plugins'

// prettier-ignore
const srcPathComp = ['app', 'src', 'main', 'java', 'top', 'lgc2333', 'sleepy_rework', 'client', 'android']

export const preBuildPlugin: ConfigPlugin = (config) => {
  config = c.withAndroidManifest(config, async (config) => {
    const androidManifest = config.modResults.manifest
    ;(androidManifest.application![0].receiver ??= []).push({
      $: {
        'android:name': '.BootReceiver',
        'android:enabled': 'true',
        'android:exported': 'true',
      },
      'intent-filter': [
        {
          category: [{ $: { 'android:name': 'android.intent.category.DEFAULT' } }],
          action: [
            { $: { 'android:name': 'android.intent.action.BOOT_COMPLETED' } },
            { $: { 'android:name': 'android.intent.action.QUICKBOOT_POWERON' } },
          ],
        },
      ],
    })
    return config
  })
  config = c.withDangerousMod(config, [
    'android',
    (config) => {
      if (config.modRequest.platform !== 'android') return config
      const { platformProjectRoot } = config.modRequest
      const srcPath = path.join(platformProjectRoot, ...srcPathComp)
      copyFileSync(
        path.join(import.meta.dirname, 'BootReceiver.kt'),
        path.join(srcPath, 'BootReceiver.kt'),
      )
      return config
    },
  ])
  return config
}

export default preBuildPlugin
