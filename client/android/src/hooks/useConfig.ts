import { useCallback, useEffect, useState } from 'react'

import type { Config } from '../utils/config'
import { defaultConfig, getConfig, setConfig } from '../utils/config'

export function useConfig<K extends keyof Config>(
  configKey: K,
  onSetFailed: (error: unknown) => void,
) {
  const [value, setValue] = useState<Config[K]>(defaultConfig[configKey] as any)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    const fetchValue = async () => {
      setIsLoading(true)
      try {
        const configValue = await getConfig(configKey)
        setValue(configValue)
      } catch (error) {
        console.error(`Error fetching config value for key "${configKey}":`, error)
        onSetFailed(error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchValue()
  }, [configKey, onSetFailed])

  const updateValue = useCallback(
    async (newValue: Config[K]) => {
      setIsLoading(true)
      try {
        await setConfig(configKey, newValue)
        setValue(newValue)
      } catch (error) {
        console.error(`Error setting config value for key "${configKey}":`, error)
        onSetFailed(error)
      } finally {
        setIsLoading(false)
      }
    },
    [configKey, onSetFailed],
  )

  return { value, updateValue, isLoading }
}
