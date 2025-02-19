import { ReactNode } from "react"
import useAxiosInterceptor from "@/hooks/useAxiosInterceptor"

export default function AxiosInterceptorWrapper({ children }: { children: ReactNode }) {
  useAxiosInterceptor()
  return children
}
