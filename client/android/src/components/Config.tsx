import React, { useMemo } from 'react'
import { List, Text } from 'react-native-paper'
import type { ListItemProps } from 'react-native-paper'

import { useConfig } from '../hooks/useConfig'
import type { Config } from '../utils/config'

export interface CallbackProps<K extends keyof Config> {
  value: Config[K]
  updateValue: (value: Config[K]) => void
  disabled: boolean
}

export type OriginalDescriptionProps = Parameters<
  Exclude<ListItemProps['description'], React.ReactNode>
>[0]
export type OriginalRightProps = Parameters<NonNullable<ListItemProps['right']>>[0]

export interface ConfigProps<K extends keyof Config> {
  configKey: K
  description?:
    | React.ReactNode
    | ((
        props: { props: OriginalDescriptionProps } & CallbackProps<K>,
      ) => React.ReactNode)
  left?: (props: OriginalRightProps & CallbackProps<K>) => React.ReactNode
  right?: (props: OriginalRightProps & CallbackProps<K>) => React.ReactNode
  onPress?: (props: CallbackProps<K>) => void
  onSetFailed?: (
    error: unknown,
    key: K,
    value: Config[K],
    updateValue: CallbackProps<K>['updateValue'],
  ) => void
}

export type ConfigListProps<K extends keyof Config> = Omit<
  ListItemProps,
  keyof ConfigProps<K>
> &
  ConfigProps<K>

export function ConfigListItem<K extends keyof Config>({
  configKey,
  description,
  left,
  right,
  onPress,
  onSetFailed,
  disabled: originalDisabled,
  ...props
}: ConfigListProps<K>) {
  const { value, updateValue, isLoading } = useConfig(configKey, (e) => {
    onSetFailed?.(e, configKey, value, updateValue)
  })
  const disabled = useMemo(
    () => originalDisabled ?? isLoading,
    [originalDisabled, isLoading],
  )
  return (
    <List.Item
      {...props}
      description={(props) =>
        typeof description === 'string' ? (
          <Text {...props}>{description}</Text>
        ) : typeof description === 'function' ? (
          description({ props, value, updateValue, disabled })
        ) : (
          description
        )
      }
      left={(props) => left?.({ ...props, value, updateValue, disabled })}
      right={(props) => right?.({ ...props, value, updateValue, disabled })}
      onPress={() => {
        if (!disabled) onPress?.({ value, updateValue, disabled })
      }}
    />
  )
}
