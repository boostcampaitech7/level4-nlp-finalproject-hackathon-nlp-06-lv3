import { useSetRecoilState } from "recoil"
import viewState from "@/states/viewState"
import ReportTitle from "@/containers/main/reports/ReportTitle"

export default function ReportBox({ report }: { report: any }) {
  const setView = useSetRecoilState(viewState)

  const descriptions: string[] = []

  JSON.parse(report.content).forEach((category: any) => {
    category.task_objects.forEach((task: any) => {
      task.items.forEach((item: any) => {
        descriptions.push(item.description)
      })
    })
  })

  return (
    <button
      type="button"
      className="flex flex-col w-full bg-white rounded-lg p-6 gap-2 h-[170px] border border-border-gray drop-shadow-small hover:bg-gray-100 hover:drop-shadow-main transition-all group justify-start"
      onClick={() => setView({ type: "report", data: report })}
    >
      <ReportTitle dateString={report.date} />
      <div className="flex flex-col items-start overflow-hidden w-full">
        {descriptions.slice(0, 3).map((description) => (
          <p key={description} className="text-start text-ellipsis line-clamp-1 text-[#5A5A5A]">
            {description}
          </p>
        ))}
      </div>
    </button>
  )
}
