import axios from 'axios'

const MAX_RETRIES = 3
const RETRY_DELAY = 5000

export const fetchPage = async (url: string, delay: number = RETRY_DELAY, retries = 0): Promise<any | undefined> => {
    try {
        const { data } = await axios.get(url)
        // console.log(`URL: ${url} fetched successfully.`)
        return data
    } catch (error: any) {
        if (error?.response?.status === 404) {
            console.error(`404 not found for URL: ${url}`)
            return undefined
        }

        if (retries < MAX_RETRIES) {
            console.warn(`RETRY ${retries + 1} for URL: ${url}`)
            await sleep(delay)
            return await fetchPage(url, delay, retries + 1)
        } else {
            console.error(`FAILED fetch after ${MAX_RETRIES} for URL: ${url}`)
            return undefined
        }
    }
}

export const fetchPaper = async (url: string, delay: number = RETRY_DELAY, retries = 0): Promise<any | undefined> => {
    try {
        const { data } = await axios.get(url)
        console.log(`OK for URL: ${url}`)
        return data
    } catch (error: any) {
        if (error?.response?.status === 404) {
            console.error(`404 not found for URL: ${url}`)
            return undefined
        }

        if (retries < MAX_RETRIES) {
            console.warn(`RETRY ${retries + 1} for URL: ${url}`)
            await sleep(delay)
            return await fetchPaper(url, delay, retries + 1)
        } else {
            console.error(`FAILED fetch after ${MAX_RETRIES} for URL: ${url}`)
            return undefined
        }
    }
}

export const sleep = async (ms: number): Promise<void> => await new Promise(resolve => setTimeout(resolve, ms))
