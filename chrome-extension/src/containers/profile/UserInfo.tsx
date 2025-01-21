import { useEffect, useState } from "react"
import { useSetRecoilState } from "recoil"
import axiosInstance from "@/utils/axiosInstance.ts"
import { userIdState } from "@/states/auth.ts"
import useToast from "@/hooks/useToast.ts"

function UserInfo() {
  const setUserId = useSetRecoilState(userIdState)
  const [userProfile, setUserProfile] = useState<any>(null)
  const { addSuccessToast } = useToast()

  const onClickLogout = () => {
    axiosInstance.post("/auth/logout").then(() => {
      setUserId(0)
      addSuccessToast("로그아웃 되었습니다.")
    })
  }
  useEffect(() => {
    axiosInstance.get("/auth/google/profile").then((res) => {
      setUserProfile(res.data)
    })
  }, [setUserProfile])

  return (
    <div>
      {userProfile && (
        <>
          <p>{userProfile.name}</p>
          <p>{userProfile.email}</p>
          <img src={userProfile.picture} alt="profile" />
        </>
      )}
      <button type="button" onClick={onClickLogout}>
        로그아웃
      </button>
    </div>
  )
}

export default UserInfo
