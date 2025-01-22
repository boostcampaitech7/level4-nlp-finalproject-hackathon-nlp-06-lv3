import { useSetRecoilState } from "recoil"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import axiosInstance from "@/utils/axiosInstance.ts"
import { userIdState } from "@/states/auth.ts"
import useToast from "@/hooks/useToast.ts"
import useUserInfoQuery from "@/hooks/useUserInfoQuery.ts"

function UserInfo() {
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
    <div>
      <p>{userInfo.name}</p>
      <p>{userInfo.email}</p>
      <img src={userInfo.picture} alt="profile" />
      <button type="button" onClick={() => logoutMutate()}>
        로그아웃
      </button>
    </div>
  )
}

export default UserInfo
