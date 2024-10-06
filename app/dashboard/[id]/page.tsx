'use client'

import React, { useEffect, useRef, useState } from 'react'
import { villages } from '../../data/villages'
import Loader from '@/app/components/Loader'
import { OptimizationParams, OptimizationResult } from '@/app/optimization/types'
import GridConfiguration from './GridConfiguration'
import LoadDispatch from './LoadDispatch'
import { MICROGRID_CONFIG } from './config'
import TextInput from '@/app/components/TextInput'
import StatsCard from '@/app/components/StatsCard'

export default function Page({ params }: { params: { id: string } }) {
  const id = parseInt(params.id)
  const village = villages.find(village => village.village_cluster_id === id)
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState({
    E_PV: [0],
    E_load: [0],
    E_Hydro: [0]
  })
  const [optimization, setOptimization] = useState<OptimizationResult>({
    capacity: {
      PV: 1,
      battery: 1,
      diesel: 1,
      hydro: 0
    },
    E_PV: [0],
    E_Hydro: [0],
    E_batt: [0],
    E_diesel: [0],
    C_batt: [0],
    E_load: [0],
    cost: 0
  })
  const popRef = useRef<HTMLInputElement>(null)
  const yearsRef = useRef<HTMLInputElement>(null)
  const batteryInstallCostRef = useRef<HTMLInputElement>(null)
  const dieselInstallCostRef = useRef<HTMLInputElement>(null)
  const dieselFuelCostRef = useRef<HTMLInputElement>(null)
  const pvInstallCostRef = useRef<HTMLInputElement>(null)
  const hydroInstallCostRef = useRef<HTMLInputElement>(null)
  const hydroMaxRef = useRef<HTMLInputElement>(null)
  const hydroDist = village?.['HydropowerDist'] ?? 1000
  const [settings, applySettings] = useState({
    years: 5,
    batteryInstallCost: 140,
    dieselInstallCost: 261,
    dieselFuelCost: 0.2,
    pvInstallCost: 720,
    hydroInstallCost: hydroDist > 2 ? 300000 : 3000,
    hydroMax: village?.['Hydropower'] ?? 0
  })
  if (!village) return <div>No data found</div>
  const { numDays, startDate } = MICROGRID_CONFIG
  // eslint-disable-next-line react-hooks/rules-of-hooks
  useEffect(() => {
    const lat = village['Y_deg']
    const lon = village['X_deg']
    const pop = village['Pop']
    const households = Math.ceil(pop / 5.1)
    const init = async () => {
      const res = await fetch(
        `/api/data?lat=${lat}&lon=${lon}&households=${households}&num_days=${numDays}&start_date=${startDate}`
      )
      const parsed = (await res.json()) as OptimizationParams
      console.log(parsed)
      setData(parsed)
      setLoading(false)
      sessionStorage.setItem(cacheKey, JSON.stringify({ parsed }))
    }
    const cacheKey = `data-${lat}-${lon}-${pop}-${households}-${numDays}-${startDate}`
    const cachedData = sessionStorage.getItem(cacheKey)

    if (cachedData) {
      const { parsed } = JSON.parse(cachedData)
      setData(parsed)
      setLoading(false)
    } else {
      init()
    }
  }, [village, numDays, startDate])

  // eslint-disable-next-line react-hooks/rules-of-hooks
  useEffect(() => {
    setLoading(true)

    // Create a new Web Worker
    const worker = new Worker('/workers/optimizeWorker.js', { type: 'module' })

    // Send data and settings to the worker
    worker.postMessage({ data, settings })

    // Listen for a message from the worker with the result
    worker.onmessage = (e: { data: OptimizationResult }) => {
      setOptimization(e.data) // Set optimization result from worker
      setLoading(false) // Loading is complete
    }

    // Capture worker errors
    worker.onerror = e => {
      console.error('Web Worker Error:', e)
    }

    // Cleanup the worker when the component is unmounted or when dependencies change
    return () => {
      worker.terminate()
    }
  }, [data, settings])

  return (
    <div className='p-10'>
      <Loader enabled={loading}></Loader>
      {/* Row: Micro Grid Info Section and Donut Chart */}
      <div className='grid grid-cols-1 md:grid-cols-3 gap-8 mb-8'>
        <div className='max-w-lg mx-auto p-5 bg-white rounded-lg shadow-lg'>
          <h2 className='text-3xl font-bold text-gray-700 text-center'>{village.name}</h2>
          {/* Subtitle */}
          <p className='text-gray-500 text-sm mb-6 text-center'>
            {village.admin1}
            {village.admin2 ? `, ${village.admin2}` : ''}
            {village.admin3 ? `, ${village.admin3}` : ''}
          </p>
          <form
            onSubmit={(e: React.FormEvent<HTMLFormElement>) => {
              e.preventDefault()

              const parseMonetaryValue = (value: string | undefined): number => {
                if (!value) return 0
                // Remove $ and other non-numeric characters, then convert to number
                const numericValue = value.replace(/[^0-9.]/g, '')
                return parseFloat(numericValue) || 0 // Return 0 if the value is NaN
              }

              const formData = {
                years: yearsRef.current?.valueAsNumber || 0,
                batteryInstallCost: parseMonetaryValue(batteryInstallCostRef.current?.value),
                dieselInstallCost: parseMonetaryValue(dieselInstallCostRef.current?.value),
                dieselFuelCost: parseMonetaryValue(dieselFuelCostRef.current?.value),
                pvInstallCost: parseMonetaryValue(pvInstallCostRef.current?.value),
                hydroInstallCost: parseMonetaryValue(hydroInstallCostRef.current?.value),
                hydroMax: hydroMaxRef.current?.valueAsNumber ?? 0
              }

              applySettings(formData)
            }}
            className='space-y-6'
          >
            <div className='grid grid-cols-1 sm:grid-cols-2 gap-4'>
              <TextInput
                id='population'
                label='Population'
                type='number'
                ref={popRef}
                defaultValue={Math.ceil(village.Pop)}
                disabled
              />
              <TextInput
                id='years'
                label='System Lifetime (years)'
                type='number'
                ref={yearsRef}
                defaultValue={settings.years}
                required
              />
            </div>
            <div className='grid grid-cols-1 sm:grid-cols-2 gap-4'>
              <TextInput
                id='dieselInstallCost'
                label='Diesel Installation Cost'
                type='number'
                ref={dieselInstallCostRef}
                defaultValue={settings.dieselInstallCost}
                monetary
                required
              />
              <TextInput
                id='dieselFuelCost'
                label='Diesel Fuel Cost'
                type='number'
                ref={dieselFuelCostRef}
                defaultValue={settings.dieselFuelCost}
                monetary
                required
              />
            </div>
            <div className='grid grid-cols-1 sm:grid-cols-2 gap-4'>
              <TextInput
                id='pvInstallCost'
                label='PV Installation Cost'
                type='number'
                ref={pvInstallCostRef}
                defaultValue={settings.pvInstallCost}
                monetary
                required
              />
              <TextInput
                id='batteryInstallCost'
                label='Battery Installation Cost'
                type='number'
                ref={batteryInstallCostRef}
                defaultValue={settings.batteryInstallCost}
                monetary
                required
              />
            </div>
            <div className='grid grid-cols-1 sm:grid-cols-2 gap-4'>
              <TextInput
                id='hydroInstallCost'
                label='Hydro Installation Cost'
                type='number'
                ref={hydroInstallCostRef}
                defaultValue={settings.hydroInstallCost}
                monetary
                required
              />
              <TextInput
                id='maxHydroPotential'
                label='Max Hydro Potential'
                type='number'
                ref={hydroMaxRef}
                defaultValue={settings.hydroMax}
                required
              />
            </div>
            <button
              type='submit'
              className='w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 transition duration-200'
            >
              Submit
            </button>
          </form>
        </div>
        <GridConfiguration {...optimization}></GridConfiguration>

        {/* Micro Grid Info Section */}
        <div className='grid grid-cols-1 md:grid-cols-2'>
          <div className='m-2'>
            <StatsCard
              subtitle='Loss Load (kW)'
              value={optimization.E_load.reduce((sum, curr, i) => {
                const loss =
                  curr - optimization.E_diesel[i] - optimization.E_PV[i] - optimization.E_batt[i]
                return sum + (loss < 0 ? 0 : loss)
              }, 0).toFixed(2)}
            ></StatsCard>
          </div>
          <div className='m-2'>
            <StatsCard
              subtitle='Curtailment (kW)'
              value={optimization.E_load.reduce((sum, curr, i) => {
                const curtailment =
                  curr - optimization.E_diesel[i] - optimization.E_PV[i] - optimization.E_batt[i]
                return sum + (curtailment >= 0 ? 0 : -curtailment)
              }, 0).toFixed(2)}
            ></StatsCard>
          </div>
          <div className='m-2'>
            <StatsCard
              subtitle='CO₂ emissions (kg)'
              value={(
                (optimization.E_diesel.reduce((sum, curr) => {
                  return sum + curr
                }, 0) /
                  9.96) *
                2.68
              ).toFixed(2)}
            ></StatsCard>
          </div>
          <div className='m-2'>
            <StatsCard
              subtitle='Levelized Cost ($)'
              value={optimization.cost.toFixed(2)}
            ></StatsCard>
          </div>
        </div>
      </div>
      <LoadDispatch {...optimization}></LoadDispatch>
    </div>
  )
}
