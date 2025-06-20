import { useState } from 'react'
import { ScrollView, View } from 'react-native'
import { Appbar, List, Snackbar } from 'react-native-paper'

import { ConfigListItem } from '../components/Config'
import Switch from '../components/Switch'

export const title = '设置'

export default function Home() {
  const [snackVisible, setSnackVisible] = useState(false)
  const [lastErrorText, setLastErrorText] = useState('')

  const onSetFailed = (e: unknown, k: string) => {
    setLastErrorText(
      `更新配置 "${k}" 失败！\n${e instanceof Error ? e.message : String(e)}`,
    )
    setSnackVisible(true)
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
          </List.Section>
        </ScrollView>

        <Snackbar
          visible={snackVisible}
          onDismiss={() => setSnackVisible(false)}
          action={{
            label: '知道了',
            onPress: () => setSnackVisible(false),
          }}
        >
          {lastErrorText}
        </Snackbar>
      </View>
    </>
  )
}
