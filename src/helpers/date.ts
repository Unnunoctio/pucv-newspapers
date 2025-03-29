// si es positivo date2 es anterior a date1, si es negativo date2 es posterior a date1
export const differenceDays = (date1: Date, date2: Date): number => {
  const oneDay = 24 * 60 * 60 * 1000 // hours*minutes*seconds*milliseconds
  const diff = date1.getTime() - date2.getTime()
  const diffDays = Math.floor(diff / oneDay)
  return diffDays
}

export const validateDate = (date: string, errorMessage: string): Date => {
  try {
    const parsedDate = new Date(date)
    if (isNaN(parsedDate.getTime())) {
      throw new Error(errorMessage)
    }
    return parsedDate
  } catch (error) {
    throw new Error(errorMessage)
  }
}

export const validateDateRange = (startDate: Date, endDate: Date): void => {
  const currentDate = new Date()
  if (startDate > currentDate) {
    throw new Error('La fecha de inicio no puede ser mayor a la fecha actual')
  }
  if (endDate > currentDate) {
    throw new Error('La fecha de fin no puede ser mayor a la fecha actual')
  }
  if (startDate > endDate) {
    throw new Error('La fecha de inicio no puede ser mayor a la de fin')
  }
}
