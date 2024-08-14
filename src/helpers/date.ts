// si es positivo date2 es anterior a date1, si es negativo date2 es posterior a date1
export const differenceDays = (date1: Date, date2: Date): number => {
  const oneDay = 24 * 60 * 60 * 1000 // hours*minutes*seconds*milliseconds
  const diff = date1.getTime() - date2.getTime()
  const diffDays = Math.floor(diff / oneDay)
  return diffDays
}
