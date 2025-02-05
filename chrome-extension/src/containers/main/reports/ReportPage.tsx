import { useRecoilValue } from "recoil"
import Markdown from "react-markdown"
import remarkGfm from "remark-gfm"
import ReportTitle from "@/containers/main/reports/ReportTitle"
import viewState from "@/states/viewState"

export default function ReportPage() {
  const view = useRecoilValue(viewState)
  const report = view.data
  return (
    <div className="flex flex-col w-full bg-white rounded-lg p-6 gap-2 min-h-[170px] border border-border-gray drop-shadow-small">
      <ReportTitle dateString={report.date} />
      <Markdown className="text-text-gray markdown-container -mt-3" remarkPlugins={[remarkGfm]}>
        {report.content}
      </Markdown>
    </div>
  )
}
