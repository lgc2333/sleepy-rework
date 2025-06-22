import {
  BatteryOptEnabled,
  OpenOptimizationSettings,
  RequestDisableOptimization,
} from '@saserinn/react-native-battery-optimization-check'
import { useEffect, useRef, useState } from 'react'
import { NativeModules } from 'react-native'
import { ScrollView, View } from 'react-native'
import AndroidOpenSettings from 'react-native-android-open-settings'
import { Appbar, Button, List, Snackbar, Text } from 'react-native-paper'

import { ConfigListItem } from '../components/Config'
import type { ConfigProps } from '../components/Config'
import Switch from '../components/Switch'
import TextInput from '../components/TextInput'
import { httpUrlValidator } from '../utils/common'

export const title = '设置'

export default function Home() {
  const [snackVisible, setSnackVisible] = useState(false)
  const [snackBarText, setSnackBarText] = useState('')
  const snackBarTimeout = useRef<number | null>(null)

  const openSnackbar = (text: string) => {
    setSnackBarText(text)
    setSnackVisible(true)
    if (snackBarTimeout.current) clearTimeout(snackBarTimeout.current)
    snackBarTimeout.current = setTimeout(() => {
      setSnackVisible(false)
    }, Snackbar.DURATION_MEDIUM)
  }
  const onSetFailed: ConfigProps<any>['onSetFailed'] = (e, k) => {
    openSnackbar(
      `更新配置 "${k}" 失败！\n${e instanceof Error ? e.message : String(e)}`,
    )
  }

  const [batteryOptEnabled, setBatteryOptEnabled] = useState(false)
  useEffect(() => {
    BatteryOptEnabled().then(setBatteryOptEnabled)
  }, [batteryOptEnabled])
  const toggleBatteryOpt = async () => {
    const nowEnabled = await BatteryOptEnabled()
    setBatteryOptEnabled(nowEnabled)
    if (nowEnabled) {
      RequestDisableOptimization()
    } else {
      OpenOptimizationSettings()
    }
  }

  const openAutoStartSettings = async () => {
    try {
      await NativeModules.AutoStart.addAutoStartup()
    } catch (e: any) {
      if (e.code === 'UNSUPPORTED_MANUFACTURER') {
        openSnackbar(`当前设备没有开机自启权限设置界面`)
      } else {
        openSnackbar(
          `打开获取权限界面失败：\n${e instanceof Error ? e.message : String(e)}`,
        )
      }
    }
  }

  return (
    <>
      <Appbar.Header elevated>
        <Appbar.Content title={title} />
      </Appbar.Header>
      <View style={{ flex: 1 }}>
        <ScrollView>
          <List.Section title="服务设置">
            <ConfigListItem
              configKey="serverEnableConnect"
              title="启用连接"
              description="是否启用与服务端的连接"
              left={(props) => <List.Icon {...props} icon="power" />}
              right={({ style, value, updateValue, disabled }) => (
                <Switch
                  style={style}
                  value={value}
                  disabled={disabled}
                  switchOnIcon="check"
                  switchOffIcon="close"
                  onPress={() => updateValue(!value)}
                />
              )}
              onPress={({ value, updateValue }) => updateValue(!value)}
              onSetFailed={onSetFailed}
            />
            <ConfigListItem
              configKey="serverUrl"
              title="服务端地址"
              description={({ props, value, updateValue, disabled }) => (
                <View>
                  <Text {...props} style={{ marginBottom: 8 }}>
                    设置连接的服务端地址
                  </Text>
                  <TextInput
                    value={value}
                    disabled={disabled}
                    onValueSubmit={(text) => updateValue(text)}
                    valueValidator={httpUrlValidator}
                  />
                </View>
              )}
              left={(props) => <List.Icon {...props} icon="server" />}
              onSetFailed={onSetFailed}
            />
            <ConfigListItem
              configKey="serverSecret"
              title="服务端密钥"
              description={({ props, value, updateValue, disabled }) => (
                <View>
                  <Text {...props} style={{ marginBottom: 8 }}>
                    设置连接服务端所需的密钥
                  </Text>
                  <TextInput
                    value={value}
                    disabled={disabled}
                    onValueSubmit={(text) => updateValue(text)}
                  />
                </View>
              )}
              left={(props) => <List.Icon {...props} icon="key" />}
              onSetFailed={onSetFailed}
            />
          </List.Section>
          <List.Section title="应用设置">
            <List.Item
              title="无障碍权限"
              description="使应用能够获取前台应用信息"
              left={(props) => <List.Icon {...props} icon="information" />}
              right={(props) => (
                <Button
                  {...props}
                  mode="outlined"
                  onPress={AndroidOpenSettings.accessibilitySettings}
                >
                  设置
                </Button>
              )}
              onPress={AndroidOpenSettings.accessibilitySettings}
            />
            <List.Item
              title="忽略电池优化"
              description="允许应用更不受限地持续在后台运行"
              left={(props) => <List.Icon {...props} icon="battery-plus" />}
              right={(props) => (
                <Button
                  {...props}
                  mode={batteryOptEnabled ? 'contained' : 'outlined'}
                  onPress={toggleBatteryOpt}
                >
                  {batteryOptEnabled ? '忽略' : '设置'}
                </Button>
              )}
              onPress={toggleBatteryOpt}
            />
            <List.Item
              title="开机自启"
              description="允许应用开机运行"
              left={(props) => <List.Icon {...props} icon="run" />}
              right={(props) => (
                <Button {...props} mode="outlined" onPress={openAutoStartSettings}>
                  设置
                </Button>
              )}
              onPress={openAutoStartSettings}
            />
          </List.Section>
          <List.Section title="设备设置">
            <ConfigListItem
              configKey="deviceKey"
              title="设备 ID"
              description={({ props, value, updateValue, disabled }) => (
                <View>
                  <Text {...props} style={{ marginBottom: 8 }}>
                    此设备的唯一标识名称
                  </Text>
                  <TextInput
                    value={value}
                    disabled={disabled}
                    onValueSubmit={(text) => updateValue(text)}
                  />
                </View>
              )}
              left={(props) => <List.Icon {...props} icon="tag" />}
              onSetFailed={onSetFailed}
            />
          </List.Section>
        </ScrollView>

        <Snackbar
          visible={snackVisible}
          onDismiss={() => setSnackVisible(false)}
          action={{
            label: '知道了',
            onPress: () => setSnackVisible(false),
          }}
          duration={Number.POSITIVE_INFINITY}
        >
          {snackBarText}
        </Snackbar>
      </View>
    </>
  )
}
