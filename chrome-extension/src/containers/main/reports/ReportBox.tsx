import moment from "moment"

function ReportTitle({ dateString }: { dateString: string }) {
  const date = moment(dateString)
  const today = moment().startOf("day")
  const yesterday = moment().subtract(1, "days").startOf("day")

  if (date.isSame(today)) {
    return <h2 className="text-2xl font-bold">오늘</h2>
  }
  if (date.isSame(yesterday)) {
    return <h2 className="text-2xl font-bold">어제</h2>
  }
  return <h2 className="text-2xl font-bold">{date.format("MM/DD")}</h2>
}

export default function ReportBox({ report }: { report: any }) {
  return (
    <div className="flex flex-col w-full bg-white rounded-lg p-6 gap-2 min-h-[170px] border border-border-gray">
      <ReportTitle dateString={report.date} />
      <p className="text-text-gray">{report.content}</p>
    </div>
  )
}
