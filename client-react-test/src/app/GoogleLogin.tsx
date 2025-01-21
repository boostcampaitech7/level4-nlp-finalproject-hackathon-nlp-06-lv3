import { useGoogleLogin } from "@react-oauth/google"

export default function GoogleLoginBtn() {
  const googleLogin = useGoogleLogin({
    flow: "auth-code",
    onSuccess: async (codeResponse) => {
      console.log(codeResponse)
      console.log(codeResponse.code)
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
