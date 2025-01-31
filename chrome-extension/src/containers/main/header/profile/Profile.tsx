import { useState } from "react"
import useUserInfoQuery from "@/hooks/useUserInfoQuery"
import ProfileInfoBox from "@/containers/main/header/profile/ProfileInfoBox"

export default function Profile() {
  const { userInfo } = useUserInfoQuery()
  const [isOpenInfoBox, setIsOpenInfoBox] = useState(false)

  return (
    <div className="relative">
      <button type="button" onClick={() => setIsOpenInfoBox(!isOpenInfoBox)}>
        <img src={userInfo.picture} alt="profile" className="rounded-full border border-gray-200 w-10 h-10" />
      </button>
      {isOpenInfoBox && <ProfileInfoBox />}
    </div>
  )
}
