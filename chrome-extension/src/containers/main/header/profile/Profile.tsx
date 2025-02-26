import { useEffect, useRef, useState } from "react"
import useUserInfoQuery from "@/hooks/useUserInfoQuery"
import ProfileInfoBox from "@/containers/main/header/profile/ProfileInfoBox"

export default function Profile() {
  const { userInfo } = useUserInfoQuery()
  const [isOpenInfoBox, setIsOpenInfoBox] = useState(false)

  const openedRef = useRef<HTMLDivElement>(null)
  const buttonRef = useRef<HTMLButtonElement>(null)

  const handleClickOutside = (event: MouseEvent) => {
    if (openedRef.current && !openedRef.current.contains(event.target as Node)) {
      if (buttonRef.current && !buttonRef.current.contains(event.target as Node)) setIsOpenInfoBox(false)
    }
  }

  useEffect(() => {
    if (isOpenInfoBox) {
      document.addEventListener("mousedown", handleClickOutside)
    } else {
      document.removeEventListener("mousedown", handleClickOutside)
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [isOpenInfoBox])

  return (
    <div className="flex flex-col h-full">
      <button type="button" ref={buttonRef} className="flex-1" onClick={() => setIsOpenInfoBox(!isOpenInfoBox)}>
        <img src={userInfo.picture} alt="profile" className="rounded-full border border-border-gray w-10 h-10" />
      </button>
      {isOpenInfoBox && (
        <div ref={openedRef} className="relative">
          <ProfileInfoBox onCloseClick={() => setIsOpenInfoBox(false)} />
        </div>
      )}
    </div>
  )
}
