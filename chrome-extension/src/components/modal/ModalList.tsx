import { useRecoilValue } from "recoil"
import modalState from "@/states/modalState"
import { ModalData } from "@/types/modal"
import Modal from "@/components/modal/Modal"

export default function ModalList() {
  const modalList = useRecoilValue(modalState)

  return modalList.map((item: ModalData, idx) => <Modal key={item.id} zIndex={idx + 100} modalData={item} />)
}
