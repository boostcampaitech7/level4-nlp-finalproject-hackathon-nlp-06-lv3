import { useSetRecoilState } from "recoil"
import { useEffect, useState } from "react"
import viewState from "@/states/viewState"
import ReportTitle from "@/containers/main/reports/ReportTitle"

export default function ReportBox({ report }: { report: any }) {
  const setView = useSetRecoilState(viewState)

  const [isCompleted, setIsCompleted] = useState(false)
  const [descriptions, setDescriptions] = useState<string[]>([])

  useEffect(() => {
    const descriptionTemps: string[] = []
    let isCompletedTemp = true
    JSON.parse(report.content).forEach((category: any) => {
      category.task_objects.forEach((task: any) => {
        task.items.forEach((item: any) => {
          descriptionTemps.push(item.description)
          if (!item.checked) {
            isCompletedTemp = false
          }
        })
      })
      setIsCompleted(isCompletedTemp)
      setDescriptions(descriptionTemps.slice(0, 3))
    })
  }, [report])

  return (
    <button
      type="button"
      className="flex flex-col w-full bg-white rounded-lg p-6 gap-2 h-[170px] border border-border-gray drop-shadow-small hover:bg-gray-100 hover:drop-shadow-main transition-all group justify-start"
      onClick={() => setView({ type: "report", data: report })}
    >
      <ReportTitle dateString={report.date} />
      <div className="flex flex-col items-start overflow-hidden w-full">
        {descriptions.map((description) => (
          <p
            key={description}
            className={`text-start text-ellipsis line-clamp-1 text-[#5A5A5A] break-all ${isCompleted ? "line-through" : ""}`}
          >
            {description}
          </p>
        ))}
      </div>
    </button>
  )
}
