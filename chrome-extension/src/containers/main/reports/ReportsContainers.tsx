import { useInfiniteQuery } from "@tanstack/react-query"
import { useCallback } from "react"
import axiosInstance from "@/utils/axiosInstance"
import ReportBox from "@/containers/main/reports/ReportBox"
import useIntersectionObserver from "@/hooks/useIntersectionObserver"

export default function ReportsContainers() {
  const { data, fetchNextPage, hasNextPage } = useInfiniteQuery({
    initialData: undefined,
    initialPageParam: 1,
    queryKey: ["/reports/temp"],
    queryFn: async ({ pageParam = 1 }) => {
      const params = { page: pageParam, limit: 20 }

      try {
        const res = await axiosInstance.get("/reports/temp", { params })
        return res.data.response
      } catch {
        return null
      }
    },
    getNextPageParam: (lastPage, _pages, pageNum) => {
      if (lastPage && lastPage.reports.length > 0) return pageNum + 1
      return undefined
    },
  })

  const handleIntersect = useCallback(
    async ([entry]: IntersectionObserverEntry[], observer: IntersectionObserver) => {
      if (entry.isIntersecting) {
        observer.unobserve(entry.target)
        if (hasNextPage) {
          await fetchNextPage()
          observer.observe(entry.target)
        }
      }
    },
    [hasNextPage, fetchNextPage],
  )

  const { targetRef } = useIntersectionObserver(handleIntersect)
  return (
    <div className="flex flex-col gap-[10px]">
      {data?.pages.map((page) => page?.reports.map((report: any) => <ReportBox key={report.id} report={report} />))}
      {hasNextPage && <div ref={targetRef} />}
    </div>
  )
}
