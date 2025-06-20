import AsyncStorage from '@react-native-async-storage/async-storage'

// eslint-disable-next-line ts/consistent-type-definitions
export type Config = {
  serverEnableConnect: boolean
  serverUrl: string
  serverSecret: string
  deviceKey: string
}

export type FilterKeyTypedAs<O extends Record<any, any>, T> = Pick<
  O,
  { [K in keyof O]: O[K] extends T ? K : never }[keyof O]
>
export type ConfigKeyWithType<T> = keyof FilterKeyTypedAs<Config, T>

export const defaultConfig: Config = {
  serverEnableConnect: false,
  serverUrl: 'http://localhost:29306',
  serverSecret: 'sleepy',
  deviceKey: 'android',
}

export function setConfig<K extends keyof Config>(
  key: K,
  value: Config[K],
): Promise<void> {
  return AsyncStorage.setItem(key, JSON.stringify(value))
}

export async function getConfig<K extends keyof Config>(key: K): Promise<Config[K]> {
  const value = await AsyncStorage.getItem(key)
  if (value === null) {
    return defaultConfig[key]
  }
  return JSON.parse(value) as Config[K]
}
