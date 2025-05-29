import { defineConfig, presetAttributify, presetWind3 } from 'unocss'

export default defineConfig({
  presets: [presetAttributify(), presetWind3()],
  shortcuts: {
    'text-dark': 'text-op-90 text-gray-900 dark:text-gray-200',
    'text-primary': 'text-op-90 text-gray-850 dark:text-gray-300',
    'text-light': 'text-op-90 text-gray-600 dark:text-gray-400',
    'text-lighter': 'text-op-90 text-gray-500 dark:text-gray-500',
    'bg-primary': 'text-op-90 bg-white dark:bg-gray-900',
    card:
      'bg-primary bg-op-10 hover:bg-op-20 dark:bg-op-30 dark:hover:bg-op-40' +
      ' text-primary shadow-sm hover:shadow-md transition transition-duration-500',
    indicator: 'transition-colors',
  },
  theme: {},
})
