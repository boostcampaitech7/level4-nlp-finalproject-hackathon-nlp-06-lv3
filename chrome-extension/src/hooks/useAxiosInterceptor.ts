import { useEffect } from "react"
import { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from "axios"
import { useSetRecoilState } from "recoil"
import useToast from "@/hooks/useToast"
import { ApiResponse } from "@/types/response"
import axiosInstance from "@/utils/axiosInstance"
import { userIdState } from "@/states/auth"

export default function useAxiosInterceptor() {
  const setUserId = useSetRecoilState(userIdState)
  const { addErrorToast } = useToast()

  const requestHandler = async (config: InternalAxiosRequestConfig) => {
    return config
  }

  const responseHandler = (response: AxiosResponse) => {
    return response
  }

  const errorHandler = (error: AxiosError) => {
    const errorResponse = error.response?.data as ApiResponse
    switch (errorResponse.status) {
      case 401:
        addErrorToast("인증 되지 않았습니다.")
        setUserId(0)
        break
      case 403:
        addErrorToast("권한이 없습니다.")
        break
      default:
        if (errorResponse.response === "UNKNOWN_SERVER_ERROR") {
          addErrorToast("서버 오류가 발생했습니다.")
        }
    }
    return Promise.reject(error)
  }

  const requestInterceptor = axiosInstance.interceptors.request.use(requestHandler)

  const responseInterceptor = axiosInstance.interceptors.response.use(
    (response) => responseHandler(response),
    (error) => errorHandler(error),
  )

  useEffect(() => {
    return () => {
      axiosInstance.interceptors.request.eject(requestInterceptor)
      axiosInstance.interceptors.response.eject(responseInterceptor)
    }
  }, [responseInterceptor, requestInterceptor])
}
