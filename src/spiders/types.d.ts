interface EmolApiResponse {
    hits: EmolApiHit
}

interface EmolApiHit {
    total: number
    hits: EmolApiHitHit[]
}

interface EmolApiHitHit {
    _type: string
    _id: string
    _score: number
    _source: EmolApiHitHitSource
}

interface EmolApiHitHitSource {
    id: number
    author: string
    fuente: string
    seccion: string
    subSeccion: string
    fechaModificacion: string
    fechaPublicacion: string
    titulo: string
    bajada: EmolApiHitHitSourceBajada[]
    texto: string
    permalink: string
}

interface EmolApiHitHitSourceBajada {
    texto: string
}
