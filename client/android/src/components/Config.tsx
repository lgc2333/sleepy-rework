import { useMemo } from 'react'
import type { ListItemProps } from 'react-native-paper'
import { List } from 'react-native-paper'

import { useConfig } from '../hooks/useConfig'
import type { Config } from '../utils/config'

export interface CallbackProps<K extends keyof Config> {
  value: Config[K]
  updateValue: (value: Config[K]) => void
  disabled: boolean
}

export type OriginalRightProps = Parameters<NonNullable<ListItemProps['right']>>[0]

export interface ConfigProps<K extends keyof Config> {
  configKey: K
  right?: (props: OriginalRightProps & CallbackProps<K>) => React.ReactNode
  onPress?: (props: CallbackProps<K>) => void
  onSetFailed?: (error: unknown, key: K) => void
}

export type ConfigListProps<K extends keyof Config> = Omit<
  ListItemProps,
  keyof ConfigProps<K>
> &
  ConfigProps<K>

export function ConfigListItem<K extends keyof Config>({
  configKey,
  right,
  onPress,
  onSetFailed,
  disabled: originalDisabled,
  ...props
}: ConfigListProps<K>) {
  const { value, updateValue, isLoading } = useConfig(configKey, (e) => {
    onSetFailed?.(e, configKey)
  })
  const disabled = useMemo(
    () => originalDisabled ?? isLoading,
    [originalDisabled, isLoading],
  )
  return (
    <List.Item
      {...props}
      right={(props) => right?.({ ...props, value, updateValue, disabled })}
      onPress={() => {
        if (!disabled) {
          onPress?.({ value, updateValue, disabled })
        }
      }}
    />
  )
}
