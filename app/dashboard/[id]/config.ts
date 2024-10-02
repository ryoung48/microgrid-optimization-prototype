export const MICROGRID_CONFIG = {
  numDays: 7,
  startDate: new Date().toISOString().slice(0, 10),
  colors: {
    demand: 'rgba(255, 99, 132, 1)',
    diesel: 'rgba(54, 162, 235, 1)',
    pv: 'rgba(75, 192, 192, 1)',
    battery: { charge: '#c0954b', discharge: '#4bc07a' }
  }
}
