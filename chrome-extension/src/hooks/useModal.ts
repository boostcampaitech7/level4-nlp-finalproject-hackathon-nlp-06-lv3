import { useSetRecoilState } from "recoil"
import React from "react"
import modalState from "@/states/modalState"
import { ModalData } from "@/types/modal"

export default function useModal() {
  const setModalList = useSetRecoilState(modalState)

  const openModal = (body: React.ReactNode) => {
    setModalList((prev) => [
      ...prev,
      {
        id: Date.now(),
        body,
      },
    ])
  }
  const onCloseModal = () => {
    setModalList((prev: ModalData[]) => {
      return prev.slice(0, prev.length - 1)
    })
  }

  return { openModal, onCloseModal }
}
