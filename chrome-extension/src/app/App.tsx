import { Suspense } from "react"
import { RecoilRoot } from "recoil"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import Content from "@/app/Content"
import Toast from "@/components/toast/Toast"

function App() {
  const queryClient = new QueryClient()

  return (
    <QueryClientProvider client={queryClient}>
      <RecoilRoot>
        <div className="flex flex-col w-full items-center">
          <Suspense fallback={<div>Loading...</div>}>
            <Content />
          </Suspense>
        </div>
        <Toast />
      </RecoilRoot>
    </QueryClientProvider>
  )
}

export default App
