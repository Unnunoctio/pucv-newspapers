import * as cheerio from 'cheerio'
import { Paper } from '../classes/Paper'
import { Newspaper } from '../enums'
import { splitIntoBlocks } from '../helpers/array'
import { differenceDays } from '../helpers/date'
import { fetchPage, fetchPaper } from '../helpers/fetch'

export class ElMostrador {
  private readonly BASE_URL = 'https://www.elmostrador.cl/categoria/dia/'
  private readonly PAGE_BLOCK = 10
  private readonly SLEEP = 5000

  public async run (startDate: Date | undefined): Promise<Paper[]> {
    console.log('Obteniendo noticias desde El Mostrador...')
    console.time('El Mostrador')
    if (startDate === undefined) {
      startDate = new Date()
    }

    let pages: string[] = []
    const totalPages = await this.getTotalPages()
    pages = await this.getPages(startDate, 1, totalPages)

    pages.reverse() //* Siempre guardar las noticias mas antiguas primero
    console.log('Cantidad de páginas: ', pages.length)

    // TODO: crear bloques de x paginas e iterar
    const blocks = splitIntoBlocks(pages, this.PAGE_BLOCK)

    const allPapers: Paper[] = []
    for (const block of blocks) {
      const urls = (await Promise.all(block.map(async page => await this.getPaperUrls(page)))).flat()
      const papers = (await Promise.all(urls.map(async url => await this.getPaper(url, startDate)))).flat()
      console.log('Cantidad de Papers:', papers.length)
      // eslint-disable-next-line @typescript-eslint/no-unnecessary-type-assertion
      allPapers.push(...papers.filter(p => p !== undefined) as Paper[])
    }

    console.timeEnd('El Mostrador')
    return allPapers
  }

  // TODO: obtiene el numero total de  paginas
  private async getTotalPages (): Promise<number> {
    const body = await fetchPage(this.BASE_URL)
    if (body === undefined) return 0

    const $ = cheerio.load(body)

    const pageItems = $('.the-pagination .the-pagination__item')
    const lastPageUrl = pageItems.last().attr('href')
    return parseInt(lastPageUrl?.split('/')[6] as string)
  }

  // TODO: obtiene la pagina con la fecha anterior, de esta manera se evita omitir noticias
  private async getPages (searchDate: Date, startPage: number, endPage: number): Promise<string[]> {
    if (startPage >= endPage - 1) return Array.from({ length: endPage }, (_, i) => `${this.BASE_URL}page/${i + 1}/`)

    const midPage = Math.floor((startPage + endPage) / 2)

    const body = await fetchPage(`${this.BASE_URL}page/${midPage}/`)
    if (body === undefined) return await this.getPages(searchDate, startPage + 1, endPage)

    const $ = cheerio.load(body)
    const pageItems = $('.d-section__body .d-tag-card .d-tag-card__date')
    // Date (dd-mm-aaaa)
    const lastPapertime = (pageItems.last().attr('datetime') as string).split('-')
    const lastPaperDate = new Date(`${lastPapertime[2]}-${lastPapertime[1]}-${lastPapertime[0]}`)

    const diff = differenceDays(searchDate, lastPaperDate)
    if (diff === 1) {
      return Array.from({ length: midPage }, (_, i) => `${this.BASE_URL}page/${i + 1}/`)
    } else if (diff > 1) {
      return await this.getPages(searchDate, startPage, midPage)
    } else {
      return await this.getPages(searchDate, midPage, endPage)
    }
  }

  private async getPaperUrls (page: string): Promise<string[]> {
    const body = await fetchPage(page, this.SLEEP)
    if (body === undefined) return []

    const $ = cheerio.load(body)

    const links = $('.d-section__body .d-tag-card__title .d-tag-card__permalink')
    const urls: string[] = []
    links.each((_, elem) => {
      const url = $(elem).attr('href')
      urls.push(url as string)
    })

    return urls
  }

  private async getPaper (url: string, startDate: Date): Promise<Paper | undefined> {
    const body = await fetchPaper(url, this.SLEEP)
    if (body === undefined) return undefined

    // TODO: Verificar si la fecha es igual o posterior a la fecha de inicio
    const $ = cheerio.load(body)
    const datetime = $('.d-the-single__date').attr('datetime')
    if (datetime === undefined) {
      return undefined
    } else {
      const date = new Date(datetime)
      if (differenceDays(startDate, date) >= 1) return undefined
    }

    const paper = new Paper(Newspaper.EL_MOSTRADOR, url)
    paper.setElMostradorData(body)
    return paper
  }
}
