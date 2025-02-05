import GoogleLoginBtn from "@/containers/auth/GoogleLogin"
import Logo from "@/svgs/logo.svg?react"

export default function LoginPage() {
  return (
    <div className="h-screen w-full flex justify-center items-center px-8">
      <div className="h-[300px] w-full bg-white rounded-lg border border-border-gray shadow flex flex-col items-center p-6">
        <div className="flex-1 flex flex-col gap-2 justify-center items-center">
          <Logo />
          <h1 className="text-lg font-GmarketSansMedium">매일메일</h1>
        </div>
        <GoogleLoginBtn />
      </div>
    </div>
  )
}
