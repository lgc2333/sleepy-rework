import type { DeviceInfo, DeviceInfoFromClient, Info } from './base'
import type { StringOnly } from './utils'
import { TypedEventTarget } from './utils'

export type DeviceInfoFromClientWS = DeviceInfoFromClient & { replace?: boolean }

export interface ws {
  '/api/v1/info': {
    path: never
    query: never
    needAuth: false
    send: any
    recv: Info
  }
  '/api/v1/device/{device_key}/info': {
    path: {
      device_key: string
    }
    query: never
    needAuth: true
    send: DeviceInfoFromClientWS
    recv: DeviceInfo
  }
}

export type WsPath = StringOnly<keyof ws>
export type WsPathParams<T extends WsPath> = ws[T]['path']
export type WsQueryParams<T extends WsPath> = ws[T]['query']
export type WsSendData<T extends WsPath> = ws[T]['send']
export type WsRecvData<T extends WsPath> = ws[T]['recv']

export namespace BasicWebSocket {
  export enum ReadyState {
    CONNECTING = 0,
    OPEN = 1,
    CLOSING = 2,
    CLOSED = 3,
  }

  export const CONNECTING = ReadyState.CONNECTING
  export const OPEN = ReadyState.OPEN
  export const CLOSING = ReadyState.CLOSING
  export const CLOSED = ReadyState.CLOSED
}

export interface BasicWebSocket {
  readonly protocol: string
  readonly readyState: BasicWebSocket.ReadyState
  readonly url: string

  close(code?: number, reason?: string): void
  send(data: string): void

  addEventListener<K extends keyof WebSocketEventMap>(
    type: K,
    listener: (this: WebSocket, ev: WebSocketEventMap[K]) => any,
    options?: boolean | AddEventListenerOptions,
  ): void
  removeEventListener<K extends keyof WebSocketEventMap>(
    type: K,
    listener: (this: WebSocket, ev: WebSocketEventMap[K]) => any,
    options?: boolean | EventListenerOptions,
  ): void
}

// eslint-disable-next-line ts/consistent-type-definitions
export type WebSocketClientEvents<M> = {
  open: CustomEvent<{ event: Event }>
  close: CustomEvent<{ event: CloseEvent }>
  error: CustomEvent<{ event: Event }>
  parseError: CustomEvent<{ event: Event; error: Error }>
  message: CustomEvent<{ data: M; event: MessageEvent }>
}

export type WSCPathOptions<K extends WsPath> =
  WsPathParams<K> extends never ? {} : { path: WsPathParams<K> }
export type WSCQueryOptions<K extends WsPath> =
  WsQueryParams<K> extends never ? {} : { query: WsQueryParams<K> }
export type WSCParamOptions<K extends WsPath> = WSCPathOptions<K> & WSCQueryOptions<K>

export interface WSOptionsCommon {
  secret?: string
  webSocketFactory?: (url: string, secret?: string) => BasicWebSocket
}

export type WSOptions<K extends WsPath> = WSOptionsCommon & WSCParamOptions<K>

export class WebSocketClient<P extends WsPath> extends TypedEventTarget<
  WebSocketClientEvents<WsRecvData<P>>
> {
  protected $ws: BasicWebSocket | null = null
  protected $stopped: boolean = true
  protected $reconnectTimer: ReturnType<typeof setTimeout> | null = null

  constructor(
    protected $baseUrl: string,
    protected $path: P,
    protected $options: WSOptions<P>,
  ) {
    super()
  }

  get stopped(): boolean {
    return this.$stopped
  }

  get connected(): boolean {
    return this.$ws !== null && this.$ws.readyState === BasicWebSocket.OPEN
  }

  buildUrl(): string {
    let path: string = this.$path
    if ('path' in this.$options) {
      for (const [k, v] of Object.entries(this.$options.path)) {
        path = path.replace(`{${k}}`, encodeURIComponent(v))
      }
    }

    let url = `${this.$baseUrl.replace(/\/+$/, '')}${path}`
    if ('query' in this.$options) {
      const params = Object.entries(this.$options.query)
        .map(
          ([key, value]) =>
            `${encodeURIComponent(key)}=${encodeURIComponent(`${value}`)}`,
        )
        .join('&')
      const hasAnd = url.includes('?')
      url += `${hasAnd ? '&' : '?'}${params}`
    }
    return url
  }

  protected $newWs() {
    if (this.$options.webSocketFactory) {
      this.$ws = this.$options.webSocketFactory(this.buildUrl(), this.$options.secret)
    } else {
      const { secret } = this.$options
      this.$ws = new WebSocket(this.buildUrl(), secret ? ['sleepy', secret] : undefined)
    }

    this.$ws.addEventListener('open', (event) => {
      this.dispatchEvent(new CustomEvent('open', { detail: { event } }))
    })

    this.$ws.addEventListener('close', (event) => {
      this.$ws = null
      this.$reconnectTimer = setTimeout(() => this.reconnect(), 5000)
      this.dispatchEvent(new CustomEvent('close', { detail: { event } }))
    })

    this.$ws.addEventListener('error', (event) => {
      this.dispatchEvent(new CustomEvent('error', { detail: { event } }))
    })

    this.$ws.addEventListener('message', (event) => {
      let data: any
      try {
        data = JSON.parse(event.data)
      } catch (error) {
        this.dispatchEvent(new CustomEvent('parseError', { detail: { event, error } }))
        return
      }
      this.dispatchEvent(new CustomEvent('message', { detail: { data, event } }))
    })

    return this.$ws
  }

  send<T extends WsPath>(data: WsSendData<T>) {
    if (!this.$ws) throw new Error('WebSocket is not connected')
    this.$ws.send(JSON.stringify(data))
  }

  stop() {
    this.$stopped = true
    if (this.$ws) {
      this.$ws.close()
      this.$ws = null
    }
    if (this.$reconnectTimer) {
      clearTimeout(this.$reconnectTimer)
      this.$reconnectTimer = null
    }
  }

  reconnect() {
    this.stop()
    this.$stopped = false
    this.$newWs()
  }

  start() {
    this.reconnect()
  }
}
