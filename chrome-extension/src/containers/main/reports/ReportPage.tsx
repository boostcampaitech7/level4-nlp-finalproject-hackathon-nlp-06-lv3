import { useRecoilValue } from "recoil"
import ReportTitle from "@/containers/main/reports/ReportTitle"
import viewState from "@/states/viewState"

export default function ReportPage() {
  const view = useRecoilValue(viewState)
  const report = view.data
  return (
    <div className="flex flex-col w-full bg-white rounded-lg p-6 gap-2 min-h-[170px] border border-border-gray shadow">
      <ReportTitle dateString={report.date} />
      <p className="text-text-gray">{report.content}</p>
    </div>
  )
}
