import { OptimizationParams, OptimizationResult } from './types'

// Constants
const SIMULATION_YEARS = 5

// Battery Constants
const RTE_BATT = 0.95 // Round trip efficiency of the battery
const CHARGE_EFFICIENCY = Math.sqrt(RTE_BATT) // Used for both charge and discharge
const MAX_DISCHARGE = 0.9 // Maximum discharge of the battery
const BATTERY_COST = 140
const battery_initial_soc = 0.5 // Initial state of charge

// PV Constants
const PV_COST = 720

// Diesel Constants
const DIESEL_COST = 261
const DIESEL_FUEL = 0.2

// Function to calculate energy balance over the time period
function energy_balance(
  pv_capacity: number,
  battery_capacity: number,
  diesel_capacity: number,
  E_load: number[],
  E_PV: number[]
): { E_batt: number[]; E_diesel: number[]; C_batt: number[] } {
  const PV_output = E_PV.map(e => pv_capacity * e) // Actual energy produced by the PV system [Wh]
  const E_batt = new Array(E_load.length).fill(0)
  const C_batt = new Array(E_load.length).fill(0)
  const E_diesel = new Array(E_load.length).fill(0)
  let soc = battery_initial_soc * battery_capacity // State of charge starts at initial SOC
  const max_battery_discharge = (1 - MAX_DISCHARGE) * battery_capacity

  for (let t = 0; t < E_load.length; t++) {
    let surplus = PV_output[t] - E_load[t]

    if (surplus > 0) {
      // Charge battery with surplus
      soc += CHARGE_EFFICIENCY * surplus
      soc = Math.min(soc, battery_capacity) // Cap at battery capacity
    } else {
      // Discharge battery to meet deficit
      const available = soc - max_battery_discharge
      const discharged = Math.min(available, -surplus / CHARGE_EFFICIENCY)
      if (discharged > 0) {
        soc -= discharged
      }
      const final_discharge = discharged * CHARGE_EFFICIENCY
      E_batt[t] = Math.max(final_discharge, 0)
      surplus += final_discharge
    }

    if (surplus < -0.0000001) {
      E_diesel[t] = Math.min(-surplus, diesel_capacity)
    }
    C_batt[t] = soc
  }

  return { E_batt, E_diesel, C_batt }
}

// Objective function to minimize
function cost_func(x: number[], E_load: number[], E_PV: number[]): number {
  const pv_capacity = x[0]
  const battery_capacity = x[1]
  const diesel_capacity = x[2]

  const pv_capacity_cost = pv_capacity * PV_COST
  const battery_capacity_cost = battery_capacity * BATTERY_COST
  const diesel_capacity_cost = diesel_capacity * DIESEL_COST

  // Levelized cost of energy (LCOE)
  const { E_diesel } = energy_balance(pv_capacity, battery_capacity, diesel_capacity, E_load, E_PV)

  // Scaling the demand with a load factor to see the long-term benefit
  const adjusted_demand = SIMULATION_YEARS * 8760
  const load_factor = 1 / (E_load.length / adjusted_demand)
  const total_cost =
    pv_capacity_cost +
    battery_capacity_cost +
    diesel_capacity_cost +
    E_diesel.reduce((sum, e) => sum + e, 0) * load_factor * DIESEL_FUEL
  return total_cost / (E_load.reduce((sum, e) => sum + e, 0) * load_factor)
}

// Checks if the demand is met
function demand_constraint(x: number[], E_load: number[], E_PV: number[]): number {
  const pv_capacity = x[0]
  const battery_capacity = x[1]
  const diesel_capacity = x[2]
  const { E_batt, E_diesel } = energy_balance(
    pv_capacity,
    battery_capacity,
    diesel_capacity,
    E_load,
    E_PV
  )
  const residuals = E_load.map(
    (e_load_t, t) => E_batt[t] + E_diesel[t] + pv_capacity * E_PV[t] - e_load_t
  )
  return Math.min(...residuals)
}

// Objective function that penalizes if constraints are violated
function constrained_cost(x: number[], E_load: number[], E_PV: number[]): number {
  const constraint_violation = demand_constraint(x, E_load, E_PV)
  if (constraint_violation < -0.0001) {
    // Apply a large penalty if the constraint is violated
    return Infinity
  }
  return cost_func(x, E_load, E_PV)
}

