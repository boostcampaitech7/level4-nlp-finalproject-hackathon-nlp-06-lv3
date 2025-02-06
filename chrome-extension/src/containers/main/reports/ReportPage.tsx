import { useRecoilValue } from "recoil"
import ReportTitle from "@/containers/main/reports/ReportTitle"
import viewState from "@/states/viewState"

export default function ReportPage() {
  const view = useRecoilValue(viewState)
  const report = view.data
  const jsonReport = JSON.parse(report.content)

  return (
    <div className="flex flex-col w-full bg-white rounded-lg p-6 gap-2 min-h-[170px] border border-border-gray drop-shadow-small">
      <ReportTitle dateString={report.date} />

      {jsonReport.map((category: any) => (
        <div key={category.title}>
          <h3>{category.title}</h3>
          {category.task_objects.map((task: any) => (
            <div key={task.title}>
              <h4>{task.title}</h4>
              {task.items.map((item: any) => (
                <div key={item.description}>
                  <p>{item.description}</p>
                  <ul>
                    {item.links.map((link: any) => (
                      <li key={link}>{link}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}
