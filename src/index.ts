/* eslint-disable no-multi-spaces */
import type { Spiders_Available } from './types'
import { getPapers } from './utils/get-papers'

const spiders_to_run: Spiders_Available = {
    COOPERATIVA: true,
    EL_MOSTRADOR: true,
    EMOL: true,
    TVN: true
}

// Formato de fecha: yyyy-mm-dd
const startDate = '2017-01-01'
const endDate = '2017-12-31'

await getPapers(startDate, endDate, spiders_to_run)
