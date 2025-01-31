import useUserInfoQuery from "@/hooks/useUserInfoQuery"
import LogoutButton from "@/containers/main/header/profile/LogoutButton"

export default function ProfileInfoBox() {
  const { userInfo } = useUserInfoQuery()

  return (
    <div className="absolute top-20 right-0 bg-white drop-shadow-lg border border-border-gray rounded-lg px-6 py-4 min-w-[170px]">
      <div className="w-full flex flex-col justify-center text-text-gray">
        <p>{userInfo.name}</p>
        <p className="text-xs">{userInfo.email}</p>
      </div>
      <hr className="my-2" />
      <LogoutButton />
    </div>
  )
}
