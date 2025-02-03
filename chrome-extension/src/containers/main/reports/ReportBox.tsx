import { useSetRecoilState } from "recoil"
import viewState from "@/states/viewState"
import ReportTitle from "@/containers/main/reports/ReportTitle"

export default function ReportBox({ report }: { report: any }) {
  const setView = useSetRecoilState(viewState)
  return (
    <button
      type="button"
      className="flex flex-col w-full bg-white rounded-lg px-6 py-6 gap-2 h-[170px] border border-border-gray shadow hover:brightness-[.97] hover:drop-shadow-lg transition-all overflow-hidden group"
      onClick={() => setView({ type: "report", data: report })}
    >
      <ReportTitle dateString={report.date} />
      <p className="text-left text-text-gray line-clamp-3 text-ellipsis whitespace-pre-wrap">{report.content}</p>
    </button>
  )
}
