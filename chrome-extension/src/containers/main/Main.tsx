import Header from "@/containers/main/header/Header"
import ReportsContainers from "@/containers/main/reports/ReportsContainers"

export default function Main() {
  return (
    <div className="flex flex-col justify-center w-full">
      <Header />
      <div>
        <ReportsContainers />
      </div>
    </div>
  )
}
