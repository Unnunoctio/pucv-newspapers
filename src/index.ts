// import { differenceDays } from './helpers/date'
import { ElMostrador } from './spiders/ElMostrador'

// const currentDate = new Date()
// const lastDate = new Date('2022-07-05')
// const antDate = new Date('2022-07-04')
// const otherDate = new Date('2021-03-30')

// console.log(differenceDays(lastDate, currentDate))
// console.log(differenceDays(lastDate, antDate))
// console.log(differenceDays(lastDate, otherDate))
// console.log(differenceDays(lastDate, lastDate))

await new ElMostrador().run()
