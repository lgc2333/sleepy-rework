<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { useDark } from '@vueuse/core'
import type { FrontendConfig, Info } from 'sleepy-rework-types'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useToast } from 'vue-toastification'

import DeviceCard from './components/DeviceCard.vue'
import { client, createWS, immutableToastOptions } from './services'

const config = ref<FrontendConfig | null>(null)
const info = ref<Info | null>(null)
const currentStatus = computed(() => {
  return config.value && info.value ? config.value.statuses[info.value.status] : null
})

const dark = useDark()
function toggleDark() {
  document.startViewTransition(() => {
    dark.value = !dark.value
  })
}

const toast = useToast()

const ws = createWS('/api/v1/info', {
  onOpen: () => {
    client
      .GET('/api/v1/config/frontend')
      .then((res) => {
        config.value = res.data!
      })
      .catch((e) => {
        console.error(e)
        toast.error('获取前端配置失败，请刷新页面重试', immutableToastOptions)
      })
  },
  onMessage: (data) => {
    info.value = data
  },
})

onMounted(async () => {
  ws.connect()
})

onUnmounted(() => {
  ws.cleanup()
})
</script>

<template>
  <div absolute top-2 right-2>
    <button
      transition="~ duration-500"
      bg="transparent hover:white hover:op-20"
      border="none"
      rd-full
      shadow="hover:sm"
      p="1"
      op="30 hover:100"
      text-primary
      :title="dark ? '切换亮色' : '切换暗色'"
      @click="toggleDark()"
    >
      <Icon :icon="dark ? 'ph:moon' : 'ph:sun'" text-size-3xl />
    </button>
  </div>

  <div flex="~ items-center justify-center" min-h="screen">
    <div
      v-if="config && info"
      card
      p-8
      rounded-xl
      w="fit"
      max-w="4xl"
      flex="~ col items-center"
      gap="4"
      m="2"
    >
      <div text-3xl font-medium>{{ config.username }}'s Status</div>
      <div
        text-4xl
        font-bold
        :style="`color: ${currentStatus!.color}`"
        transition-color
      >
        {{ currentStatus!.name }}
      </div>
      <div>{{ currentStatus!.description }}</div>

      <template v-if="info.devices && Object.keys(info.devices).length">
        <div gap-2 class="devices-grid">
          <DeviceCard v-for="(device, id) in info.devices" :key="id" :info="device" />
        </div>
      </template>
    </div>
    <div v-else card p-8 rounded-xl>Loading...</div>
  </div>
</template>

<style lang="scss" scoped>
.devices-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));

  & > * {
    grid-column: span 4;
  }

  @media (min-width: 640px) {
    &:has(> *:nth-child(2)) > * {
      grid-column: span 2;

      &:last-child:nth-child(2n - 1) {
        grid-column-end: 4;
      }
    }
  }
}
</style>
