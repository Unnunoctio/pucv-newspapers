import * as cheerio from "cheerio"
import axios from "axios"

// const { data } = await axios.get('https://www.elmostrador.cl/cultura/ciencia-cultura/2024/08/13/ciencia-y-humanidades-se-unen-en-puerto-de-ideas-biobio-para-conversar-sobre-el-mar-y-la-naturaleza/')
// const { data } = await axios.get('https://www.elmostrador.cl/noticias/pais/2024/08/13/aventura-en-el-casino-bonos-sin-deposito-para-jugadores-de-chile/')
const { data } = await axios.get('https://www.elmostrador.cl/noticias/multimedia/2024/08/13/caso-audios-fiscalia-pidio-formalizar-a-luis-hermosilla-tras-querella-del-sii/')

const $ = cheerio.load(data)

console.log('-------------------------------------------------------------------------------')

// Titulo
const title = $('.d-the-single__title').text().trim()
console.log(title)

// Fecha
const time = $('.d-the-single__date').attr('datetime')
console.log(time)

// Autores
let author: string | undefined
if ($('.the-by__permalink').length > 0) {
    author = $('.the-by__permalink').text().trim()
} else if ($('.the-single-author__permalink').length > 0) {
    author = $('.the-single-author__permalink').text().trim()
} 
console.log(author)

// Bajada
const excerpt = $('.d-the-single__excerpt').text().trim()
console.log(excerpt)

// Cuerpo de la noticia
const body = $('.d-the-single-wrapper__text')
const bodyElem = body.find('h3, p')
bodyElem.each((i, elem) => {
    console.log('')
    console.log($(elem).text().trim())
})