/* eslint-disable @typescript-eslint/restrict-plus-operands */
import * as cheerio from 'cheerio'
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

  constructor (newspaper: Newspaper, url: string) {
    this.newspaper = newspaper
    this.url = url
  }

  setElMostradorData (data: any): void {
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
}
