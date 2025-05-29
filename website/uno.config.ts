import { defineConfig, presetAttributify, presetWind3 } from 'unocss'

export default defineConfig({
  presets: [presetAttributify(), presetWind3()],
  shortcuts: {
    'text-dark': 'text-op-90 text-black dark:text-gray-2',
    'text-primary': 'text-op-90 text-gray-9 dark:text-gray-3',
    'text-light': 'text-op-90 text-gray-6 dark:text-gray-4',
    'text-lighter': 'text-op-90 text-gray-5 dark:text-gray-5',
    'bg-primary': 'text-op-90 bg-white dark:bg-gray-9',
    card:
      'bg-primary bg-op-10 hover:bg-op-20 dark:bg-op-30 dark:hover:bg-op-40' +
      ' text-primary shadow-sm hover:shadow-md transition transition-duration-500',
    indicator: 'transition-colors',
  },
  theme: {},
})
