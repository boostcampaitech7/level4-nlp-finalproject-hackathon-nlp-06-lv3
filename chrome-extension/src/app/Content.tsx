import { useEffect } from "react"
import { useRecoilValue, useSetRecoilState } from "recoil"
import { isLoginState, userIdState } from "@/states/auth"
import useUserLoginInfoQuery from "@/hooks/useUserLoginInfoQuery"
import Main from "@/containers/main/Main"
import LoginPage from "@/containers/auth/LoginPage"

export default function Content() {
  const setUserId = useSetRecoilState(userIdState)
  const isLogin = useRecoilValue(isLoginState)
  const { userLoginInfo } = useUserLoginInfoQuery()

  useEffect(() => {
    if (!userLoginInfo.is_login) return
    setUserId(userLoginInfo.user_id)
  }, [userLoginInfo])

  return isLogin ? <Main /> : <LoginPage />
}
