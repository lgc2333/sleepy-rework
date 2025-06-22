import { copyFileSync, readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'

import type { ConfigPlugin } from '@expo/config-plugins'
import c from '@expo/config-plugins'

// prettier-ignore
const srcPathComp = ['app', 'src', 'main', 'java', 'top', 'lgc2333', 'sleepy_rework', 'client', 'android']
const appBuildGradleComp = ['app', 'build.gradle']

const modifiedTip = `// File modified by project's custom pre-build plugin\n`
const modifyVersionTip = `// Modify version 1\n`

const keyStoreProperties = `
def reactNativeArchitectures() {
    def value = project.getProperties().get("reactNativeArchitectures")
    return value ? value.split(",") : ["armeabi-v7a", "x86", "x86_64", "arm64-v8a"]
}
def keystoreProperties = new Properties()
def keystorePropertiesFile = file('../../assets/release.keystore.properties')
keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
`
const signingConfigRelease = `
        release {
            storeFile file('../../assets/release.keystore')
            storePassword keystoreProperties.getProperty('storePassword')
            keyAlias keystoreProperties.getProperty('keyAlias')
            keyPassword keystoreProperties.getProperty('keyPassword')
        }
`
const splitsConfig = `
    splits {
        abi {
            reset()
            enable true
            universalApk true
            include (*reactNativeArchitectures())
        }
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
      let appBuildGradle = readFileSync(appBuildGradlePath, 'utf-8')

      if (!appBuildGradle.includes(modifiedTip)) {
        copyFileSync(appBuildGradlePath, `${appBuildGradlePath}.bak`)
        appBuildGradle =
          modifiedTip +
          modifyVersionTip +
          appBuildGradle
            .replace(
              /^(android \{[\s\S]+?)(^\})/m,
              `${keyStoreProperties}$1${splitsConfig}$2`,
            )
            .replace(/(release \{[\s\S]+?signingConfigs\.)debug/, '$1release')
            .replace(
              /(signingConfigs \{[\s\S]+?)(^ {4}\})/m,
              `$1${signingConfigRelease}$2`,
            )
        writeFileSync(appBuildGradlePath, appBuildGradle, 'utf-8')
      } else if (!appBuildGradle.includes(modifyVersionTip)) {
        console.error(
          'Pre-build plugin updated, app/build.gradle leave untouched!!' +
            'Please restore this file, then re-run pre-build.',
        )
      }

      return config
    },
  ])
  return config
}

export default preBuildPlugin
