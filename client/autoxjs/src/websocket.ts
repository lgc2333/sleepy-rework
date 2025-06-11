import { BasicWebSocket, TypedEventTarget } from 'sleepy-rework-types'

const { Request, WebSocketListener } = Packages['okhttp3']

type WebSocketEventMap = {
  [P in keyof globalThis.WebSocketEventMap]: globalThis.WebSocketEventMap[P]
}

// @ts-ignore
const OkHttp = new com.stardust.autojs.core.http.MutableOkHttp()

export class WebSocket
  extends TypedEventTarget<WebSocketEventMap>
  implements BasicWebSocket
{
  readonly url: string
  readonly protocol: string

  protected $readyState = BasicWebSocket.CONNECTING

  protected $webSocket: any | null = null

  get readyState(): BasicWebSocket.ReadyState {
    return this.$readyState
  }

  constructor(url: string, protocols?: string | string[]) {
    super()
    this.url = url.toString()
    this.protocol = Array.isArray(protocols) ? protocols.join(', ') : protocols || ''

    const requestBuilder = new (Request as any).Builder().url(this.url)
    if (this.protocol) {
      requestBuilder.addHeader('Sec-WebSocket-Protocol', this.protocol)
    }
    const request = requestBuilder.build()
    this.$setupClient(request)
  }

  protected $setupClient(request: any) {
    const self = this

    const listener = {
      onOpen: function (webSocket: any, response: any) {
        self.$webSocket = webSocket
        self.$readyState = BasicWebSocket.OPEN
        self.dispatchEvent(new Event('open'))
      },

      onMessage: function (webSocket: any, msg: any) {
        if (typeof msg !== 'string') {
          console.warn('WebSocket received non-string message, ignoring.')
          return
        }
        self.dispatchEvent(
          new MessageEvent('message', {
            data: msg,
            origin: self.url,
            lastEventId: '',
            source: null,
            ports: [],
          }),
        )
      },

      onClosing: function (webSocket: any, code: number, reason: string) {
        self.$readyState = BasicWebSocket.CLOSING
      },

      onClosed: function (webSocket: any, code: number, reason: string) {
        self.$readyState = BasicWebSocket.CLOSED
        self.dispatchEvent(
          new CloseEvent('close', {
            wasClean: code === 1000,
            code: code,
            reason: reason,
          }),
        )
      },

      onFailure: function (webSocket: any, t: any, response: any) {
        self.$readyState = BasicWebSocket.CLOSED
        self.dispatchEvent(new Event('error'))

        // 同时触发 close 事件
        const closeEvent = new CloseEvent('close', {
          wasClean: false,
          code: 1006,
          reason: t ? t.toString() : 'Connection failed',
        })
        self.dispatchEvent(closeEvent)
      },
    }

    // 创建 WebSocket 连接
    try {
      this.$webSocket = OkHttp.newWebSocket(request, new WebSocketListener(listener))
    } catch (e) {
      // 如果连接失败，延迟触发错误事件
      setTimeout(() => {
        self.$readyState = BasicWebSocket.CLOSED
        self.dispatchEvent(new Event('error'))
        self.dispatchEvent(
          new CloseEvent('close', {
            wasClean: false,
            code: 1006,
            reason: `${e}`,
          }),
        )
      }, 0)
    }
  }

  close(code?: number, reason?: string): void {
    if (
      this.$readyState === BasicWebSocket.CLOSED ||
      this.$readyState === BasicWebSocket.CLOSING
    ) {
      return
    }

    this.$readyState = BasicWebSocket.CLOSING
    if (!this.$webSocket) return

    try {
      this.$webSocket.close(code || 1000, reason || '')
    } catch (e) {
      // 如果关闭失败，强制设置状态
      this.$readyState = BasicWebSocket.CLOSED
      this.dispatchEvent(
        new CloseEvent('close', {
          wasClean: false,
          code: 1006,
          reason: `${e}`,
        }),
      )
    }
  }

  send(data: string): void {
    if (this.$readyState !== BasicWebSocket.OPEN) {
      throw new Error('WebSocket is not open: readyState ' + this.$readyState)
    }
    if (!this.$webSocket) {
      throw new Error('WebSocket is not initialized')
    }
    try {
      this.$webSocket.send(data)
    } catch (e) {
      throw e instanceof Error ? e : new Error(`${e}`)
    }
  }
}
