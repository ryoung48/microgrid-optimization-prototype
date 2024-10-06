export type OptimizationParams = {
  E_load: number[]
  E_PV: number[]
  E_Hydro: number[]
  options: {
    years: number
    battery: {
      initial_soc: number
      max_discharge: number
      efficiency: number
      capex: number
    }
    diesel: { capex: number; opex: number }
    pv: { capex: number }
    hydro: { capex: number; max: number }
  }
}

export type OptimizationResult = {
  capacity: {
    PV: number
    battery: number
    diesel: number
    hydro: number
  }
  E_PV: number[]
  E_Hydro: number[]
  E_batt: number[]
  E_diesel: number[]
  C_batt: number[]
  E_load: number[]
  cost: number
}
