import {
  DeviceInfoFromClient,
  DeviceInfoFromClientWS,
  WebSocketClient,
} from 'sleepy-rework-types'

import { WebSocket } from './websocket'

const baseUrl = 'http://192.168.1.111:29306'
const secret = 'sleepy'
const deviceKey = 'sample_device'

const detectActivitiesDelay = 1000

let initialState: DeviceInfoFromClientWS = {
  name: '饼干 - OnePlus 8T',
  description: 'Snapdragon 865, 256G + 12G',
  device_type: 'phone',
  device_os: 'Nameless 15',
  remove_when_offline: false,
  idle: false,
  data: {},
  replace: true,
}

const client = new WebSocketClient(
  baseUrl.replace(/^http/, 'ws'),
  '/api/v1/device/{device_key}/info',
  {
    secret,
    path: { device_key: deviceKey },
    webSocketFactory: (url, secret) => new WebSocket(url, ['sleepy', secret ?? '']),
  },
)

client.addEventListener('error', (ev) => {
  console.error('WebSocket error:', ev.detail.event)
})
client.addEventListener('close', (ev) => {
  console.log(
    'WebSocket connection closed',
    ev.detail.event.code,
    ev.detail.event.reason,
  )
})
client.addEventListener('parseError', (ev) => {
  console.error('WebSocket parse error:', ev.detail.error)
})

client.addEventListener('open', () => {
  console.info('WebSocket connection opened')
  client.send(initialState)
})

type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

function deepUpdate(target: Record<any, any>, source: Record<any, any>): any {
  const updated: any = { ...target }
  for (const [k, v] of Object.entries(source)) {
    if (typeof v === 'object' && typeof target[k] === 'object') {
      target[k] = deepUpdate(target[k], v)
    } else {
      target[k] = v
    }
  }
  return updated
}

const detector = new (class ActivityDetector {
  protected $lastApp: string | null = null
  protected $lastBattery: number | null = null
  protected $lastBatteryCharging: boolean | null = null
  protected $lastIdle: boolean | null = null

  protected $detectAppChange(): DeepPartial<DeviceInfoFromClient> | null {
    const currApp = currentPackage()
    if (currApp === this.$lastApp) return null
    this.$lastApp = currApp
    return {
      data: {
        current_app: {
          name: app.getAppName(currApp),
          last_change_time: Date.now(),
        },
      },
    }
  }

  protected $detectBatteryChange(): DeepPartial<DeviceInfoFromClient> | null {
    const currBattery = device.getBattery()
    const currCharging = device.isCharging()
    if (
      currBattery === this.$lastBattery &&
      currCharging === this.$lastBatteryCharging
    ) {
      return null
    }
    this.$lastBattery = currBattery
    this.$lastBatteryCharging = currCharging
    return {
      data: {
        battery: { percent: currBattery, charging: currCharging },
      },
    }
  }

  protected $detectIdleChange(): DeepPartial<DeviceInfoFromClient> | null {
    const currIdle = !device.isScreenOn()
    if (currIdle === this.$lastIdle) return null
    this.$lastIdle = currIdle
    return { idle: currIdle }
  }

  run() {
    let changes: DeepPartial<DeviceInfoFromClient> | null = null

    const appChange = this.$detectAppChange()
    if (appChange) changes = deepUpdate(changes ?? {}, appChange)

    const batteryChange = this.$detectBatteryChange()
    if (batteryChange) changes = deepUpdate(changes ?? {}, batteryChange)

    const idleChange = this.$detectIdleChange()
    if (idleChange) changes = deepUpdate(changes ?? {}, idleChange)

    if (changes) {
      initialState = deepUpdate(initialState, changes)
      if (client.connected) client.send(changes)
    }
  }
})()

auto.waitFor()

setInterval(() => detector.run(), detectActivitiesDelay)
detector.run()

client.start()

events.on('exit', () => {
  client.stop()
})
