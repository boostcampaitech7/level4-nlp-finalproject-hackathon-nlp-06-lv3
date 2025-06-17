import moment from "moment"

// eslint-disable-next-line import/prefer-default-export
export function convertDateToTitle(dateString: string) {
  const date = moment(dateString)
  const today = moment().startOf("day")
  const yesterday = moment().subtract(1, "days").startOf("day")

  if (date.isSame(today)) {
    return "오늘"
  }
  if (date.isSame(yesterday)) {
    return "어제"
  }
  return date.format("MM/DD")
}
