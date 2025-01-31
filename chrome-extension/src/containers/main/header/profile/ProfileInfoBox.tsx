import { useSetRecoilState } from "recoil"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { MdLogout } from "react-icons/md"
import axiosInstance from "@/utils/axiosInstance"
import { userIdState } from "@/states/auth"
import useToast from "@/hooks/useToast"
import useUserInfoQuery from "@/hooks/useUserInfoQuery"

function ProfileInfoBox() {
  const setUserId = useSetRecoilState(userIdState)
  const { userInfo } = useUserInfoQuery()
  const { addSuccessToast } = useToast()

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
    },
  })

  return (
    <div className="absolute top-20 right-0 bg-white drop-shadow-lg border border-gray-300 rounded-lg px-6 py-4 min-w-[170px]">
      <div className="w-full flex flex-col justify-center text-text-gray">
        <p>{userInfo.name}</p>
        <p className="text-xs">{userInfo.email}</p>
      </div>
      <hr className="my-2" />
      <button className="w-full flex items-center justify-between" type="button" onClick={() => logoutMutate()}>
        <span>로그아웃</span>
        <span className="text-xl">
          <MdLogout />
        </span>
      </button>
    </div>
  )
}

export default ProfileInfoBox
