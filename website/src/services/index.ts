import { useToast } from 'vue-toastification'
import type { ToastID, ToastOptions } from 'vue-toastification/dist/types/types'

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

export function connectWS<T extends WsPath>(
  endpoint: T,
  onMessage: (data: WsMessage<T>) => void,
  onError?: (error: Event) => void,
  onClose?: (event: CloseEvent) => void,
) {
  const url = `${WS_BASE}${endpoint}`

  let ws: WebSocket | null = null
  let wsCloseToastID: ToastID | null = null

  const reconnect = () => {
    setTimeout(() => connect(), 3000)
  }

  const connect = () => {
    ws = new WebSocket(url)

    ws.addEventListener('open', () => {
      if (wsCloseToastID) toast.dismiss(wsCloseToastID)
      console.log(`WebSocket connected`)
      toast.success(`已连接服务端`)
    })

    ws.addEventListener('message', (event) => {
      try {
        const data = JSON.parse(event.data) as WsMessage<T>
        onMessage(data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
        toast.error(`服务端发送数据解析失败`)
      }
    })

    ws.addEventListener('error', (error) => {
      console.error('WebSocket error:', error)
      // toast.error(`连接服务端出错`)
      onError?.(error)
    })

    ws.addEventListener('close', (ev) => {
      console.warn('WebSocket connection closed')
      if (!wsCloseToastID) {
        wsCloseToastID = toast.error(`服务端连接断开 (${ev.code})，正在重连`, {
          timeout: false,
          closeButton: false,
          closeOnClick: false,
        })
        onClose?.(ev)
      }
      reconnect()
    })
  }

  const getWebSocket = () => {
    return ws
  }

  connect()

  return { getWebSocket }
}
