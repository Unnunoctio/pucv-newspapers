import type { Paper } from '../classes/Paper'
import { Newspaper } from '../enums'
import { validateDate, validateDateRange } from '../helpers/date'
import { createExcelFile } from '../helpers/excel'
import { createFolder } from '../helpers/file'
import { Cooperativa } from '../spiders/Cooperativa'
import { ElMostrador } from '../spiders/ElMostrador'
import { Emol } from '../spiders/Emol'
import { TVN } from '../spiders/TVN'

export const getPapers = async (startDateString: string, endDateString: string): Promise<void> => {
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

  // TODO: Obtener noticias desde los Spiders
  const papers: Paper[] = []
  const spiders = [new ElMostrador(), new Cooperativa(), new Emol(), new TVN()]

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
