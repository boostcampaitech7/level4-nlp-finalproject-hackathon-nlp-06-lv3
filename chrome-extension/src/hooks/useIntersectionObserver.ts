import { useEffect, useRef } from "react"

function useIntersectionObserver(
  handleIntersect: ([entry]: IntersectionObserverEntry[], observer: IntersectionObserver) => void,
) {
  const targetRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const observer = new IntersectionObserver(handleIntersect)
    const target = targetRef.current
    if (target) {
      observer.observe(target)
    }
    return () => {
      return observer.disconnect()
    }
  }, [targetRef, handleIntersect])
  return { targetRef }
}

export default useIntersectionObserver
