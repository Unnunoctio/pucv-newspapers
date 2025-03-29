/* eslint-disable no-multi-spaces */
import { getPapers } from './utils/get-papers'

// Formato de fecha: yyyy-mm-dd
const startDate = '2025-01-01'
const endDate   = '2025-01-31'

await getPapers(startDate, endDate)
