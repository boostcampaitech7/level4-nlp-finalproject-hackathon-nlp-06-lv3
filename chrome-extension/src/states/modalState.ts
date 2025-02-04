import { atom } from "recoil"
import { ModalData } from "@/types/modal"

const modalState = atom<ModalData[]>({
  key: "modalState",
  default: [],
})

export default modalState
