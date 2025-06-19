import { useMaterial3Theme } from '@pchmn/expo-material3-theme'
import Constants from 'expo-constants'
import { StatusBar } from 'expo-status-bar'
import { useMemo } from 'react'
import { SafeAreaView, ScrollView, StyleSheet, View } from 'react-native'
import { useColorScheme } from 'react-native'
import {
  Button,
  MD3DarkTheme,
  MD3LightTheme,
  PaperProvider,
  Text,
} from 'react-native-paper'

const styles = StyleSheet.create({
  rootContainer: {
    flex: 1,
    marginTop: Constants.statusBarHeight + 8,
    marginHorizontal: 16,
  },
  mainContainer: {
    gap: 8,
  },
})

export function MainView() {
  return (
    <View style={styles.mainContainer}>
      <Text>Open up App.tsx to start working on your app!</Text>
      <Button mode="contained">Some Text</Button>
    </View>
  )
}

export function AppMain() {
  return (
    <SafeAreaView style={styles.rootContainer}>
      <StatusBar style="auto" />
      <ScrollView>
        <MainView />
      </ScrollView>
    </SafeAreaView>
  )
}

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
  return (
    <PaperProvider theme={paperTheme}>
      <AppMain />
    </PaperProvider>
  )
}