// Helper function to select k unique random elements from an array
function randomSample(arr: number[], k: number): number[] {
  const arrCopy = arr.slice()
  const result: number[] = []
  while (result.length < k && arrCopy.length > 0) {
    const idx = Math.floor(Math.random() * arrCopy.length)
    result.push(arrCopy.splice(idx, 1)[0])
  }
  return result
}

// Differential Evolution optimization algorithm
function differential_evolution(
  objective: (x: number[], ...args: any[]) => number,
  bounds: [number, number][],
  mutation = 0.5,
  recombination = 0.7,
  pop_size = 20,
  max_iter = 1000,
  tol = 1e-6,
  ...args: any[]
): { best_solution: number[]; best_score: number } {
  const num_params = bounds.length

  // Initialize population with random solutions within the specified bounds
  const population: number[][] = []
  for (let i = 0; i < pop_size; i++) {
    const individual: number[] = []
    for (let j = 0; j < num_params; j++) {
      const [lower, upper] = bounds[j]
      const value = lower + Math.random() * (upper - lower)
      individual.push(value)
    }
    population.push(individual)
  }

  // Evaluate the population
  const scores = population.map(ind => objective(ind, ...args))

  for (let iteration = 0; iteration < max_iter; iteration++) {
    const best_score = Math.min(...scores)
    const worst_score = Math.max(...scores)

    if (Math.abs(worst_score - best_score) < tol) {
      console.log(`Convergence reached at iteration ${iteration}`)
      break
    }

    for (let i = 0; i < pop_size; i++) {
      // Mutation: select three random and distinct individuals from the population, excluding individual i
      const indices = [...Array(pop_size).keys()].filter(idx => idx !== i)
      const [a, b, c] = randomSample(indices, 3)

      // Create a mutant vector
      const mutant: number[] = []
      for (let j = 0; j < num_params; j++) {
        const value = population[a][j] + mutation * (population[b][j] - population[c][j])
        mutant.push(value)
      }

      // Recombination (crossover) with the current individual
      const trial: number[] = []
      for (let j = 0; j < num_params; j++) {
        trial.push(Math.random() < recombination ? mutant[j] : population[i][j])
      }

      // Ensure trial vector remains within the bounds
      for (let j = 0; j < num_params; j++) {
        const [lower, upper] = bounds[j]
        trial[j] = Math.max(Math.min(trial[j], upper), lower)
      }

      // Evaluate the trial solution
      const trial_score = objective(trial, ...args)

      // Selection: replace the current individual with the trial vector if it has a lower objective value
      if (trial_score < scores[i]) {
        population[i] = trial
        scores[i] = trial_score
      }
    }
  }

  const best_idx = scores.indexOf(Math.min(...scores))
  return {
    best_solution: population[best_idx],
    best_score: scores[best_idx]
  }
}

// Function to optimize battery and solar capacity
export function optimize_capacity({ E_load, E_PV }: OptimizationParams): OptimizationResult {
  const bounds: [number, number][] = [
    [0, 1000],
    [0, 5000],
    [0, 1000]
  ] // Lower and upper bounds

  // Attempt optimization with different methods or tweaks
  const result = differential_evolution(
    constrained_cost,
    bounds,
    0.5,
    0.7,
    15,
    5000,
    1e-7,
    E_load,
    E_PV
  )
  const optimal_pv_capacity = result.best_solution[0]
  const optimal_battery_capacity = result.best_solution[1]
  const optimal_diesel_capacity = result.best_solution[2]
  const { E_batt, E_diesel, C_batt } = energy_balance(
    optimal_pv_capacity,
    optimal_battery_capacity,
    optimal_diesel_capacity,
    E_load,
    E_PV
  )

  return {
    capacity: {
      PV: optimal_pv_capacity,
      battery: optimal_battery_capacity,
      diesel: optimal_diesel_capacity
    },
    E_PV: E_PV.map(e => optimal_pv_capacity * e),
    E_batt: E_batt,
    E_diesel: E_diesel,
    C_batt: C_batt,
    E_load: E_load
  }
}
