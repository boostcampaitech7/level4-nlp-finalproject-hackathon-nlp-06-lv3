import useUserInfoQuery from "@/hooks/useUserInfoQuery"
import LogoutButton from "@/containers/main/header/profile/LogoutButton"
import useModal from "@/hooks/useModal"
import UpdateAPIKeyForm from "@/containers/main/header/profile/UpdateAPIKeyForm"

export default function ProfileInfoBox({ onCloseClick }: { onCloseClick: () => void }) {
  const { userInfo } = useUserInfoQuery()

  const { openModal, onCloseModal } = useModal()

  return (
    <div className="absolute top-0 -right-3 bg-white drop-shadow-main border border-border-gray rounded-lg py-2 min-w-[170px]">
      <div className="w-full flex flex-col justify-center text-text-gray px-6 py-2">
        <p>{userInfo.name}</p>
        <p className="text-xs">{userInfo.email}</p>
      </div>
      <hr />
      <button
        className="w-full h-12 flex items-center bg-white hover:bg-gray-100 px-6 transition-all"
        type="button"
        onClick={() => {
          openModal(<UpdateAPIKeyForm onSubmit={onCloseModal} />)
          onCloseClick()
        }}
      >
        <p>API key 변경</p>
      </button>
      <div className="px-6">
        <hr />
      </div>
      <LogoutButton onCloseClick={onCloseClick} />
    </div>
  )
}
