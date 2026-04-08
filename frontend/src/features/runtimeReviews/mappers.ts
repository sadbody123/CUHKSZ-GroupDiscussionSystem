import { ApiError } from "../../api/client";

export function toUserErrorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.status === 400) return `请求失败：${err.detail}`;
    if (err.status === 404) return "资源不存在或已被移除。";
    if (err.status === 409) return "版本冲突，请刷新后重试。";
    return `接口错误(${err.status})：${err.detail}`;
  }
  if (err instanceof Error) return err.message;
  return "发生未知错误，请稍后重试。";
}
