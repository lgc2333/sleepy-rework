import { useMaterial3Theme } from '@pchmn/expo-material3-theme'
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
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const styles = StyleSheet.create({
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
  const insets = useSafeAreaInsets()
  const viewStyle = useMemo(
    () => ({
      marginTop: insets.top,
      marginBottom: insets.bottom,
      marginLeft: insets.left + 16,
      marginRight: insets.right + 16,
    }),
    [insets],
  )
  return (
    <SafeAreaView style={{ flex: 1 }}>
      <StatusBar style="auto" />
      <ScrollView style={viewStyle}>
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
