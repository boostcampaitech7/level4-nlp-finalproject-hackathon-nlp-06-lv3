export default function useOpenLink() {
  return (url: string) => {
    chrome.tabs.create({
      url,
    })
  }
}
