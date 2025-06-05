/* eslint-disable ts/no-empty-object-type */
import type { components } from './schema'

export * from './schema'

export type DeviceConfig = components['schemas']['DeviceConfig']
export type DeviceCurrentApp = components['schemas']['DeviceCurrentApp']
export type DeviceData = components['schemas']['DeviceData']
export type DeviceInfo = components['schemas']['DeviceInfo']
export type DeviceInfoFromClient = components['schemas']['DeviceInfoFromClient']
export type DeviceType = components['schemas']['DeviceType']
export type ErrDetail = components['schemas']['ErrDetail']
export type FrontendConfig = components['schemas']['FrontendConfig']
export type FrontendStatusConfig = components['schemas']['FrontendStatusConfig']
export type Info = components['schemas']['Info']
export type OnlineStatus = components['schemas']['OnlineStatus']
export type OpSuccess = components['schemas']['OpSuccess']

export type DeviceInfoFromClientWS = DeviceInfoFromClient & { replace?: boolean }

export interface ws {
  '/api/v1/info': {
    headers?: {}
    path?: {}
    query?: {}
    send: any
    recv: Info
  }
  '/api/v1/device/{device_key}/info': {
    headers?: {
      Authorization?: string
      'X-Sleepy-Secret'?: string
    }
    path?: {
      device_key: string
    }
    query?: {}
    send: DeviceInfoFromClientWS
    recv: DeviceInfo
  }
}

export type StringOnly<T> = T extends string ? T : never
export type WsPath = StringOnly<keyof ws>
export type WsHeaders<T extends WsPath> = ws[T]['headers']
export type WsPathParams<T extends WsPath> = ws[T]['path']
export type WsQueryParams<T extends WsPath> = ws[T]['query']
export type WsSendData<T extends WsPath> = ws[T]['send']
export type WsRecvData<T extends WsPath> = ws[T]['recv']
