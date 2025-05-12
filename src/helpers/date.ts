// si es positivo date2 es anterior a date1, si es negativo date2 es posterior a date1
export const differenceDays = (date1: Date, date2: Date): number => {
  const oneDay = 24 * 60 * 60 * 1000 // hours*minutes*seconds*milliseconds
  const diff = date1.getTime() - date2.getTime()
  const diffDays = Math.floor(diff / oneDay)
  return diffDays
}

export const validateDate = (date: string, errorMessage: string): Date => {
  try {
    // Verificar si la fecha tiene el formato correcto (YYYY-MM-DD)
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/
    if (!dateRegex.test(date)) {
      throw new Error(errorMessage)
    }

    // Extraer año, mes y día
    const [year, month, day] = date.split('-').map(Number)

    // Crear una fecha con los componentes
    const parsedDate = new Date(year, month - 1, day)

    // Verificar si la fecha resultante tiene el mismo año, mes y día que la entrada
    // Esto detectará fechas inválidas como 2025-02-31
    if (
      parsedDate.getFullYear() !== year ||
      parsedDate.getMonth() !== month - 1 ||
      parsedDate.getDate() !== day
    ) {
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
