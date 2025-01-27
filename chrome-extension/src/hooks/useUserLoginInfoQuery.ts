import { useSuspenseQuery } from "@tanstack/react-query"
import axiosInstance from "@/utils/axiosInstance"

export default function useUserLoginInfoQuery() {
  const { data, isFetched } = useSuspenseQuery({
    queryKey: ["/auth/is-login"],
    queryFn: async () => {
      return axiosInstance.get("/auth/is-login").then((res) => res.data.data)
    },
    staleTime: 300_000,
  })
  return { userLoginInfo: data, isFetched }
}
