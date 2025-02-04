import { useSetRecoilState } from "recoil"
import React from "react"
import modalState from "@/states/modalState"
import { ModalData } from "@/types/modal"

export default function useModal() {
  const setModalList = useSetRecoilState(modalState)

  const openModal = (body: React.ReactNode) => {
    const id = Date.now()
    setModalList((prev) => [
      ...prev,
      {
        id,
        body,
      },
    ])
    return id
  }
  const onCloseModal = () => {
    setModalList((prev: ModalData[]) => {
      return prev.slice(0, prev.length - 1)
    })
  }

  const onCloseModalWithId = (id: number) => {
    setModalList((prev: ModalData[]) => {
      return prev.filter((item) => item.id !== id)
    })
  }

  return { openModal, onCloseModal, onCloseModalWithId }
}
