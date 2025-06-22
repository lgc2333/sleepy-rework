export const httpUrlRegex =
  /^(?<scheme>http|https):\/\/(?<host>[a-zA-Z0-9\.]+)(?<port>:\d+)?(?<path>\/.*)?$/

export function httpUrlValidator(url: string): string | void {
  if (!httpUrlRegex.test(url)) return '请输入正确的 HTTP URL'
}
