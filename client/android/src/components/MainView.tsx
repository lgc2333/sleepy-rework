import type { ReactNode } from 'react'
import { StyleSheet, View } from 'react-native'

const styleSheet = StyleSheet.create({
  mainView: {
    padding: 16,
    gap: 16,
  },
})

export namespace MainView {
  export interface Props {
    children?: ReactNode
    [k: string]: any
  }
}

export default function MainView({ children, style, ...props }: MainView.Props) {
  return (
    <View style={[styleSheet.mainView, style]} {...props}>
      {children}
    </View>
  )
}
