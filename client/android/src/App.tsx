import {
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  View,
  useColorScheme,
} from 'react-native'

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
})

export default function App() {
  const isDarkMode = useColorScheme() === 'dark'

  return (
    <View style={styles.container}>
      <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />
      <ScrollView>
        <Text>Some Sample Text</Text>
      </ScrollView>
    </View>
  )
}
