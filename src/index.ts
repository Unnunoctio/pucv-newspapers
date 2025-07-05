/* eslint-disable no-multi-spaces */
import type { Spiders_Available } from './types'
import { getPapers } from './utils/get-papers'

const spiders_to_run: Spiders_Available = {
    COOPERATIVA: false,
    EL_MOSTRADOR: true,
    EMOL: false,
    TVN: false
}

// Formato de fecha: yyyy-mm-dd
const startDate = '2025-06-20'
const endDate = '2025-06-21'

await getPapers(startDate, endDate, spiders_to_run)
