export type StringOnly<T> = T extends string ? T : never

export interface EventListener<TE extends Event = Event> {
  (evt: TE): void
}

export interface EventListenerObject<TE extends Event = Event> {
  handleEvent: (object: TE) => void
}

export type EvListenerFuncOrObj<TE extends Event = Event> =
  | EventListener<TE>
  | EventListenerObject<TE>

export interface TargetedCustomEvent<T extends EventTarget | null, P = any>
  extends CustomEvent<P> {
  currentTarget: T
  target: T
}

export class TypedEventTarget<E extends { [key: string]: Event }> extends EventTarget {
  public override addEventListener<K extends StringOnly<keyof E>>(
    type: K,
    callback: EvListenerFuncOrObj<E[K]> | null,
    options?: AddEventListenerOptions | boolean,
  ): void {
    super.addEventListener(type, callback as any, options)
  }

  public override removeEventListener<K extends StringOnly<keyof E>>(
    type: K,
    callback: EvListenerFuncOrObj<E[K]> | null,
    options?: EventListenerOptions | boolean,
  ): void {
    super.removeEventListener(type, callback as any, options)
  }

  public override dispatchEvent<K extends StringOnly<keyof E>>(event: E[K]): boolean {
    return super.dispatchEvent(event)
  }
}
