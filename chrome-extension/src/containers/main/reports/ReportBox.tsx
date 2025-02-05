import { useSetRecoilState } from "recoil"
import Markdown from "react-markdown"
import remarkGfm from "remark-gfm"
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
        <Markdown
          className="text-left text-text-gray markdown-container -mt-3 line-clamp-3 text-ellipsis flex flex-col"
          remarkPlugins={[remarkGfm]}
        >
          {report.content}
        </Markdown>
      </div>
    </button>
  )
}
