import { useSetRecoilState } from "recoil"
import { useMutation } from "@tanstack/react-query"
import { FcGoogle } from "react-icons/fc"
import axiosInstance from "@/utils/axiosInstance"
import { userIdState } from "@/states/auth"
import useToast from "@/hooks/useToast"

export default function GoogleLoginBtn() {
  const setUserId = useSetRecoilState(userIdState)
  const { addSuccessToast, addErrorToast } = useToast()

  const { mutate: oAuthMutate } = useMutation({
    mutationFn: (data: any) => {
      return axiosInstance.post("/auth/google", data)
    },
    onSuccess: (data) => {
      setUserId(data.data.user_id)
      addSuccessToast("환영합니다!")
    },
  })

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
      const uri = new URL(redirectedUri)
      const code = uri.searchParams.get("code")
      oAuthMutate({ code, redirect_uri: redirectUri })
    })
  }

  return (
    <button
      type="button"
      className="w-full h-10 flex justify-center items-center gap-2 rounded-lg bg-main-theme text-white hover:brightness-110 transition-all"
      onClick={() => googleLogin()}
    >
      <FcGoogle />
      <span>Continue with Google</span>
    </button>
  )
}
