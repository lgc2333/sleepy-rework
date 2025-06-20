import { Appbar, Text } from 'react-native-paper'

import MainView from '../components/MainView'

export const title = '设置'

export default function Home() {
  return (
    <>
      <Appbar.Header elevated>
        <Appbar.Content title={title} />
      </Appbar.Header>
      <MainView>
        <Text>Meow</Text>
      </MainView>
    </>
  )
}
