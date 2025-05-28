<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { useDark } from '@vueuse/core'
import { computed, onMounted, ref } from 'vue'

import DeviceCard from './components/DeviceCard.vue'
import { connectWS, request } from './services'
import { type FrontendConfig, type Info, OnlineStatus } from './types'

const loadFailed = ref(false)
const config = ref<FrontendConfig | null>(null)
const info = ref<Info | null>(null)
const currentStatus = computed(() => {
  return config.value && info.value ? config.value.status[info.value.status] : null
})

const dark = useDark()
const toggleDark = () => {
  document.startViewTransition(() => {
    dark.value = !dark.value
  })
}

onMounted(async () => {
  try {
    config.value = await request('/config/frontend', 'GET', {
      timeout: false,
      closeButton: false,
      closeOnClick: false,
    })
    connectWS('/info', (data) => {
      info.value = data
    })
  } catch (e) {
    loadFailed.value = true
  }
})
</script>

<template>
  <div absolute top-2 right-2 text-primary>
    <button
      transition="~ duration-500"
      bg="transparent hover:white hover:op-20"
      border="none"
      rounded
      shadow="hover:sm"
      p="1"
      op="30 hover:100"
      text-primary
      @click="toggleDark()"
    >
      <Icon
        :icon="dark ? 'mdi:weather-night' : 'mdi:weather-sunny'"
        text-size-3xl
        :title="dark ? 'Switch to light mode' : 'Switch to dark mode'"
      />
    </button>
  </div>

  <div flex="~ items-center justify-center" min-h="screen" max-w="99vw" text-primary>
    <div
      v-if="config && info"
      card
      p-8
      rounded-xl
      w="fit"
      flex="~ col items-center"
      gap="4"
    >
      <h1>{{ config.username }}'s Status</h1>
      <h1 text-op-90 :style="`color: ${currentStatus!.color}`" transition-color>
        {{ currentStatus!.name }}
      </h1>
      <p
        :text-lighter="info.status === OnlineStatus.ONLINE ? null : ''"
        transition-color
      >
        {{ currentStatus!.description }}
      </p>
      <template v-if="info.devices">
        <div v-if="Object.keys(info.devices).length > 1" grid="~" cols-2>
          <DeviceCard v-for="(device, id) in info.devices" :key="id" :info="device" />
        </div>
        <div v-else grid="~" cols-1>
          <DeviceCard v-for="(device, id) in info.devices" :key="id" :info="device" />
        </div>
      </template>
    </div>
    <div v-else-if="loadFailed" card p-8 rounded-xl>Failed to load data</div>
    <div v-else card p-8 rounded-xl>Loading...</div>
  </div>
</template>

<style lang="scss" scoped></style>
