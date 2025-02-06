import { useRecoilValue } from "recoil"
import { useEffect, useState } from "react"
import { useMutation } from "@tanstack/react-query"
import ReportTitle from "@/containers/main/reports/ReportTitle"
import viewState from "@/states/viewState"
import useOpenLink from "@/hooks/useOpenLink"
import axiosInstance from "@/utils/axiosInstance"
import useErrorResponseHandler from "@/hooks/useErrorResponseHandler"

export default function ReportPage() {
  const view = useRecoilValue(viewState)
  const report = view.data
  const openLink = useOpenLink()
  const errorHandler = useErrorResponseHandler()

  const [jsonReport, setJsonReport] = useState(JSON.parse(report.content))

  // 체크박스 상태 변경 핸들러
  const onCheckChange = (description: string, checked: boolean) => {
    const updatedReport = jsonReport.map((category: any) => ({
      ...category,
      task_objects: category.task_objects.map((task: any) => ({
        ...task,
        items: task.items.map((item: any) => (item.description === description ? { ...item, checked } : item)),
      })),
    }))
    setJsonReport(updatedReport)
  }

  const { mutate } = useMutation({
    mutationFn: (data: any) => {
      return axiosInstance.put(`/reports/temp/${report.id}`, data)
    },
    onError: (err) => errorHandler(err),
  })

  useEffect(() => {
    mutate({ content: JSON.stringify(jsonReport) })
  }, [jsonReport])

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
                  <div key={item.description} className="flex gap-2 items-start">
                    <div className="h-full">
                      <div>
                        <input
                          type="checkbox"
                          checked={item.checked}
                          onChange={(e) => onCheckChange(item.description, e.target.checked)}
                        />
                      </div>
                    </div>
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
