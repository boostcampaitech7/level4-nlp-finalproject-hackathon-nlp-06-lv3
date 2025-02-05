import useUserInfoQuery from "@/hooks/useUserInfoQuery"
import LogoutButton from "@/containers/main/header/profile/LogoutButton"
import useModal from "@/hooks/useModal"
import UpdateAPIKeyForm from "@/containers/main/header/profile/UpdateAPIKeyForm"

export default function ProfileInfoBox({ onCloseClick }: { onCloseClick: () => void }) {
  const { userInfo } = useUserInfoQuery()

  const { openModal, onCloseModal } = useModal()

  return (
    <div className="absolute top-5 right-0 bg-white drop-shadow-lg border border-border-gray rounded-lg py-4 min-w-[170px]">
      <div className="w-full flex flex-col justify-center text-text-gray px-6">
        <p>{userInfo.name}</p>
        <p className="text-xs">{userInfo.email}</p>
      </div>
      <hr className="my-2 px-6" />
      <button
        className="w-full h-9 flex items-center bg-white hover:bg-gray-50 px-6"
        type="button"
        onClick={() => {
          openModal(<UpdateAPIKeyForm onSubmit={onCloseModal} />)
          onCloseClick()
        }}
      >
        <p>API key 변경</p>
      </button>
      <div className="bg-white hover:bg-gray-50 px-6">
        <LogoutButton onCloseClick={onCloseClick} />
      </div>
    </div>
  )
}
