import axios from 'axios'

const MAX_RETRIES = 3
const RETRY_DELAY = 5000

export const fetchWithRetry = async (url: string, retries = 0): Promise<string> => {
  try {
    const { data } = await axios.get(url)
    return data
  } catch (error) {
    if (retries < MAX_RETRIES) {
      console.log(`Retry ${retries + 1} for URL: ${url}`)
      await delay(RETRY_DELAY)
      return await fetchWithRetry(url, retries + 1)
    } else {
      // throw error
      throw new Error(`Failed to fetch URL: ${url} after ${MAX_RETRIES} retries.`)
    }
  }
}

export const delay = async (ms: number): Promise<void> => await new Promise(resolve => setTimeout(resolve, ms))
