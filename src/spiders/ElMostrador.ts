import axios from 'axios'
import * as cheerio from 'cheerio'
import { Paper } from '../classes/Paper'
import { Newspaper } from '../enums'
import { differenceDays } from '../helpers/date'
import { splitIntoBlocks } from '../helpers/array'

export class ElMostrador {
  private readonly baseUrl = 'https://www.elmostrador.cl/categoria/dia/'
  private readonly pageRange = 25
  private readonly pageBlock = 200
  private readonly sleepBlock = 60000 // 30 segundos

  public async run (): Promise<Paper[]> {
    console.time('El Mostrador')
    // const lastDate: Date | undefined = undefined
    const lastDate: Date | undefined = new Date('2023-08-14')

    let pages: string[] = []

    if (lastDate === undefined) pages = await this.getAllPages()
    else pages = await this.getPages(lastDate, this.pageRange)
    console.log(pages.length)

    // TODO: crear bloques de 50 paginas e iterar: obtener los papers y esperar 10 segundos
    const blocks = splitIntoBlocks(pages, this.pageBlock)

    const paperUrls: string[] = []
    for (const block of blocks) {
      console.log(paperUrls.length)
      const urls = (await Promise.all(block.map(async page => await this.getPaperUrls(page)))).flat()
      paperUrls.push(...urls)
      // const papers = (await Promise.all(paperUrls.map(async url => await this.getPaper(url)))).flat()
      // allPapers.push(...papers.filter(p => p !== undefined))
      await new Promise(resolve => setTimeout(resolve, this.sleepBlock))
    }

    // const pages = await this.getAllPages()
    // console.log(pages)

    // const pages = await this.getPages(this.pageRange)
    // console.log(pages)

    // const paperUrls = (await Promise.all(pages.map(async page => await this.getPaperUrls(page)))).flat()
    // console.log(paperUrls)

    // const papers = (await Promise.all(paperUrls.map(async url => await this.getPaper(url)))).flat()
    // console.log(papers)

    console.timeEnd('El Mostrador')
    return []
  }

  // TODO: obtiene todas las paginas
  private async getAllPages (): Promise<string[]> {
    const { data } = await axios.get(this.baseUrl)
    const $ = cheerio.load(data)

    const pageItems = $('.the-pagination .the-pagination__item')
    const lastPageUrl = pageItems.last().attr('href')
    const lastPage = parseInt(lastPageUrl?.split('/')[6] as string)

    return Array.from({ length: lastPage }, (_, i) => `${this.baseUrl}page/${i + 1}/`)
  }

  // TODO: obtiene de la pagina 5 el ultimo paper y si la diferencia de dias es menor a 2 dias, aumenta otras 5 paginas
  private async getPages (lastDate: Date, pagesCount: number): Promise<string[]> {
    const { data } = await axios.get(`${this.baseUrl}page/${pagesCount}/`)
    const $ = cheerio.load(data)

    const paperItems = $('.d-section__body .d-tag-card .d-tag-card__date')
    // Date (dd-mm-aaaa)
    const lastPapertime = (paperItems.last().attr('datetime') as string).split('-')
    const lastPaperDate = new Date(`${lastPapertime[2]}-${lastPapertime[1]}-${lastPapertime[0]}`)

    const diff = differenceDays(lastDate, lastPaperDate)

    if (diff >= 1) return Array.from({ length: pagesCount }, (_, i) => `${this.baseUrl}page/${i + 1}/`)
    return await this.getPages(lastDate, pagesCount + this.pageRange)
  }

  private async getPaperUrls (page: string): Promise<string[]> {
    const { data } = await axios.get(page)
    const $ = cheerio.load(data)

    const links = $('.d-section__body .d-tag-card__permalink')
    const urls: string[] = []
    links.each((_, elem) => {
      const url = $(elem).attr('href')
      if (url !== undefined) {
        urls.push(url)
      }
    })

    return urls
  }

  private async getPaper (url: string): Promise<Paper | undefined> {
    try {
      const { data } = await axios.get(url)

      const paper = new Paper(Newspaper.EL_MOSTRADOR, url)
      paper.setElMostradorData(data)
      return paper
    } catch (error) {
      console.error('Error al cargar la url:', url, error)
      return undefined
    }
  }
}
