import { MdLogout } from "react-icons/md"
import { useSetRecoilState } from "recoil"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import useToast from "@/hooks/useToast"
import axiosInstance from "@/utils/axiosInstance"
import { userIdState } from "@/states/auth"
import viewState from "@/states/viewState"

export default function LogoutButton({ onCloseClick }: { onCloseClick: () => void }) {
  const setUserId = useSetRecoilState(userIdState)
  const { addSuccessToast } = useToast()
  const setView = useSetRecoilState(viewState)

  const queryClient = useQueryClient()

  const { mutate: logoutMutate } = useMutation({
    mutationFn: () => {
      return axiosInstance.post("/auth/logout")
    },
    onSuccess: () => {
      setUserId(0)
      addSuccessToast("로그아웃 되었습니다.")
      queryClient.clear()
      setView({ type: "home" })
    },
  })
  return (
    <button
      className="bg-white hover:bg-gray-100 px-6 w-full h-12 flex items-center justify-between transition-all"
      type="button"
      onClick={() => {
        logoutMutate()
        onCloseClick()
      }}
    >
      <span>로그아웃</span>
      <span className="text-xl font-bold">
        <MdLogout />
      </span>
    </button>
  )
}
