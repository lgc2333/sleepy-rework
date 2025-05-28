export enum DeviceType {
  PC = 'pc',
  PHONE = 'phone',
  TABLET = 'tablet',
  SMARTWATCH = 'smartwatch',
  UNKNOWN = 'unknown',
}

export enum DeviceOS {
  WINDOWS = 'windows',
  MACOS = 'macos',
  LINUX = 'linux',
  ANDROID = 'android',
  IOS = 'ios',
  UNKNOWN = 'unknown',
}

export enum OnlineStatus {
  ONLINE = 'online',
  OFFLINE = 'offline',
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
  device_type: DeviceType | string
  device_os: DeviceOS | string
  current_app?: DeviceCurrentApp | null
  [key: string]: any
}

export interface DeviceInfo {
  name: string
  description?: string | null
  online: boolean
  data?: DeviceData | null
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
  status: Record<OnlineStatus, FrontendStatusConfig>
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
