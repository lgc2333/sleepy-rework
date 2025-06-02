export enum DeviceType {
  PC = 'pc',
  LAPTOP = 'laptop',
  PHONE = 'phone',
  TABLET = 'tablet',
  SMARTWATCH = 'smartwatch',
  UNKNOWN = 'unknown',
}

export enum DeviceOS {
  WINDOWS = 'Windows',
  MACOS = 'MacOS',
  LINUX = 'Linux',
  ANDROID = 'Android',
  IOS = 'iOS',
  WEAR_OS = 'Wear OS',
  UNKNOWN = 'unknown',
}

export enum OnlineStatus {
  ONLINE = 'online',
  OFFLINE = 'offline',
  IDLE = 'idle',
  UNKNOWN = 'unknown',
}

export interface ErrDetail {
  type?: string | null
  msg?: string | null
  data?: any
}

export interface DeviceCurrentApp {
  name: string
  last_change_time?: number | null
}

export interface DeviceData {
  current_app?: DeviceCurrentApp | null
  additional_statuses?: string[] | null
  [key: string]: any
}

export interface DeviceInfo {
  name: string
  description?: string | null
  device_type: DeviceType | string
  device_os: DeviceOS | string
  remove_when_offline: boolean
  data?: DeviceData | null
  online: boolean
  idle: boolean
  status: Exclude<OnlineStatus, OnlineStatus.UNKNOWN>
  last_update_time?: number | null
  long_connection: boolean
}

export interface Info {
  status: OnlineStatus
  devices?: Record<string, DeviceInfo>
}

export interface OpSuccess {
  success: true
}

export interface FrontendStatusConfig {
  name: string
  description: string
  color: string
}

export interface FrontendConfig {
  username: string
  statuses: Record<OnlineStatus, FrontendStatusConfig>
  [key: string]: any
}

export interface ApiResponses {
  '/': { GET: string }
  '/config/frontend': { GET: FrontendConfig }
  '/info': { GET: Info }
}

export type ApiPath = keyof ApiResponses
export type ApiMethod<T extends ApiPath> = keyof ApiResponses[T]
export type ApiResponse<T extends ApiPath, M extends ApiMethod<T>> = ApiResponses[T][M]

export interface WsMessages {
  '/info': Info
}
export type WsPath = keyof WsMessages
export type WsMessage<T extends WsPath> = WsMessages[T]
