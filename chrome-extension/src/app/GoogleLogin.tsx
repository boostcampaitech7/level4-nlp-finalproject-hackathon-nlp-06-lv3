import axios from "axios"

export default function GoogleLoginBtn({ setUserId }: { setUserId: (userId: number) => void }) {
  const googleLogin = () => {
    const redirectUri = chrome.identity.getRedirectURL()
    const url =
      "https://accounts.google.com/o/oauth2/v2/auth" +
      "?scope=openid%20https://www.googleapis.com/auth/gmail.readonly%20https://www.googleapis.com/auth/userinfo.email%20https://www.googleapis.com/auth/userinfo.profile" +
      "&access_type=offline" +
      "&response_type=code" +
      "&prompt=consent" +
      "&state=state_parameter_passthrough_value" +
      `&redirect_uri=${redirectUri}` +
      "&client_id=814835238278-fesn4cl6798n00p2ljbtlnsqbk9bfbj8.apps.googleusercontent.com"

    chrome.identity.launchWebAuthFlow({ interactive: true, url }, async (redirectedUri) => {
      if (chrome.runtime.lastError || !redirectedUri) {
        return
      }
      const uri = new URL(redirectedUri!)
      const code = uri.searchParams.get("code")
      axios.post("http://localhost:8000/auth/google", { code, redirect_uri: redirectUri }).then((res) => {
        setUserId(res.data.user_id)
      })
    })
  }

  return (
    <button type="button" onClick={() => googleLogin()}>
      <span>Continue with Google</span>
    </button>
  )
}
