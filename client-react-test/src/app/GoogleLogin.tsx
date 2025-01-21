import { useGoogleLogin } from "@react-oauth/google"
import axios from "axios"

export default function GoogleLoginBtn({ setUserId }: { setUserId: (userId: number) => void }) {
  const googleLogin = useGoogleLogin({
    flow: "auth-code",
    onSuccess: async (codeResponse) => {
      const { code } = codeResponse
      const redirectUri = "http://localhost:3000"
      axios.post("http://localhost:8000/auth/google", { code, redirect_uri: redirectUri }).then((res) => {
        setUserId(res.data.user_id)
      })
    },
    onError: (errorResponse) => console.log(errorResponse),
    scope: "https://www.googleapis.com/auth/gmail.readonly",
  })
  return (
    <button type="button" onClick={() => googleLogin()}>
      <span>Continue with Google</span>
    </button>
  )
}
