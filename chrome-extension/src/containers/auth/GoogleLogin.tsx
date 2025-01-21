import { useSetRecoilState } from "recoil"
import axiosInstance from "@/utils/axiosInstance.ts"
import { userIdState } from "@/states/auth.ts"
import useToast from "@/hooks/useToast.ts"

export default function GoogleLoginBtn() {
  const setUserId = useSetRecoilState(userIdState)
  const { addSuccessToast, addErrorToast } = useToast()

  const googleLogin = () => {
    const redirectUri = chrome.identity.getRedirectURL()

    const scope = [
      "openid",
      "https://www.googleapis.com/auth/gmail.readonly",
      "https://www.googleapis.com/auth/userinfo.email",
      "https://www.googleapis.com/auth/userinfo.profile",
    ]
    const url =
      "https://accounts.google.com/o/oauth2/v2/auth" +
      `?scope=${scope.join(" ")}` +
      "&access_type=offline" +
      "&response_type=code" +
      "&prompt=consent" +
      "&state=state_parameter_passthrough_value" +
      `&redirect_uri=${redirectUri}` +
      `&client_id=${import.meta.env.VITE_GOOGLE_CLIENT_ID}`

    chrome.identity.launchWebAuthFlow({ interactive: true, url }, async (redirectedUri) => {
      if (chrome.runtime.lastError || !redirectedUri) {
        addErrorToast("로그인에 실패했습니다.")
        return
      }
      const uri = new URL(redirectedUri!)
      const code = uri.searchParams.get("code")
      axiosInstance.post("/auth/google", { code, redirect_uri: redirectUri }).then((res) => {
        setUserId(res.data.user_id)
        addSuccessToast("환영합니다!")
      })
    })
  }

  return (
    <button type="button" onClick={() => googleLogin()}>
      <span>Continue with Google</span>
    </button>
  )
}
