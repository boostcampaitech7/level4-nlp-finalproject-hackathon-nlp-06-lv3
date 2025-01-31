import { TbBrandGmail } from "react-icons/tb"
import { useEffect, useState } from "react"
import Profile from "@/containers/main/header/profile/Profile"

export default function Header() {
  const [isScrolled, setIsScrolled] = useState(false)

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
          <TbBrandGmail />
        </span>
        <h1 className="text-xl">Daily Report</h1>
        <div className="w-16 flex justify-end">
          <Profile />
        </div>
      </header>
      <div className="h-[100px]" />
    </>
  )
}
