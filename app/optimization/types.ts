export type OptimizationParams = {
  E_load: number[]
  E_PV: number[]
}

export type OptimizationResult = {
  capacity: {
    PV: number
    battery: number
    diesel: number
  }
  E_PV: number[]
  E_batt: number[]
  E_diesel: number[]
  C_batt: number[]
  E_load: number[]
}
