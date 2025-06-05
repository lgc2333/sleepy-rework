<script setup lang="ts">
import { Icon } from '@iconify/vue'
import type { DeviceInfo } from 'sleepy-rework-types'
import { computed, onBeforeUnmount, onMounted, onUpdated, ref } from 'vue'

const { info } = defineProps<{ info: DeviceInfo }>()

const deviceIcon = computed(() => {
  switch (info.device_type) {
    case 'pc':
      return 'bi:pc-display'
    case 'laptop':
      return 'carbon:laptop'
    case 'phone':
      return 'carbon:mobile'
    case 'tablet':
      return 'carbon:tablet'
    case 'smartwatch':
      return 'carbon:watch'
    default:
      return 'carbon:application'
  }
})

const debianFishCakeEaster = ref(false)

const osIcon = computed(() => {
  if (debianFishCakeEaster.value) return 'noto:fish-cake-with-swirl'

  if (info.device_os) {
    const os = info.device_os.toLowerCase()

    if (os.startsWith('atlas')) return 'simple-icons:atlasos'
    if (os.startsWith('windows')) return 'mage:microsoft-windows'

    if (os.startsWith('macos') || os.startsWith('ios')) return 'cib:apple'

    if (os.startsWith('debian')) return 'mdi:debian'
    if (os.startsWith('ubuntu')) return 'ri:ubuntu-line'
    if (os.startsWith('kubuntu')) return 'simple-icons:kubuntu'
    if (os.startsWith('fedora')) return 'mdi:fedora'
    if (os.includes('mint')) return 'mdi:linux-mint'
    if (os.startsWith('manjaro')) return 'mdi:manjaro'
    if (os.startsWith('centos')) return 'la:centos'
    if (os.startsWith('gentoo')) return 'mdi:gentoo'
    if (os.startsWith('alma')) return 'simple-icons:almalinux'
    if (os.startsWith('kali')) return 'simple-icons:kalilinux'
    if (os.startsWith('popos')) return 'simple-icons:popos'
    if (os.startsWith('rocky')) return 'simple-icons:rockylinux'
    if (os.startsWith('alpine')) return 'simple-icons:alpinelinux'
    if (os.startsWith('endeavouros')) return 'simple-icons:endeavouros'
    if (os.startsWith('cachyos')) return 'mdi:arch'
    if (os.startsWith('arch')) return 'mdi:arch'
    if (os.startsWith('deepin')) return 'simple-icons:deepin'
    if (os.endsWith('linux')) return 'cib:linux'

    if (os.startsWith('coloros')) return 'simple-icons:oppo'
    if (os.startsWith('hyperos')) return 'simple-icons:xiaomi'
    if (os.startsWith('miui')) return 'simple-icons:xiaomi'
    if (os.startsWith('one ui')) return 'arcticons:oneui-dark'
    if (os.startsWith('realme')) return 'arcticons:realme-community'
    if (os.startsWith('emui')) return 'simple-icons:huawei'
    if (os.startsWith('harmonyos')) return 'ant-design:harmony-o-s-outlined'
    if (os.startsWith('lineage')) return 'simple-icons:lineageos'
    if (os.startsWith('crdroid')) return 'cib:android'
    if (os.startsWith('pixel experience')) return 'cib:android'
    if (os.startsWith('evolutionx')) return 'cib:android'
    if (os.startsWith('miku')) return 'tdesign:green-onion'
    if (os.endsWith('android')) return 'cib:android'
  }

  return 'icon-park-solid:coordinate-system'
})

const iconClass = computed(() => {
  if (debianFishCakeEaster.value) {
    return 'animate-rotate-in animate-duration-500 animate-ease-in-out'
  }
  switch (osIcon.value) {
    case 'tdesign:green-onion':
      return 'text-[#39c5bb]'
  }
  return ''
})

function onIconClick() {
  switch (osIcon.value) {
    case 'mdi:debian':
      debianFishCakeEaster.value = true
      break
    case 'noto:fish-cake-with-swirl':
      debianFishCakeEaster.value = false
      break
  }
}

const statusName = computed(() => {
  switch (info.status) {
    case 'online':
      return '在线'
    case 'idle':
      return '闲置'
    case 'offline':
      return '离线'
  }
  return '未知'
})

function formatUpdate(timestamp: number) {
  const now = Date.now()
  const diff = now - timestamp

  if (diff <= 0) return '0秒'

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

function updateTimeCallback() {
  lastUpdate.value = getLastUpdate()
  appOpenedTime.value = getAppOpenedTime()
}

onMounted(() => {
  setInterval(updateTimeCallback, 1000)
})

onBeforeUnmount(() => {
  if (updateTimer.value !== null) clearInterval(updateTimer.value)
})

onUpdated(() => {
  updateTimeCallback()
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

        <div flex="~ items-center justify-end gap-2 wrap" text-light text-sm my="1">
          <div
            v-if="info.device_os"
            flex="~ items-center gap-1"
            title="操作系统"
            @dblclick="onIconClick"
          >
            <Icon :icon="osIcon" :class="iconClass" />
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
