import * as cheerio from 'cheerio'
import { Paper } from '../classes/Paper'
import { Newspaper } from '../enums'
import { fetchPage, fetchPaper } from '../helpers/fetch'

export class TVN {
    private readonly BASE_URL = 'https://www.tvn.cl/noticias'
    private readonly PAPER_BASE_URL = 'https://www.tvn.cl'

    public async run(startDate: Date, endDate: Date): Promise<Paper[]> {
        console.log('Obteniendo noticias desde TVN...')
        console.time('TVN')

        // TODO: Obtener numero de paginas
        const totalPages = await this.getTotalPages()

        const pages = await this.generatePages(1, totalPages)
        pages.reverse() //* Siempre guardar las noticias mas antiguas primero

        const allPapers: Paper[] = []
        for (const page of pages) {
            const urls = (await Promise.all(await this.getPaperUrls(page))).flat()
            const papers = (await Promise.all(urls.map(async url => await this.getPaper(url)))).flat()
            // eslint-disable-next-line @typescript-eslint/no-unnecessary-type-assertion
            allPapers.push(...papers.filter(p => p !== undefined) as Paper[])
        }

        console.timeEnd('TVN')
        return allPapers
    }

    // TODO: obtiene el numero total de  paginas
    private async getTotalPages(): Promise<number> {
        const body = await fetchPage(`${this.BASE_URL}/p/1`)
        if (body === undefined) return 0

        const $ = cheerio.load(body)

        const pageItems = $('.auxi .wp-pagenavi a')
        const lastPageUrl = pageItems.last().attr('href')
        return parseInt(lastPageUrl?.split('/')[3] as string)
    }

    // TODO: genera las urls de las paginas de las noticias
    private async generatePages(startPage: number, endPage: number): Promise<string[]> {
        return Array.from({ length: endPage }, (_, i) => `${this.BASE_URL}/p/${startPage + i}/`)
    }

    // TODO: procesar las paginas
    private async getPaperUrls(page: string): Promise<string[]> {
        const body = await fetchPage(page)
        if (body === undefined) return []

        const $ = cheerio.load(body)

        const links = $('.auxi .row article a')

        const urls: Set<string> = new Set()
        links.each((_, elem) => {
            const url = $(elem).attr('href')
            urls.add(`${this.PAPER_BASE_URL}${url as string}`)
        })

        return [...urls]
    }

    private async getPaper(url: string): Promise<Paper | undefined> {
        const body = await fetchPaper(url)
        if (body === undefined) return undefined

        const paper = new Paper(Newspaper.TVN, url)
        paper.setTVNData(body)
        return paper
    }
}
