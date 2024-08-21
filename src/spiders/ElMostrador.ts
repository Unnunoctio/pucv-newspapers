import * as cheerio from 'cheerio'
import { Paper } from '../classes/Paper'
import { Newspaper } from '../enums'
import { differenceDays } from '../helpers/date'
import { fetchWithRetry } from '../helpers/fetch'
import { splitIntoBlocks } from '../helpers/array'

export class ElMostrador {
  private readonly BASE_URL = 'https://www.elmostrador.cl/categoria/dia/'
  private readonly PAGE_RANGE = 100
  private readonly PAGE_BLOCK = 200
  private readonly SLEEP = 10000

  public async run (): Promise<Paper[]> {
    console.time('El Mostrador')
    // const lastDate: Date | undefined = undefined
    const lastDate: Date | undefined = new Date('2023-08-14')

    let pages: string[] = []

    if (lastDate === undefined) pages = await this.getAllPages()
    else pages = await this.getPages(lastDate, this.PAGE_RANGE)

    pages.reverse() //* Siempre guardar las noticias mas antiguas primero
    console.log(pages.length)

    // TODO: crear bloques de x paginas e iterar
    const blocks = splitIntoBlocks(pages, this.PAGE_BLOCK)

    const allPapers: Paper[] = []
    for (const block of blocks) {
      const urls = (await Promise.all(block.map(async page => await this.getPaperUrls(page)))).flat()
      const papers = (await Promise.all(urls.map(async url => await this.getPaper(url)))).flat()
      allPapers.push(...papers)
      console.log(allPapers.length)
    }

    console.timeEnd('El Mostrador')
    return []
  }

  // TODO: obtiene todas las paginas
  private async getAllPages (): Promise<string[]> {
    const body = await fetchWithRetry(this.BASE_URL)
    const $ = cheerio.load(body)

    const pageItems = $('.the-pagination .the-pagination__item')
    const lastPageUrl = pageItems.last().attr('href')
    const lastPage = parseInt(lastPageUrl?.split('/')[6] as string)

    return Array.from({ length: lastPage }, (_, i) => `${this.BASE_URL}page/${i + 1}/`)
  }

  // TODO: obtiene de la pagina 5 el ultimo paper y si la diferencia de dias es menor a 2 dias, aumenta otras 5 paginas
  private async getPages (lastDate: Date, pagesCount: number): Promise<string[]> {
    const body = await fetchWithRetry(`${this.BASE_URL}page/${pagesCount}/`)
    const $ = cheerio.load(body)

    const paperItems = $('.d-section__body .d-tag-card .d-tag-card__date')
    // Date (dd-mm-aaaa)
    const lastPapertime = (paperItems.last().attr('datetime') as string).split('-')
    const lastPaperDate = new Date(`${lastPapertime[2]}-${lastPapertime[1]}-${lastPapertime[0]}`)

    const diff = differenceDays(lastDate, lastPaperDate)

    if (diff >= 1) return Array.from({ length: pagesCount }, (_, i) => `${this.BASE_URL}page/${i + 1}/`)
    return await this.getPages(lastDate, pagesCount + this.PAGE_RANGE)
  }

  private async getPaperUrls (page: string): Promise<string[]> {
    const body = await fetchWithRetry(page, this.SLEEP)
    const $ = cheerio.load(body)

    const links = $('.d-section__body .d-tag-card__title .d-tag-card__permalink')
    const urls: string[] = []
    links.each((_, elem) => {
      const url = $(elem).attr('href')
      urls.push(url as string)
    })

    return urls
  }

  private async getPaper (url: string): Promise<Paper> {
    const body = await fetchWithRetry(url, this.SLEEP)

    const paper = new Paper(Newspaper.EL_MOSTRADOR, url)
    paper.setElMostradorData(body)
    return paper
  }
}
