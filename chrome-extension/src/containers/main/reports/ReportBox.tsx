import { useSetRecoilState } from "recoil"
import remarkGfm from "remark-gfm"
import Markdown from "react-markdown"
import viewState from "@/states/viewState"
import ReportTitle from "@/containers/main/reports/ReportTitle"

export default function ReportBox({ report }: { report: any }) {
  const setView = useSetRecoilState(viewState)
  return (
    <button
      type="button"
      className="flex flex-col w-full bg-white rounded-lg px-6 pt-6 gap-2 h-[170px] border border-border-gray shadow hover:brightness-[.97] hover:drop-shadow-lg transition-all overflow-hidden group"
      onClick={() => setView({ type: "report", data: report })}
    >
      <ReportTitle dateString={report.date} />
      <Markdown
        className="text-left text-text-gray line-clamp-3 text-ellipsis markdown-container"
        remarkPlugins={[remarkGfm]}
      >
        {report.content}
      </Markdown>
      <div className="flex flex-1 justify-end items-end w-full pt-1 pb-3">
        <span className="text-xs text-text-gray group-hover:text-black">자세히 보기</span>
      </div>
    </button>
  )
}
