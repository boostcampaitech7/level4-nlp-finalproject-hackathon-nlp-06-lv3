import { atom, selector } from "recoil"

export const userIdState = atom({
  key: "userIdState",
  default: 0,
})

export const isLoginState = selector({
  key: "isLoginState",
  get: ({ get }) => {
    return get(userIdState) !== 0
  },
})
