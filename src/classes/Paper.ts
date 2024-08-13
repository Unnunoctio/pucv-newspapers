import type { Newspaper } from "../enums"

export class Paper {
    newspaper: Newspaper
    authors: string | undefined // autores
    dateline: Date | undefined // fecha
    title: string | undefined // Titulo
    drophead: string | undefined // subtitulo o bajada
    lead: string | undefined // primer parrafo
    body: string | undefined // cuerpo de la noticia

    constructor (newspaper: Newspaper) {
        this.newspaper = newspaper
    }
}
