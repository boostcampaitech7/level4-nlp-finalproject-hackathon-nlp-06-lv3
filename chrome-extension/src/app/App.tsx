import { Suspense } from "react"
import { RecoilRoot } from "recoil"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import Content from "@/app/Content"
import Toast from "@/components/toast/Toast"
import AxiosInterceptorWrapper from "@/wrappers/AxiosInterceptorWrapper"
import ModalList from "@/components/modal/ModalList"

export default function App() {
  const queryClient = new QueryClient()

  return (
    <QueryClientProvider client={queryClient}>
      <RecoilRoot>
        <AxiosInterceptorWrapper>
          <div className="flex flex-col w-full items-center">
            <Suspense
              fallback={
                <div className="flex w-full h-screen justify-center items-center">
                  <div className="loading-dots" />
                </div>
              }
            >
              <Content />
            </Suspense>
          </div>
          <Toast />
          <ModalList />
        </AxiosInterceptorWrapper>
      </RecoilRoot>
    </QueryClientProvider>
  )
}
