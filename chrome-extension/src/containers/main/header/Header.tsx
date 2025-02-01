import { TbBrandGmail } from "react-icons/tb"
import { useEffect, useState } from "react"
import { useRecoilState } from "recoil"
import { FaAngleLeft } from "react-icons/fa6"
import Profile from "@/containers/main/header/profile/Profile"
import viewState from "@/states/viewState"

export default function Header() {
  const [isScrolled, setIsScrolled] = useState(false)

  const [view, setView] = useRecoilState(viewState)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50)
    }

    window.addEventListener("scroll", handleScroll)
    return () => {
      window.removeEventListener("scroll", handleScroll)
    }
  }, [])

  return (
    <>
      <header
        className={
          `fixed top-0 left-0 z-[500] flex w-full items-center justify-between px-8 bg-white ` +
          `border border-b-border-gray shadow transition-all ${isScrolled ? "h-[50px]" : "h-[100px]"}`
        }
      >
        <span className="text-4xl w-16">
          {view.type === "home" ? (
            <TbBrandGmail />
          ) : (
            <button type="button" onClick={() => setView({ type: "home" })}>
              <FaAngleLeft />
            </button>
          )}
        </span>
        <h1 className="text-lg font-GmarketSansMedium">{view.type === "home" && "Daily Report"}</h1>
        <div className="w-16 h-full flex justify-end">
          <Profile />
        </div>
      </header>
      <div className="h-[100px]" />
    </>
  )
}
