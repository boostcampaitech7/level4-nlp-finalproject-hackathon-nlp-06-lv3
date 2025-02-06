import { useRecoilValue } from "recoil"
import ReportTitle from "@/containers/main/reports/ReportTitle"
import viewState from "@/states/viewState"
import useOpenLink from "@/hooks/useOpenLink"

export default function ReportPage() {
  const view = useRecoilValue(viewState)
  const report = view.data
  const jsonReport = JSON.parse(report.content)
  const openLink = useOpenLink()

  return (
    <div className="flex flex-col w-full bg-white rounded-lg p-6 gap-3 min-h-[170px] border border-border-gray drop-shadow-small">
      <ReportTitle dateString={report.date} />
      <div className="flex flex-col gap-10">
        {jsonReport.map((category: any) => (
          <div key={category.title} className="flex flex-col gap-3">
            <h3 className="text-xl">{category.title}</h3>
            {category.task_objects.map((task: any) => (
              <div key={task.title} className="flex flex-col gap-3">
                <h4>{task.title}</h4>
                {task.items.map((item: any) => (
                  <div key={item.description}>
                    <p className="text-text-gray">
                      {item.description}
                      {item.links.map((link: any) => (
                        <button type="button" key={link} onClick={() => openLink(link)}>
                          🔗
                        </button>
                      ))}
                    </p>
                  </div>
                ))}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
