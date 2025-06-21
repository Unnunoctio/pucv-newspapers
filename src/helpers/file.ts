import * as fs from 'fs'
import * as path from 'path'

export const createFolder = (folderName: string): string => {
    const projectRoot = path.join(__dirname, '..', '..')
    const folderPath = path.join(projectRoot, folderName)

    if (!fs.existsSync(folderPath)) {
        fs.mkdirSync(folderPath)
    }

    return folderPath
}
