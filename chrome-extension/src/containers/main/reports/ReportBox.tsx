import { useSetRecoilState } from "recoil"
import viewState from "@/states/viewState"
import ReportTitle from "@/containers/main/reports/ReportTitle"

export default function ReportBox({ report }: { report: any }) {
  const setView = useSetRecoilState(viewState)
  return (
    <button
      type="button"
      className="flex flex-col w-full bg-white rounded-lg p-6 gap-2 h-[170px] border border-border-gray drop-shadow-small hover:bg-gray-100 hover:drop-shadow-main transition-all group"
      onClick={() => setView({ type: "report", data: report })}
    >
      <ReportTitle dateString={report.date} />
      <div className="overflow-hidden w-full">
        <p className="text-left text-text-gray line-clamp-3 overflow-hidden text-ellipsis whitespace-pre-wrap">
          {report.content}
        </p>
      </div>
    </button>
  )
}
