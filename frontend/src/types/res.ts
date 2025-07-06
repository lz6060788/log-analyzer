export type RespType<T extends any> = {
  code: number
  message: string
  data: T
}