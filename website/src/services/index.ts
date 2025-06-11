import createClient from 'openapi-fetch'
import type {
  ErrDetail,
  WsPath,
  WsPathParams,
  WsQueryParams,
  WsRecvData,
  openapi,
} from 'sleepy-rework-types'
import { TYPE, useToast } from 'vue-toastification'
import type {
  ToastContent,
  ToastID,
  ToastOptions,
} from 'vue-toastification/dist/types/types'

const toast = useToast()

export const API_BASE = import.meta.env.VITE_API_BASE_URL || window.location.origin
export const WS_BASE = API_BASE.replace(/^http/, 'ws')

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: ErrDetail,
  ) {
    super(
      `[${status}]` +
        `${detail.type ? ` (${detail.type})` : ''}` +
        `${detail.msg ? `: ${detail.msg}` : ''}`,
    )
    this.name = 'ApiError'
    this.detail = detail
  }
}

export const immutableToastOptions = {
  timeout: false,
  draggable: false,
  closeButton: false,
  closeOnClick: false,
} satisfies ToastOptions

export const client = createClient<openapi.paths>({ baseUrl: API_BASE })
client.use({
  onResponse: async ({ response }) => {
    if (!response.ok) {
      throw new ApiError(response.status, await response.json())
    }
  },
  onError: ({ error }) => {
    return error instanceof Error ? error : new Error(`${error}`)
  },
})

export type WSPathOption<K extends WsPath> =
  WsPathParams<K> extends never ? {} : { path: WsPathParams<K> }
export type WSQueryOption<K extends WsPath> =
  WsQueryParams<K> extends never ? {} : { query: WsQueryParams<K> }
export type WSOption<K extends WsPath> = WSPathOption<K> & WSQueryOption<K>

export function createWS<T extends WsPath>(
  endpoint: T,
  options: WSOption<T> & {
    onOpen?: (event: Event) => void
    onMessage?: (data: WsRecvData<T>) => void
    onError?: (event: Event) => void
    onClose?: (event: CloseEvent) => void
  },
) {
  if ('path' in options) {
    for (const [k, v] of Object.entries(options.path)) {
      endpoint = endpoint.replace(`{${k}}`, encodeURIComponent(v)) as any
    }
  }

  const url = `${WS_BASE}${endpoint}`

  let ws: WebSocket | null = null
  let stickingToastID: ToastID | null = null
  let connected = false
  let firstConnect = true
  let stopped = false

  const updateStickingToast = (options?: {
    content?: ToastContent
    options?: ToastOptions
  }) => {
    if (!options) {
      if (stickingToastID !== null) {
        toast.dismiss(stickingToastID)
      }
      return
    }

    if (stickingToastID !== null) {
      toast.update(stickingToastID, options)
    } else {
      stickingToastID = toast(options.content, options.options)
    }
  }

  const connect = () => {
    ws = new WebSocket(url)
    if (!firstConnect) {
      updateStickingToast({
        content: `正在连接服务端`,
        options: { type: TYPE.INFO, ...immutableToastOptions },
      })
    }
    firstConnect = false

    ws.addEventListener('open', (event) => {
      updateStickingToast()
      // console.log(`WebSocket connected`)
      // toast.success(`已连接服务端`)
      connected = true
      options.onOpen?.(event)
    })

    ws.addEventListener('message', (event) => {
      try {
        const data = JSON.parse(event.data) as WsRecvData<T>
        options.onMessage?.(data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
        toast.error(`服务端发送数据解析失败`)
      }
    })

    ws.addEventListener('error', (error) => {
      console.error('WebSocket error:', error)
      // toast.error(`连接服务端出错`)
      if (stopped) return
      options.onError?.(error)
    })

    ws.addEventListener('close', (ev) => {
      console.warn('WebSocket connection closed')
      if (stopped) return
      updateStickingToast({
        content: `服务端连接${connected ? '断开' : '失败'} (${ev.code})，3 秒后重连`,
        options: { type: TYPE.ERROR, ...immutableToastOptions },
      })
      connected = false
      options.onClose?.(ev)
      setTimeout(() => connect(), 3000)
    })
  }

  const getWebSocket = () => {
    return ws
  }

  const stop = () => {
    stopped = true
    connected = false
    ws?.close()
  }

  const cleanup = () => {
    stop()
    updateStickingToast()
  }

  return { getWebSocket, connect, stop, cleanup }
}
