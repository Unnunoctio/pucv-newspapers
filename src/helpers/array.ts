
export const splitIntoBlocks = (array: string[], blockSize: number): string[][] => {
    const blocks: string[][] = []
    for (let i = 0; i < array.length; i += blockSize) {
        blocks.push(array.slice(i, i + blockSize))
    }
    return blocks
}
