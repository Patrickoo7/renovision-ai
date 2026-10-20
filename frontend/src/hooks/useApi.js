import { useState, useCallback } from 'react'

export function useApi() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const call = useCallback(async (apiFunc, ...args) => {
    setLoading(true)
    setError(null)
    try {
      const res = await apiFunc(...args)
      return res.data
    } catch (err) {
      const msg = err.response?.data?.detail || err.message
      setError(msg)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const clearError = useCallback(() => setError(null), [])

  return { loading, error, call, clearError }
}
