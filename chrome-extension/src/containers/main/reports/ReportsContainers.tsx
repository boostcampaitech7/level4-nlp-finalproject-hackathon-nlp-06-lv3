import { useInfiniteQuery } from "@tanstack/react-query"
import axiosInstance from "@/utils/axiosInstance"

export default function ReportsContainers() {
  const { data, fetchNextPage, hasNextPage } = useInfiniteQuery({
    initialData: undefined,
    initialPageParam: 1,
    queryKey: ["/reports/temp"],
    queryFn: async ({ pageParam = 1 }) => {
      const params = { page: pageParam, limit: 1 }

      try {
        const res = await axiosInstance.get("/reports/temp", { params })
        return res.data.data
      } catch {
        return null
      }
    },
    getNextPageParam: (lastPage, _pages, pageNum) => {
      if (lastPage && lastPage.reports.length > 0) return pageNum + 1
      return undefined
    },
  })

  return (
    <>
      {data?.pages.map((page) => page?.reports.map((report: any) => <div key={report.id}>{report.content}</div>))}
      {hasNextPage && (
        <button type="button" onClick={() => fetchNextPage()}>
          더보기
        </button>
      )}
    </>
  )
}
