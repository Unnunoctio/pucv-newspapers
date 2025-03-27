import { createExcelFile } from './helpers/excel'
import { createFolder } from './helpers/file'
import { ElMostrador } from './spiders/ElMostrador'

// Formato de fecha: yyyy-mm-dd
const startDate = new Date('2025-01-01')
const papers = await new ElMostrador().run(startDate)

console.log('Cantidad de newspapers obtenidos:', papers.length)

// Verifica que existan datos a agregar
if (papers.length === 0) {
  console.log('No se encontraron noticias.')
} else {
  // Crea la carpeta "archivos"
  const folderPath = createFolder('archivos')

  // Crea el archivo excel y lo guarda en la carpeta "archivos"
  await createExcelFile(papers, `newspapers_${startDate.toISOString().split('T')[0]}_al_${new Date().toISOString().split('T')[0]}.xlsx`, folderPath)
}
