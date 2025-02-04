import useOpenLink from "@/hooks/useOpenLink"

export default function UpdateAPIKeyForm({ onSubmit }: { onSubmit: () => void }) {
  const openLink = useOpenLink()
  return (
    <form
      className="flex flex-col gap-4 pt-[98px]"
      onSubmit={(e) => {
        e.preventDefault()
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
        <input className="w-full h-10 p-2 rounded-lg border border-border-gray text-text-gray" placeholder="Key 입력" />
      </div>
      <button type="submit" className="w-full h-10 rounded-lg bg-main-theme text-white">
        확인
      </button>
    </form>
  )
}
