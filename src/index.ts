/* eslint-disable no-multi-spaces */
import { getPapers } from './utils/get-papers'

// Formato de fecha: yyyy-mm-dd
const startDate = '2017-01-01'
const endDate   = '2017-12-31'

await getPapers(startDate, endDate)
