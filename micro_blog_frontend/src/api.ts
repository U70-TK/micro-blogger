// Fallback to localhost:8000 for frontend dev when VITE_API_BASE is not set.
const envBase = (import.meta.env.VITE_API_BASE as string) || ''
export const BASE_URL = envBase || (typeof window !== 'undefined' && window.location.hostname === 'localhost' ? 'http://localhost:8000' : '')
