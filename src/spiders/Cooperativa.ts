import * as cheerio from 'cheerio'
import { Paper } from '../classes/Paper'
import { Newspaper } from '../enums'
import { fetchPage, fetchPaper } from '../helpers/fetch'

export class Cooperativa {
  private readonly BASE_URL = 'https://www.cooperativa.cl'
  private readonly PAGE_BASE_URL = 'https://www.cooperativa.cl/noticias/site/cache/nroedic/todas/'
  private readonly SLEEP = 5000

  public async run (startDate: Date, endDate: Date): Promise<Paper[]> {
    console.log('Obteniendo noticias desde Cooperativa...')
    console.time('Cooperativa')

    // TODO: Generar url de las paginas
    const pages = await this.generatePages(startDate, endDate)

    const allPapers: Paper[] = []
    for (const page of pages) {
      const dateString = page.split('/').pop()?.split('.')[0]
      const date = new Date(`${dateString?.substring(0, 4)}-${dateString?.substring(4, 6)}-${dateString?.substring(6, 8)}`)

      const urls = await this.getPaperUrls(page)
      urls.reverse()
      const papers = (await Promise.all(urls.map(async url => await this.getPaper(url, date)))).flat()
      // eslint-disable-next-line @typescript-eslint/no-unnecessary-type-assertion
      allPapers.push(...papers.filter(p => p !== undefined) as Paper[])
    }

    console.timeEnd('Cooperativa')
    return allPapers
  }

  // TODO: genera las urls de las paginas de las noticias
  private async generatePages (startDate: Date, endDate: Date): Promise<string[]> {
    const pages: string[] = []

    // eslint-disable-next-line no-unmodified-loop-condition
    for (let i = new Date(startDate); i <= endDate; i.setDate(i.getDate() + 1)) {
      const dateFormatted = i.toISOString().split('T')[0].replaceAll('-', '')
      pages.push(`${this.PAGE_BASE_URL}${dateFormatted}.html`)
    }

    return pages
  }

  // TODO: procesar las paginas
  private async getPaperUrls (page: string): Promise<string[]> {
    const body = await fetchPage(page, this.SLEEP)
    if (body === undefined) return []

    const $ = cheerio.load(body)

    const links = $('.art-todas a')
    const urls: Set<string> = new Set()
    links.each((_, elem) => {
      const pageUrl = $(elem).attr('href')
      const url = `${this.BASE_URL}${pageUrl as string}`
      urls.add(url)
    })

    return [...urls]
  }

  private async getPaper (url: string, date: Date): Promise<Paper | undefined> {
    const body = await fetchPaper(url, this.SLEEP)
    if (body === undefined) return undefined

    const paper = new Paper(Newspaper.COOPERATIVA, url)
    paper.setCooperativaData(body, date)
    return paper
  }
}
