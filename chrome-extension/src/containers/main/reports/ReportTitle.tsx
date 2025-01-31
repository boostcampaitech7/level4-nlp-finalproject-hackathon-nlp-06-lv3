import moment from "moment/moment"

export default function ReportTitle({ dateString }: { dateString: string }) {
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
