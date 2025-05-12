/* eslint-disable no-multi-spaces */
import { getPapers } from './utils/get-papers'

// Formato de fecha: yyyy-mm-dd
const startDate = '2025-05-01'
const endDate   = '2025-05-10'

await getPapers(startDate, endDate)
