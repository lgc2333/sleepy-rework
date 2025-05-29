import { defineConfig, presetAttributify, presetWind3 } from 'unocss'

export default defineConfig({
  presets: [presetAttributify(), presetWind3()],
  shortcuts: {
    'text-primary': 'text-op-90 text-gray-900 dark:text-gray-200',
    'text-lighter': 'text-op-90 text-gray-800 dark:text-gray-300',
    'text-lightest': 'text-op-90 text-gray-600 dark:text-gray-400',
    'bg-primary': 'text-op-90 bg-white dark:bg-gray-900',
    card:
      'bg-primary bg-op-10 hover:bg-op-20 dark:bg-op-30 dark:hover:bg-op-40' +
      ' text-primary shadow-sm hover:shadow-md transition transition-duration-500',
    indicator: 'transition-colors',
  },
  theme: {},
})
