import '@unocss/reset/tailwind-compat.css'
import 'virtual:uno.css'
import { createApp } from 'vue'
import Toast, { POSITION } from 'vue-toastification'
import type { PluginOptions as ToastOptions } from 'vue-toastification'
import 'vue-toastification/dist/index.css'

import App from './App.vue'
import './style.scss'

createApp(App)
  .use(Toast, { position: POSITION.BOTTOM_RIGHT } satisfies ToastOptions)
  .mount('#app')
