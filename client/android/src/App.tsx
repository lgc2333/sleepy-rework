import { useMaterial3Theme } from '@pchmn/expo-material3-theme'
import { useMemo, useState } from 'react'
import { useColorScheme } from 'react-native'
import {
  BottomNavigation,
  MD3DarkTheme,
  MD3LightTheme,
  PaperProvider,
} from 'react-native-paper'

import Home, { title as homeTitle } from './views/Home'
import Settings, { title as settingsTitle } from './views/Settings'

export default function App() {
  const colorScheme = useColorScheme()
  const { theme } = useMaterial3Theme()
  const paperTheme = useMemo(
    () =>
      colorScheme === 'dark'
        ? { ...MD3DarkTheme, colors: theme.dark }
        : { ...MD3LightTheme, colors: theme.light },
    [colorScheme, theme],
  )

  const [index, setIndex] = useState(0)
  const [routes] = useState([
    {
      key: 'home',
      title: homeTitle,
      focusedIcon: 'home',
      unfocusedIcon: 'home-outline',
    },
    {
      key: 'settings',
      title: settingsTitle,
      focusedIcon: 'cog',
      unfocusedIcon: 'cog-outline',
    },
  ])
  const renderScene = BottomNavigation.SceneMap({
    home: Home,
    settings: Settings,
  })

  return (
    <PaperProvider theme={paperTheme}>
      <BottomNavigation
        navigationState={{ index, routes }}
        onIndexChange={setIndex}
        renderScene={renderScene}
      />
    </PaperProvider>
  )
}
