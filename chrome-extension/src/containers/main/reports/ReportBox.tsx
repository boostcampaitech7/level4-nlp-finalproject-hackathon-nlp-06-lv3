import { useSetRecoilState } from "recoil"
import viewState from "@/states/viewState"
import ReportTitle from "@/containers/main/reports/ReportTitle"

export default function ReportBox({ report }: { report: any }) {
  const setView = useSetRecoilState(viewState)
  return (
    <button
      type="button"
      className="flex flex-col w-full bg-white rounded-lg p-6 gap-2 min-h-[170px] border border-border-gray shadow hover:brightness-[.97] hover:drop-shadow-lg transition-all"
      onClick={() => setView({ type: "report", data: report })}
    >
      <ReportTitle dateString={report.date} />
      <p className="text-text-gray">{report.content}</p>
    </button>
  )
}
