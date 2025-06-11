declare namespace device {
  function getBattery(): number
  function isCharging(): boolean
  function isScreenOn(): boolean
}

declare namespace app {
  function getAppName(packageName: string): string
}

declare namespace auto {
  function waitFor(): void
}

declare namespace events {
  function on(eventName: string, callback: (...args: any[]) => void): void
}

declare namespace globalThis {
  function currentPackage(): string

  function importPackage(package: any): void
  const Packages: Record<string, any>
}
