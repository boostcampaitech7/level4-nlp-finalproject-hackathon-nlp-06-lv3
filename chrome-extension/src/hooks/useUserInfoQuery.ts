import { useSuspenseQuery } from "@tanstack/react-query"
import axiosInstance from "@/utils/axiosInstance"

export default function useUserInfoQuery() {
  const { data, isFetched } = useSuspenseQuery({
    queryKey: ["/auth/google/profile"],
    queryFn: async () => {
      return axiosInstance.get("/auth/profile").then((res) => res.data.response)
    },
    staleTime: 300_000,
  })
  return { userInfo: data, isFetched }
}
