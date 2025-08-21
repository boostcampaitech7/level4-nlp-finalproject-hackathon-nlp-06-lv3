import { ModalData } from "@/types/modal"

interface Props {
  modalData: ModalData
  zIndex: number
}

function Modal({ modalData, zIndex = 100 }: Props) {
  return (
    <div
      style={{ zIndex }}
      className="fixed left-0 right-0 top-0 bottom-0 flex items-center justify-center bg-black/30"
    >
      <div className="m-8 bg-white border border-border-gray rounded-lg drop-shadow-main p-6">
        <section>{modalData.body}</section>
      </div>
    </div>
  )
}

export default Modal
