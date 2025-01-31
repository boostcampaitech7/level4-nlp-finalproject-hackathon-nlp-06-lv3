import { atom } from "recoil"
import { ViewData } from "@/types/view"

const viewState = atom<ViewData>({
  key: "viewState",
  default: { type: "home" },
})

export default viewState
