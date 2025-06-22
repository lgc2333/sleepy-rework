import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'

import type { ConfigPlugin } from '@expo/config-plugins'
import c from '@expo/config-plugins'

const preBuildAssetsPath = path.join(import.meta.dirname, '..', 'assets', 'pre-build')

// prettier-ignore
const srcPathComp = ['app', 'src', 'main', 'java', 'top', 'lgc2333', 'sleepy_rework', 'client', 'android']
const resPathComp = ['app', 'src', 'main', 'res']

const modifiedTip = `// File modified by project's custom pre-build plugin\n`
const modifyVersionTip = `// Modify version 1\n`

const keyStoreProperties = `
def reactNativeArchitectures() {
    def value = project.getProperties().get("reactNativeArchitectures")
    return value ? value.split(",") : ["armeabi-v7a", "x86", "x86_64", "arm64-v8a"]
}
def keystoreProperties = new Properties()
def keystorePropertiesFile = file('../../assets/keystore/keystore.properties')
keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
`
const signingConfigRelease = `
        release {
            storeFile file('../../assets/keystore/release.keystore')
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
  // auto boot
  // <receiver
  //   android:name=".BootReceiver"
  //   android:enabled="true"
  //   android:exported="true"
  // >
  //   <intent-filter>
  //     <action android:name="android.intent.action.BOOT_COMPLETED" />
  //     <action android:name="android.intent.action.QUICKBOOT_POWERON" />
  //   </intent-filter>
  // </receiver>
  config = c.withAndroidManifest(config, async (config) => {
    const androidManifest = config.modResults.manifest
    const receiver = (androidManifest.application![0].receiver ??= []).filter(
      (r) => r.$['android:name'] !== '.BootReceiver',
    )
    androidManifest.application![0].receiver = receiver
    receiver.push({
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

  // accessibility service
  // <service
  //   android:name="com.zareanmasoud.rnaccessibilityservice.MyAccessibilityService"
  //   android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE"
  //   android:label="@string/accessibility_service_label"
  // >
  //   <intent-filter>
  //     <action android:name="android.accessibilityservice.AccessibilityService" />
  //   </intent-filter>
  //   <meta-data
  //     android:name="android.accessibilityservice"
  //     android:resource="@xml/accessibility_service_config"
  //   />
  // </service>
  config = c.withAndroidManifest(config, async (config) => {
    const androidManifest = config.modResults.manifest
    const service = (androidManifest.application![0].service ??= []).filter(
      (s) =>
        s.$['android:name'] !==
        'com.zareanmasoud.rnaccessibilityservice.MyAccessibilityService',
    )
    androidManifest.application![0].service = service
    service.push({
      $: {
        'android:name':
          'com.zareanmasoud.rnaccessibilityservice.MyAccessibilityService',
        'android:permission': 'android.permission.BIND_ACCESSIBILITY_SERVICE',
        'android:enabled': 'true',
        'android:exported': 'false',
        // @ts-ignore
        'android:label': '@string/accessibility_service_label',
      },
      'intent-filter': [
        {
          action: [
            // prettier-ignore
            { $: { 'android:name': 'android.accessibilityservice.AccessibilityService' } },
          ],
        },
      ],
      // @ts-ignore
      'meta-data': [
        {
          $: {
            'android:name': 'android.accessibilityservice',
            'android:resource': '@xml/accessibility_service',
          },
        },
      ],
    })
    return config
  })

  // <string name="accessibility_service_label">Sleepy Rework Android Client</string>
  // <string name="accessibility_service_description">...</string>
  config = c.withStringsXml(config, async (config) => {
    const stringsXml = config.modResults
    const string = (stringsXml.resources.string ??= []).filter(
      (s) =>
        s.$.name !== 'accessibility_service_label' &&
        s.$.name !== 'accessibility_service_description',
    )
    stringsXml.resources.string = string
    string.push(
      {
        $: { name: 'accessibility_service_label' },
        _: 'Sleepy Rework Android Client',
      },
      {
        $: { name: 'accessibility_service_description' },
        _: '启用此服务以使应用能获取前台应用信息',
      },
    )
    return config
  })

  config = c.withAppBuildGradle(config, (config) => {
    const { contents, path } = config.modResults
    if (!contents.includes(modifiedTip)) {
      copyFileSync(path, `${path}.bak`)
      config.modResults.contents =
        modifiedTip +
        modifyVersionTip +
        contents
          .replace(
            /^(android \{[\s\S]+?)(^\})/m,
            `${keyStoreProperties}$1${splitsConfig}$2`,
          )
          .replace(/(release \{[\s\S]+?signingConfigs\.)debug/, '$1release')
          .replace(
            /(signingConfigs \{[\s\S]+?)(^ {4}\})/m,
            `$1${signingConfigRelease}$2`,
          )
    } else if (!contents.includes(modifyVersionTip)) {
      console.error(
        'Pre-build plugin updated, app/build.gradle leave untouched!!' +
          'Please restore this file, then re-run pre-build.',
      )
    }
    return config
  })

  config = c.withDangerousMod(config, [
    'android',
    (config) => {
      const { platformProjectRoot } = config.modRequest

      // copy BootReceiver.kt
      const srcPath = path.join(platformProjectRoot, ...srcPathComp)
      copyFileSync(
        path.join(preBuildAssetsPath, 'BootReceiver.kt'),
        path.join(srcPath, 'BootReceiver.kt'),
      )

      // copy some xmls
      const xmlFolder = path.join(platformProjectRoot, ...resPathComp, 'xml')
      mkdirSync(xmlFolder, { recursive: true })
      copyFileSync(
        path.join(preBuildAssetsPath, 'accessibility_service.xml'),
        path.join(xmlFolder, 'accessibility_service.xml'),
      )

      return config
    },
  ])
  return config
}

export default preBuildPlugin
