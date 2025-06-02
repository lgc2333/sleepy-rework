<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import { DeviceOS, DeviceType, OnlineStatus } from '../types'
import type { DeviceInfo } from '../types'

const { info } = defineProps<{ info: DeviceInfo }>()

const deviceIcon = computed(() => {
  if (info.device_type) {
    switch (info.device_type) {
      case DeviceType.PC:
        return 'bi:pc-display'
      case DeviceType.LAPTOP:
        return 'carbon:laptop'
      case DeviceType.PHONE:
        return 'carbon:mobile'
      case DeviceType.TABLET:
        return 'carbon:tablet'
      case DeviceType.SMARTWATCH:
        return 'carbon:watch'
    }
  }
  return 'carbon:application'
})

const osIcon = computed(() => {
  if (info.device_os) {
    switch (info.device_os) {
      case DeviceOS.WINDOWS:
        return 'mage:microsoft-windows'
      case DeviceOS.MACOS:
      case DeviceOS.IOS:
        return 'mage:apple'
      case DeviceOS.ANDROID:
        return 'cib:android'
    }
    if (info.device_os.endsWith('Linux')) {
      return 'cib:linux'
    }
  }
  return 'icon-park-solid:coordinate-system'
})

const statusName = computed(() => {
  switch (info.status) {
    case OnlineStatus.ONLINE:
      return '在线'
    case OnlineStatus.IDLE:
      return '闲置'
    case OnlineStatus.OFFLINE:
      return '离线'
  }
  return '未知'
})

function formatUpdate(timestamp: number) {
  const now = Date.now()
  const diff = now - timestamp
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (minutes < 1) return `${Math.floor(diff / 1000)}秒`
  if (minutes < 60) return `${minutes}分钟`
  if (hours < 24) return `${hours}小时`
  return `${days}天`
}

function getLastUpdate() {
  return info.last_update_time ? formatUpdate(info.last_update_time) : null
}
function getAppOpenedTime() {
  return info.data?.current_app?.last_change_time
    ? formatUpdate(info.data.current_app.last_change_time)
    : null
}

const lastUpdate = ref(getLastUpdate())
const appOpenedTime = ref(getAppOpenedTime())

const updateTimer = ref<number | null>(null)

onMounted(() => {
  setInterval(() => {
    lastUpdate.value = getLastUpdate()
    appOpenedTime.value = getAppOpenedTime()
  }, 1000)
})

onBeforeUnmount(() => {
  if (updateTimer.value !== null) clearInterval(updateTimer.value)
})
</script>

<template>
  <div
    card
    rounded-md
    overflow="hidden"
    flex="~"
    transition="all duration-300"
    min-w="200px"
  >
    <div :indicator="info.status" w-1 transition-all duration-500></div>
    <div flex="~ 1 col justify-center">
      <div mx="2" my="1px">
        <div flex="~ items-center" my="1">
          <Icon :icon="deviceIcon" text="2xl" mr="2" />

          <div flex="~ col 1">
            <div flex="~ items-center wrap" gap-x-1>
              <div font-bold flex-1 text-lg>{{ info.name }}</div>
              <span flex="~ items-center gap-1" text-light text-sm>
                <div w-2 h-2 rounded-full :indicator="info.status"></div>
                {{ statusName }}
              </span>
            </div>

            <div v-if="info.description" text-sm>{{ info.description }}</div>
          </div>
        </div>

        <div my="1" text-sm>
          <div v-if="info.data?.current_app">
            <template v-if="info.online">
              当前应用：{{ info.data.current_app.name
              }}{{ appOpenedTime && `（已驻前台${appOpenedTime}）` }}
            </template>
            <template v-else>离线前应用：{{ info.data.current_app.name }}</template>
          </div>

          <template
            v-if="
              info.data?.additional_statuses && info.data?.additional_statuses.length
            "
          >
            <div v-for="(status, index) in info.data.additional_statuses" :key="index">
              {{ status }}
            </div>
          </template>
        </div>

        <div flex="~ items-center justify-end gap-2" text-light text-sm my="1">
          <div
            v-if="info.device_os !== DeviceOS.UNKNOWN"
            flex="~ items-center gap-1"
            title="操作系统"
          >
            <Icon :icon="osIcon" />
            <span>{{ info.device_os }}</span>
          </div>

          <div v-if="info.online" flex="~ items-center gap-1">
            <Icon icon="carbon:connection-signal" />
            <span>{{ info.long_connection ? '长连接' : '轮询' }}</span>
          </div>

          <div v-if="lastUpdate" flex="~ items-center gap-1" title="最后更新时间">
            <Icon icon="carbon:time" />
            <span>{{ lastUpdate }}前</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
