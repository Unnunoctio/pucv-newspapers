/* eslint-disable @typescript-eslint/restrict-plus-operands */
import * as cheerio from 'cheerio'
import { convert } from 'html-to-text'
import type { Newspaper } from '../enums'

export class Paper {
    newspaper: Newspaper
    url: string // url
    author: string | undefined // autor
    date: Date | undefined // fecha
    tag: string | undefined // etiqueta
    title: string | undefined // Titulo
    drophead: string | undefined // subtitulo o bajada
    excerpt: string | undefined // primer parrafo
    body: string | undefined // cuerpo de la noticia

    constructor(newspaper: Newspaper, url: string) {
        this.newspaper = newspaper
        this.url = url
    }

    setElMostradorData(data: any): void {
        const $ = cheerio.load(data)
        // AUTHOR
        if ($('.the-by__permalink').length > 0) {
            this.author = $('.the-by__permalink').text().trim()
        } else if ($('.the-single-author__permalink').length > 0) {
            this.author = $('.the-single-author__permalink').text().trim()
            if ($('.the-single-author__subtitle').length > 0) {
                const authorSub = $('.the-single-author__subtitle').text().trim()
                if (authorSub !== '') this.author += `, ${authorSub}`
            }
        }
        // DATE (aaaa-mm-dd)
        const time = $('.d-the-single__date').attr('datetime')
        if (time !== undefined) {
            this.date = new Date(time)
        }
        // TAG
        this.tag = $('.d-the-single-media__bag').text().trim()
        // TITLE
        this.title = $('.d-the-single__title').text().trim()
        // DROPHEAD
        // EXCERPT
        this.excerpt = $('.d-the-single__excerpt').text().trim()
        // BODY
        const bodyElem = $('.d-the-single-wrapper__text')
        const elements = bodyElem.find('h3, p, li')
        this.body = ''
        elements.each((_, elem) => {
            const elemString = $(elem).text().trim()
            if (elemString.split(' ')[0] !== 'Inscríbete') {
                this.body += elemString + '\n'
            }
        })
    }

    setCooperativaData(data: any, date: Date): void {
        const $ = cheerio.load(data)
        // AUTHOR
        if ($('.fecha-publicacion span').length > 0) {
            this.author = $('.fecha-publicacion span').text().trim()
        }
        // DATE
        this.date = date
        // TAG
        if ($('.rotulo-topicos').length > 0) {
            const tags = $('.rotulo-topicos a span')
            this.tag = $(tags[0]).text().trim()
        } else {
            const urlSplit = this.url.split('/')
            this.tag = urlSplit[4]
        }
        // TITLE
        this.title = $('h1.titular').text().trim()
        // DROPHEAD
        this.drophead = ''
        if ($('.contenedor-bajada .texto-bajada p').length > 0) {
            const paragraphs = $('.contenedor-bajada .texto-bajada p')
            paragraphs.each((_, elem) => {
                const elemString = $(elem).text().trim()
                this.drophead += elemString + '\n'
            })
        }
        // EXCERPT
        // BODY
        const bodyElem = $('.contenedor-cuerpo .texto-bajada .cuerpo-articulo .cuerpo-ad')
        const elements = bodyElem.find('h2, p, li')
        this.body = ''
        elements.each((_, elem) => {
            const elemString = $(elem).text().trim()
            this.body += elemString + '\n'
        })
    }

    setEmolData(data: EmolApiHitHitSource): void {
        // AUTHOR
        if (data.author !== undefined) {
            this.author = data.author
        }
        // DATE
        if (data.fechaPublicacion !== undefined) {
            this.date = new Date(data.fechaPublicacion.split('T')[0])
        }
        // TAG
        if (data.subSeccion !== undefined) {
            this.tag = data.subSeccion
        } else if (data.seccion !== undefined) {
            this.tag = data.seccion
        }
        // TITLE
        if (data.titulo !== undefined) {
            this.title = data.titulo
        }
        // DROPHEAD
        if (data.bajada !== undefined && data.bajada.length > 0) {
            this.drophead = data.bajada[0].texto
        }
        // EXCERPT
        // BODY
        if (data.texto !== undefined) {
            this.body = convert(data.texto, { wordwrap: false })
        }
    }

    setTVNData(data: any): void {
        const $ = cheerio.load(data)
        // AUTHOR
        if ($('.cont-credits').length > 0) {
            if ($('.cont-credits .author').length > 0) {
                this.author = $('.cont-credits .author').text().trim()
                if ($('.cont-credits .credit').length > 0) {
                    const authorCredit = $('.cont-credits .credit').text().trim()
                    this.author += `, ${authorCredit}`
                }
            }
        }
        // DATE
        if ($('.toolbar .fecha').length > 0) {
            const dateString = $('.toolbar .fecha').text().trim()
            const dateSplit = dateString.split(' ')

            const months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
            this.date = new Date(Number(dateSplit[5]), months.indexOf(dateSplit[3]), Number(dateSplit[1]))
        }
        // TAG
        if ($('.breadcrumbs').length > 0) {
            this.tag = $('.breadcrumbs .breadcrumb a').last().text().trim()
        }
        // TITLE
        if ($('.tit').length > 0) {
            this.title = $('.tit').text().trim()
        }
        // DROPHEAD
        if ($('.baj').length > 0) {
            this.drophead = $('.baj').text().trim()
        }
        // EXCERPT
        // BODY
        if ($('.CUERPO').length > 0) {
            const bodyElem = $('.CUERPO').html()
            this.body = convert(bodyElem as string, { wordwrap: false })
        }
    }
}
