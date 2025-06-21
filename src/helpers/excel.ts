import { Workbook } from 'exceljs'
import * as path from 'path'
import type { Paper } from '../classes/Paper'

export const createExcelFile = async (papers: Paper[], fileName: string, folderPath: string): Promise<void> => {
    // TODO: crear archivo excel
    const workbook = new Workbook()

    const groupPapers = Object.groupBy(papers, ({ newspaper }) => newspaper as string)

    Object.keys(groupPapers).forEach((newspaper: string) => {
        const worksheet = workbook.addWorksheet(newspaper)

        worksheet.columns = [
            { header: 'Newspaper', key: 'newspaper' },
            { header: 'URL', key: 'url' },
            { header: 'Autor/Autores', key: 'author' },
            { header: 'Fecha', key: 'date' },
            { header: 'Etiqueta', key: 'tag' },
            { header: 'Título', key: 'title' },
            { header: 'Bajada', key: 'drophead' },
            { header: 'Resumen', key: 'excerpt' },
            { header: 'Cuerpo', key: 'body' }
        ]

        const data = groupPapers[newspaper]?.toSorted((a, b) => {
            if (a.date === undefined || b.date === undefined) return 0
            return a.date.getTime() - b.date.getTime()
        })

        worksheet.addRows(data as Paper[])
    })

    // // Ajustar el ancho de las columnas
    // worksheet.columns.forEach((column: any) => {
    //   let maxLength = 0
    //   column.eachCell({ includeEmpty: true }, (cell: any) => {
    //     // eslint-disable-next-line @typescript-eslint/strict-boolean-expressions
    //     const cellValue = cell.value ? cell.value.toString() : ''
    //     maxLength = Math.max(maxLength, cellValue.length)
    //   })

    //   // Ajustar el ancho de la columna
    //   column.width = maxLength + 1 // Añade un poco de espacio extra
    // })

    const filePath = path.join(folderPath, fileName)

    try {
        await workbook.xlsx.writeFile(filePath)
        console.log('Archivo Excel creado: ', filePath)
    } catch (error) {
        console.error('Error al crear el archivo Excel: ', error)
        throw error
    }
}
