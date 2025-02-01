import { MdLogout } from "react-icons/md"
import { useSetRecoilState } from "recoil"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import useToast from "@/hooks/useToast"
import axiosInstance from "@/utils/axiosInstance"
import { userIdState } from "@/states/auth"
import viewState from "@/states/viewState"

export default function LogoutButton() {
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
      queryClient.invalidateQueries({ queryKey: ["/auth/is-login"] }).then()
      queryClient.invalidateQueries({ queryKey: ["/auth/google/profile"] }).then()
      setView({ type: "home" })
    },
  })
  return (
    <button className="w-full flex items-center justify-between" type="button" onClick={() => logoutMutate()}>
      <span>로그아웃</span>
      <span className="text-xl">
        <MdLogout />
      </span>
    </button>
  )
}
