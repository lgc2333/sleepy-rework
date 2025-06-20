import { Appbar, Text } from 'react-native-paper'

import MainView from '../components/MainView'

export const title = '欢迎'

export default function Home() {
  return (
    <>
      <Appbar.Header elevated>
        <Appbar.Content title={title} />
      </Appbar.Header>
      <MainView>
        <Text variant="headlineSmall" style={{ textAlign: 'center' }}>
          欢迎使用{'\n'}Sleepy Rework Android Client
        </Text>
      </MainView>
    </>
  )
}
