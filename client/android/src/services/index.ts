import AccessibilityService from '@zareanmasoud/react-native-accessibility-service'
import { NativeEventEmitter } from 'react-native'
import BackgroundService from 'react-native-background-actions'

export async function accessibilityTask() {
  let eventEmitterListener = null as ReturnType<
    typeof NativeEventEmitter.prototype.addListener
  > | null

  const eventListener = (e: string) => {
    console.log('event', e)
  }

  const eventEmitter = new NativeEventEmitter(AccessibilityService)
  eventEmitterListener = eventEmitter.addListener('EventReminder', eventListener)

  for (; BackgroundService.isRunning(); ) {
    await new Promise<void>((resolve) => {
      setTimeout(() => resolve(), 1)
    })
  }
}

BackgroundService.start(accessibilityTask, {
  taskName: 'accessibility-task',
  taskTitle: 'Sleepy Rework',
  taskDesc: '信息收集服务运行中',
  taskIcon: {
    name: 'ic_launcher',
    type: 'mipmap',
  },
})
