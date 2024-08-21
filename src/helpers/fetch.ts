import axios from 'axios'

const MAX_RETRIES = 3
const RETRY_DELAY = 5000

export const fetchPage = async (url: string, delay: number = RETRY_DELAY, retries = 0): Promise<any | undefined> => {
  try {
    const { data } = await axios.get(url)
    return data
  } catch (error: any) {
    if (retries < MAX_RETRIES) {
      console.log(`Retry ${retries + 1} for URL: ${url}`)
      await sleep(delay)
      return await fetchPage(url, retries + 1)
    } else {
      console.error(`Failed to fetch URL: ${url} after ${MAX_RETRIES} retries.`)
      return undefined
    }
  }
}

export const fetchPaper = async (url: string, delay: number = RETRY_DELAY, retries = 0): Promise<any | undefined> => {
  try {
    const { data } = await axios.get(url)
    return data
  } catch (error: any) {
    if (error?.response?.status === 404) {
      console.error(`URL not found: ${url}`)
      return undefined
    }

    if (retries < MAX_RETRIES) {
      console.log(`Retry ${retries + 1} for URL: ${url}`)
      await sleep(delay)
      return await fetchPage(url, retries + 1)
    } else {
      console.error(`Failed to fetch URL: ${url} after ${MAX_RETRIES} retries.`)
      return undefined
    }
  }
}

export const sleep = async (ms: number): Promise<void> => await new Promise(resolve => setTimeout(resolve, ms))
