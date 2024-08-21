import axios from 'axios'

const MAX_RETRIES = 3
const RETRY_DELAY = 5000

export const fetchWithRetry = async (url: string, delay: number = RETRY_DELAY, retries = 0): Promise<string> => {
  try {
    const { data } = await axios.get(url)
    return data
  } catch (error) {
    if (retries < MAX_RETRIES) {
      console.log(`Retry ${retries + 1} for URL: ${url}`)
      await sleep(delay)
      return await fetchWithRetry(url, retries + 1)
    } else {
      // throw error
      throw new Error(`Failed to fetch URL: ${url} after ${MAX_RETRIES} retries.`)
    }
  }
}

export const sleep = async (ms: number): Promise<void> => await new Promise(resolve => setTimeout(resolve, ms))
