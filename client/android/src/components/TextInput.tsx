import { useMemo, useState } from 'react'
import { HelperText, TextInput as OriginalTextInput } from 'react-native-paper'
import type { TextInputProps } from 'react-native-paper'

export interface Props extends TextInputProps {
  valueValidator?: (text: string) => string | void
  onValueSubmit?: (text: string) => void
}

export default function TextInput({ value, error, valueValidator, ...props }: Props) {
  const [currentText, setCurrentText] = useState<string>(value ?? '')
  const errorText = useMemo(
    () => valueValidator?.(currentText) ?? null,
    [currentText, valueValidator],
  )
  const isError = useMemo(() => error || !!errorText, [error, errorText])
  return (
    <>
      <OriginalTextInput
        {...props}
        error={isError}
        value={currentText}
        onChangeText={(text) => {
          setCurrentText(text)
          props.onChangeText?.(text)
        }}
        onBlur={(e) => {
          props.onBlur?.(e)
          if (!isError) props.onValueSubmit?.(currentText)
        }}
      />
      {errorText && <HelperText type="error">{errorText}</HelperText>}
    </>
  )
}
