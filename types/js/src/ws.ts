import type { DeviceInfo, DeviceInfoFromClient, Info } from './base'

export type DeviceInfoFromClientWS = DeviceInfoFromClient & { replace?: boolean }

export interface ws {
  '/api/v1/info': {
    headers: never
    path: never
    query: never
    send: any
    recv: Info
  }
  '/api/v1/device/{device_key}/info': {
    headers: {
      Authorization?: string
      'X-Sleepy-Secret'?: string
    }
    path: {
      device_key: string
    }
    query: never
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
