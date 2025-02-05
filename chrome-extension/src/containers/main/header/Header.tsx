import { useRecoilState } from "recoil"
import { FaAngleLeft } from "react-icons/fa6"
import Profile from "@/containers/main/header/profile/Profile"
import viewState from "@/states/viewState"
import Logo from "@/svgs/logo.svg?react"

export default function Header() {
  const [view, setView] = useRecoilState(viewState)

  return (
    <>
      <header className="fixed top-0 left-0 z-30 flex w-full h-[70px] items-center justify-between px-8 bg-background">
        <span className="text-4xl w-16 flex items-center">
          {view.type === "home" ? (
            <Logo width={28} height={28} />
          ) : (
            <button type="button" aria-label="back" onClick={() => setView({ type: "home" })}>
              <FaAngleLeft />
            </button>
          )}
        </span>
        <h1 className="text-xl font-GmarketSansMedium">
          {view.type === "home" && "Daily Reports"}
          {view.type === "report" && "Report"}
        </h1>
        <div className="w-16 h-full flex justify-end">
          <Profile />
        </div>
      </header>
      <div className="h-[70px]" />
    </>
  )
}
