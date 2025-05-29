import { TYPE, useToast } from 'vue-toastification'
import type {
  ToastContent,
  ToastID,
  ToastOptions,
} from 'vue-toastification/dist/types/types'

import type {
  ApiMethod,
  ApiPath,
  ApiResponse,
  ErrDetail,
  WsMessage,
  WsPath,
} from '../types'

const toast = useToast()

const API_BASE = `${import.meta.env.VITE_API_BASE_URL || window.location.origin}/api/v1`
const WS_BASE = API_BASE.replace(/^http/, 'ws')

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

export async function request<T extends ApiPath, M extends ApiMethod<T>>(
  path: T,
  method: M,
  toastOptions: Omit<ToastOptions, 'type'> = {},
): Promise<ApiResponse<T, M>> {
  const options: RequestInit = {
    method: method as string,
    headers: {
      'Content-Type': 'application/json',
    },
  }

  let resp: Response
  let data: any
  try {
    resp = await fetch(`${API_BASE}${path}`, options)
    data = await resp.json()
  } catch (e) {
    toast.error(`请求出错：${e}`, toastOptions)
    throw e
  }

  if (!resp.ok) {
    const e = new ApiError(resp.status, data)
    toast.error(`请求出错：${e}`, toastOptions)
    throw e
  }
  return data
}

export function createWS<T extends WsPath>(
  endpoint: T,
  options: {
    onOpen?: (event: Event) => void
    onMessage?: (data: WsMessage<T>) => void
    onError?: (event: Event) => void
    onClose?: (event: CloseEvent) => void
  } = {},
) {
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
        options: {
          type: TYPE.INFO,
          timeout: false,
          draggable: false,
          closeButton: false,
          closeOnClick: false,
        },
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
        const data = JSON.parse(event.data) as WsMessage<T>
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
        options: {
          type: TYPE.ERROR,
          timeout: false,
          draggable: false,
          closeButton: false,
          closeOnClick: false,
        },
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
