import { TbBrandGmail } from "react-icons/tb"
import Profile from "@/containers/main/header/profile/Profile"

export default function Header() {
  return (
    <header className="h-[100px] flex w-full items-center justify-between px-8 bg-white border border-b-gray-300">
      <span className="text-4xl w-16">
        <TbBrandGmail />
      </span>
      <h1 className="text-xl">Daily Report</h1>
      <div className="w-16 flex justify-end">
        <Profile />
      </div>
    </header>
  )
}
