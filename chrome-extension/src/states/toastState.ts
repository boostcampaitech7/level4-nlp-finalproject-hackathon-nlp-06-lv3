import { atom } from "recoil"
import { ToastData } from "@/types/toast"

const toastState = atom<ToastData[]>({
  key: "toastState",
  default: [],
})

export default toastState
