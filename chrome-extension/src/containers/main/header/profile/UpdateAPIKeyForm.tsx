import { useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import useOpenLink from "@/hooks/useOpenLink"
import useUserInfoQuery from "@/hooks/useUserInfoQuery"
import axiosInstance from "@/utils/axiosInstance"
import useToast from "@/hooks/useToast"
import useErrorResponseHandler from "@/hooks/useErrorResponseHandler"

export default function UpdateAPIKeyForm({ onSubmit }: { onSubmit: () => void }) {
  const { addSuccessToast, addWarningToast } = useToast()
  const openLink = useOpenLink()

  const { userInfo } = useUserInfoQuery()
  const queryClient = useQueryClient()
  const errorHandler = useErrorResponseHandler()

  const [upstageApiKey, setUpstageApiKey] = useState<string>(userInfo.upstage_api_key)

  const { mutate } = useMutation({
    mutationFn: (data: any) => axiosInstance.put("/auth/profile", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/auth/google/profile"] }).then()
      addSuccessToast("API Key가 저장되었습니다.")
    },
    onError: (err) => errorHandler(err),
  })

  return (
    <form
      className="flex flex-col gap-4 pt-[90px]"
      onSubmit={(e) => {
        e.preventDefault()
        if (!upstageApiKey || upstageApiKey === "") {
          addWarningToast("API Key를 입력해주세요.")
          return
        }
        mutate({ upstage_api_key: upstageApiKey })
        onSubmit()
      }}
    >
      <div className="flex flex-col gap-9">
        <p>
          Upstage{" "}
          <button
            type="button"
            className="text-blue-600 hover:text-blue-800"
            onClick={() => openLink("https://console.upstage.ai/api-keys")}
          >
            API Key
          </button>
          를 입력하세요.
        </p>
        <input
          className="w-full h-10 p-2 rounded-lg border border-border-gray text-text-gray focus:bg-gray-50"
          placeholder="Key 입력"
          value={upstageApiKey || ""}
          onChange={(e) => setUpstageApiKey(e.target.value)}
          onBlur={() => {
            const trimKey = upstageApiKey.replaceAll(" ", "")
            setUpstageApiKey(trimKey === "" ? userInfo.upstage_api_key : trimKey)
          }}
        />
      </div>
      <button type="submit" className="w-full h-10 rounded-lg bg-main-theme text-white">
        확인
      </button>
    </form>
  )
}
