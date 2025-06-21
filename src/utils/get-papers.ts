import type { Paper } from '../classes/Paper'
import { Newspaper } from '../enums'
import { validateDate, validateDateRange } from '../helpers/date'
import { createExcelFile } from '../helpers/excel'
import { createFolder } from '../helpers/file'
import { Cooperativa } from '../spiders/Cooperativa'
import { ElMostrador } from '../spiders/ElMostrador'
import { Emol } from '../spiders/Emol'
import { TVN } from '../spiders/TVN'
import type { Spiders_Available } from '../types'

export const getPapers = async (startDateString: string, endDateString: string, spiders_to_run: Spiders_Available): Promise<void> => {
    // TODO: Validar fechas
    let startDate = new Date()
    let endDate = new Date()

    try {
        startDate = validateDate(startDateString, 'La fecha de inicio no es válida')
        endDate = validateDate(endDateString, 'La fecha de fin no es válida')

        validateDateRange(startDate, endDate)
    } catch (error: any) {
        console.error('ERROR:', error.message)
        return
    }

    // TODO: Set spiders
    const spiders: any[] = []
    if (spiders_to_run.COOPERATIVA) spiders.push(new Cooperativa())
    if (spiders_to_run.EL_MOSTRADOR) spiders.push(new ElMostrador())
    if (spiders_to_run.EMOL) spiders.push(new Emol())
    if (spiders_to_run.TVN) spiders.push(new TVN())

    // TODO: Obtener noticias desde los Spiders
    const papers: Paper[] = []
    for (const spider of spiders) {
        const spiderPapers = await spider.run(startDate, endDate)
        papers.push(...spiderPapers)
    }

    // TODO: Imprimir cantidad de noticias por periódico
    console.log('\n-------------------------------------------------------------------')
    console.log('Cantidad de total de noticias obtenidas:')
    for (const newspapers of Object.values(Newspaper)) {
        const papersByNewspaper = papers.filter(paper => paper.newspaper === newspapers)
        console.log(`\t${newspapers}:`, papersByNewspaper.length)
    }

    // TODO: Guarda las noticias en la carpeta "archivos"
    console.log('\n-------------------------------------------------------------------')
    if (papers.length === 0) {
        console.log('No se encontraron noticias.')
        return
    }

    try {
        const folderPath = createFolder('archivos')
        await createExcelFile(papers, `newspapers_${startDate.toISOString().split('T')[0]}_al_${endDate.toISOString().split('T')[0]}.xlsx`, folderPath)
    } catch (error: any) {
        console.error('ERROR:', error.message)
    }
}
