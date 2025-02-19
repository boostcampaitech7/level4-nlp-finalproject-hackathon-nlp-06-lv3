import { AxiosError } from "axios"
import useToast from "@/hooks/useToast"

export default function useErrorResponseHandler() {
  const { addErrorToast, addWarningToast } = useToast()

  return (err: Error, response?: string, message?: string, type?: "WARN" | "ERR") => {
    if (!(err instanceof AxiosError)) {
      addErrorToast(err.message)
      return
    }

    const toastMessage =
      response && message && err.response?.data.response === response ? message : err.response?.data.error_message

    if (type && type === "WARN") addWarningToast(toastMessage)
    else addErrorToast(toastMessage)
  }
}
