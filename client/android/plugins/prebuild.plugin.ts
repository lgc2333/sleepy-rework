import { copyFileSync, readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'

import type { ConfigPlugin } from '@expo/config-plugins'
import c from '@expo/config-plugins'

// prettier-ignore
const srcPathComp = ['app', 'src', 'main', 'java', 'top', 'lgc2333', 'sleepy_rework', 'client', 'android']
const appBuildGradleComp = ['app', 'build.gradle']

const keyStoreProperties = `
def keystoreProperties = new Properties()
def keystorePropertiesFile = file('../../assets/release.keystore.properties')
keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
`
const signingConfigRelease = `
        release {
            storeFile file('../assets/release.keystore')
            storePassword keystoreProperties.getProperty('storePassword')
            keyAlias keystoreProperties.getProperty('keyAlias')
            keyPassword keystoreProperties.getProperty('keyPassword')
        }
`

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
        path.join(import.meta.dirname, '..', 'assets', 'BootReceiver.kt'),
        path.join(srcPath, 'BootReceiver.kt'),
      )

      const appBuildGradlePath = path.join(platformProjectRoot, ...appBuildGradleComp)
      const appBuildGradle = readFileSync(appBuildGradlePath, 'utf-8')
        .replace(/^(android \{)/m, `${keyStoreProperties}$1`)
        .replace(/(release \{[\s\S]+?signingConfigs\.)debug/, '$1release')
        .replace(/(signingConfigs \{[\s\S]+?)(^ {4}\})/m, `$1${signingConfigRelease}$2`)
      writeFileSync(appBuildGradlePath, appBuildGradle, 'utf-8')

      return config
    },
  ])
  return config
}

export default preBuildPlugin
