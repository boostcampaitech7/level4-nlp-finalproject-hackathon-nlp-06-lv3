import { useSetRecoilState } from "recoil"
import viewState from "@/states/viewState"
import ReportTitle from "@/containers/main/reports/ReportTitle"

export default function ReportBox({ report }: { report: any }) {
  const setView = useSetRecoilState(viewState)
  const jsonReport = JSON.parse(report.content)
  return (
    <button
      type="button"
      className="flex flex-col w-full bg-white rounded-lg p-6 gap-2 h-[170px] border border-border-gray drop-shadow-small hover:bg-gray-100 hover:drop-shadow-main transition-all group justify-start"
      onClick={() => setView({ type: "report", data: report })}
    >
      <ReportTitle dateString={report.date} />
      <div className="flex flex-col items-start overflow-hidden w-full">
        {jsonReport.map((category: any) =>
          category.task_objects.map((task: any) =>
            task.items.map((item: any) => (
              <p key={item.description} className="text-start">
                {item.description}
              </p>
            )),
          ),
        )}
      </div>
    </button>
  )
}
