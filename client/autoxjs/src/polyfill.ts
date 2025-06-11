import { Event, EventTarget } from 'event-target-shim'

globalThis.EventTarget = EventTarget as any
globalThis.Event = Event as any

class CustomEvent<T> extends globalThis.Event implements globalThis.CustomEvent {
  readonly detail: T

  constructor(type: string, eventInitDict?: CustomEventInit<T>) {
    super(type, eventInitDict)
    this.detail = eventInitDict?.detail || (undefined as T)
  }

  initCustomEvent(
    type: string,
    bubbles?: boolean,
    cancelable?: boolean,
    detail?: T,
  ): void {
    throw new Error('Not implemented')
  }
}

class MessageEvent<T> extends globalThis.Event implements globalThis.MessageEvent {
  readonly data: T
  readonly origin: string
  readonly lastEventId: string
  readonly source: globalThis.MessageEventSource | null
  readonly ports: ReadonlyArray<globalThis.MessagePort>

  constructor(type: string, eventInitDict?: globalThis.MessageEventInit<T>) {
    super(type, eventInitDict)
    this.data = eventInitDict?.data ?? ('' as any)
    this.origin = eventInitDict?.origin ?? ''
    this.lastEventId = eventInitDict?.lastEventId ?? ''
    this.source = eventInitDict?.source ?? null
    this.ports = eventInitDict?.ports ?? []
  }

  initMessageEvent(
    type: string,
    bubbles?: boolean,
    cancelable?: boolean,
    data?: any,
    origin?: string,
    lastEventId?: string,
    source?: MessageEventSource | null,
    ports?: MessagePort[],
  ): void {
    throw new Error('Not implemented')
  }
}

class CloseEvent extends globalThis.Event implements globalThis.CloseEvent {
  readonly code: number
  readonly reason: string
  readonly wasClean: boolean

  constructor(type: string, eventInitDict?: globalThis.CloseEventInit) {
    super(type, eventInitDict)
    this.code = eventInitDict?.code ?? 1000
    this.reason = eventInitDict?.reason ?? ''
    this.wasClean = eventInitDict?.wasClean ?? false
  }
}

globalThis.CustomEvent = CustomEvent
globalThis.MessageEvent = MessageEvent
globalThis.CloseEvent = CloseEvent
