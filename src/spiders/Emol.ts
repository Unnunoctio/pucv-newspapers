import { Paper } from '../classes/Paper'
import { Newspaper } from '../enums'
import { differenceDays } from '../helpers/date'
import { fetchPage } from '../helpers/fetch'

export class Emol {
  private readonly BASE_URL = 'https://newsapi.ecn.cl/NewsApi/emol/buscador/emol?'

  public async run (startDate: Date, endDate: Date): Promise<Paper[]> {
    console.log('Obteniendo noticias desde Emol...')
    console.time('Emol')

    const totalPapers = await this.getTotalPapers()
    const startPaper = await this.getStartPaper(startDate, 0, totalPapers - 1)
    const endPaper = await this.getEndPaper(endDate, 0, startPaper)

    const papersJson = await this.getPaperJson(startPaper, endPaper)
    papersJson.reverse() //* Siempre guardar las noticias mas antiguas primero

    const allPapers: Paper[] = []
    for (const paperJson of papersJson) {
      const paper = new Paper(Newspaper.EMOL, paperJson._source.permalink)
      paper.setEmolData(paperJson._source)
      allPapers.push(paper)
    }

    console.timeEnd('Emol')
    return allPapers
  }

  private async getTotalPapers (): Promise<number> {
    const url = `${this.BASE_URL}size=1&from=0`
    const data: EmolApiResponse = await fetchPage(url)

    return data.hits.total
  }

  private async getStartPaper (startDate: Date, startPaper: number, endPaper: number): Promise<number> {
    if (startPaper >= endPaper - 1) return endPaper

    const midPaper = Math.floor((startPaper + endPaper) / 2)

    const data: EmolApiResponse = await fetchPage(`${this.BASE_URL}size=1&from=${midPaper}`)
    if (data === undefined) return await this.getStartPaper(startDate, startPaper + 1, endPaper)

    const paperDate = new Date(data.hits.hits[0]._source.fechaPublicacion.split('T')[0])

    const diff = differenceDays(startDate, paperDate)
    if (diff === 1) {
      return midPaper
    } else if (diff > 1) {
      return await this.getStartPaper(startDate, startPaper, midPaper)
    } else {
      return await this.getStartPaper(startDate, midPaper, endPaper)
    }
  }

  private async getEndPaper (endDate: Date, startPaper: number, endPaper: number): Promise<number> {
    if (startPaper >= endPaper - 1) return startPaper

    const midPaper = Math.floor((startPaper + endPaper) / 2)

    const data: EmolApiResponse = await fetchPage(`${this.BASE_URL}size=1&from=${midPaper}`)
    if (data === undefined) return await this.getStartPaper(endDate, startPaper, endPaper - 1)

    const paperDate = new Date(data.hits.hits[0]._source.fechaPublicacion.split('T')[0])

    const diff = differenceDays(endDate, paperDate)
    if (diff === -1) {
      return midPaper
    } else if (diff < -1) {
      return await this.getEndPaper(endDate, midPaper, endPaper)
    } else {
      return await this.getEndPaper(endDate, startPaper, midPaper)
    }
  }

  private async getPaperJson (startPaper: number, endPaper: number): Promise<EmolApiHitHit[]> {
    const MAX_SIZE = 500
    const size = startPaper - (endPaper - 1)

    if (size > MAX_SIZE) {
      const hits: EmolApiHitHit[] = []
      for (let i = endPaper; i < startPaper; i += MAX_SIZE) {
        console.log(`URL: ${this.BASE_URL}size=${MAX_SIZE}&from=${i}`)
        const data: EmolApiResponse = await fetchPage(`${this.BASE_URL}size=${MAX_SIZE}&from=${i}`)
        hits.push(...data.hits.hits)
      }
      return hits
    }

    console.log(`URL: ${this.BASE_URL}size=${size}&from=${endPaper}`)
    const data: EmolApiResponse = await fetchPage(`${this.BASE_URL}size=${size}&from=${endPaper}`)
    return data.hits.hits
  }
}
