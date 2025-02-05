import { useRecoilValue } from "recoil"
import { useEffect } from "react"
import Header from "@/containers/main/header/Header"
import ReportsContainers from "@/containers/main/reports/ReportsContainers"
import viewState from "@/states/viewState"
import ReportPage from "@/containers/main/reports/ReportPage"
import useModal from "@/hooks/useModal"
import UpdateAPIKeyForm from "@/containers/main/header/profile/UpdateAPIKeyForm"
import useUserInfoQuery from "@/hooks/useUserInfoQuery"

export default function Main() {
  const view = useRecoilValue(viewState)
  const { openModal, onCloseModal, onCloseModalWithId } = useModal()
  const { userInfo } = useUserInfoQuery()

  useEffect(() => {
    window.scrollTo({ top: 0 })
  }, [view])

  useEffect(() => {
    if (!userInfo.upstage_api_key || userInfo.upstage_api_key === "") {
      const modalId = openModal(<UpdateAPIKeyForm onSubmit={onCloseModal} />)
      return () => onCloseModalWithId(modalId)
    }
    return () => {}
  }, [])

  return (
    <div className="flex flex-col justify-center w-full">
      <Header />
      <div className="px-[14px] py-[5px]">
        {view.type === "home" && <ReportsContainers />}
        {view.type === "report" && <ReportPage />}
      </div>
    </div>
  )
}
