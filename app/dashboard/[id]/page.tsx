'use client'

import React from 'react'
import { villages } from '../../data/villages'
import Loader from '@/app/components/Loader'
import dynamic from 'next/dynamic'
import { OptimizationParams, OptimizationResult } from '@/app/optimization/types'
import { optimize_capacity } from '@/app/optimization'
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false })

function generateHourlyTimestampsUTC(startDate: string, n: number): string[] {
  const timestamps: string[] = []
  const start = new Date(`${startDate}T00:00:00Z`) // Force UTC start date

  for (let day = 0; day < n; day++) {
    for (let hour = 0; hour < 24; hour++) {
      // Create a new date for each hour
      const timestamp = new Date(start)
      timestamp.setUTCDate(start.getUTCDate() + day) // Move to the correct day in UTC
      timestamp.setUTCHours(hour, 0, 0, 0) // Set the hour, minutes, seconds, milliseconds in UTC

      // Format the date to 'YYYY-MM-DD HH:mm' in UTC
      const year = timestamp.getUTCFullYear()
      const month = String(timestamp.getUTCMonth() + 1).padStart(2, '0') // Month is zero-indexed
      const dayOfMonth = String(timestamp.getUTCDate()).padStart(2, '0')
      const hours = String(timestamp.getUTCHours()).padStart(2, '0')
      const formattedTimestamp = `${year}-${month}-${dayOfMonth} ${hours}:00`

      timestamps.push(formattedTimestamp)
    }
  }

  return timestamps
}

export default function Page({ params }: { params: { id: string } }) {
  const id = parseInt(params.id)
  const startDate = new Date().toISOString().slice(0, 10)
  const numDays = 7
  const village = villages.find(village => village.village_cluster_id === id)
  const [loading, setLoading] = React.useState(true)
  const [data, setData] = React.useState<OptimizationResult>({
    capacity: {
      PV: 1,
      battery: 1,
      diesel: 1
    },
    E_PV: [0],
    E_batt: [0],
    E_diesel: [0],
    C_batt: [0],
    E_load: [0]
  })
  if (!village) return <div>No data found</div>
  // eslint-disable-next-line react-hooks/rules-of-hooks
  React.useEffect(() => {
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
      const result = optimize_capacity(parsed)
      setData(result)
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
  }, [village, startDate])
  const timestamps = generateHourlyTimestampsUTC(startDate, numDays)

  const colors = {
    diesel: 'rgba(54, 162, 235, 1)',
    pv: 'rgba(75, 192, 192, 1)',
    battery: '#c0954b'
  }

  const microGridConfig = {
    data: [
      {
        type: 'pie',
        values: [data.capacity.PV, data.capacity.battery, data.capacity.diesel],
        labels: ['Solar Panels', 'Battery Storage', 'Diesel Generator'],
        hole: 0.4, // Creates the 'donut' hole in the middle
        textinfo: 'label+percent',
        insidetextorientation: 'radial',
        marker: {
          colors: [colors.pv, colors.battery, colors.diesel]
        }
      }
    ],
    layout: {
      annotations: [
        {
          text: '',
          font: {
            size: 20
          },
          showarrow: false,
          x: 0.5,
          y: 0.5
        }
      ],
      showlegend: false,
      legend: {
        x: 1,
        y: 0.5
      },
      margin: { l: 0, r: 0, b: 30, t: 40 }, // Adjusts margins to make the chart bigger inside the container
      height: 300, // Adjust the height inside the plotly container
      width: 550 // Adjust the width inside the plotly container
    }
  }

  const energyDispatch = {
    data: [
      {
        name: 'Demand Load',
        y: data.E_load,
        x: timestamps,
        type: 'scatter', // Line chart type in Plotly is 'scatter'
        mode: 'lines+markers',
        line: { color: 'rgba(255, 99, 132, 1)' }, // Line color
        marker: { color: 'rgba(255, 99, 132, 0.8)' } // Marker color
      },
      {
        name: 'Diesel Energy',
        y: data.E_diesel,
        x: timestamps,
        type: 'scatter', // Line chart type in Plotly is 'scatter'
        mode: 'lines+markers',
        line: { color: colors.diesel },
        marker: { color: colors.diesel }
      },
      {
        name: 'Solar Energy',
        y: data.E_PV,
        x: timestamps,
        type: 'scatter', // Line chart type in Plotly is 'scatter'
        mode: 'lines+markers',
        line: { color: colors.pv },
        marker: { color: colors.pv }
      },
      {
        name: 'Battery Charge',
        y: data.C_batt,
        x: timestamps,
        type: 'scatter', // Line chart type in Plotly is 'scatter'
        mode: 'lines+markers',
        line: { color: colors.battery },
        marker: { color: colors.battery }
      },
      {
        name: 'Battery Discharge',
        y: data.E_batt,
        x: timestamps,
        type: 'scatter', // Line chart type in Plotly is 'scatter'
        mode: 'lines+markers',
        line: { color: '#4bc07a' },
        marker: { color: '#4bc07a' }
      }
    ],
    layout: {
      yaxis: {
        title: 'kWh'
      },
      legend: {
        orientation: 'h' as const, // 'h' for horizontal legend, 'v' for vertical
        x: 0.25,
        y: 1.5
      }
    }
  }

  return (
    <div className='p-10'>
      <Loader enabled={loading}></Loader>
      {/* Row: Micro Grid Info Section and Donut Chart */}
      <div className='grid grid-cols-1 md:grid-cols-3 gap-8 mb-8'>
        {/* Micro Grid Info Section */}
        <div>
          <h1 className='text-4xl font-bold mb-4'>{village.name}</h1>
          <p>
            <strong>Admin level 1:</strong> {village.admin1 ?? '-'}
          </p>
          <p>
            <strong>Admin level 2:</strong> {village.admin2 ?? '-'}
          </p>
          <p>
            <strong>Admin level 3:</strong> {village.admin3 ?? '-'}
          </p>
          <p>
            <strong>Population:</strong> {Math.ceil(village.Pop)}
          </p>
        </div>

        {/* Donut Chart: MicroGrid Configuration */}
        <div className='h-96 bg-white shadow-lg rounded-lg p-6 pb-12 border border-gray-200'>
          <div className='h-full'>
            <h1 className='text-2xl font-bold mb-4'>Optimization Objectives</h1>
            <p>
              Loss Load:{' '}
              {data.E_load.reduce((sum, curr, i) => {
                const loss = curr - data.E_diesel[i] - data.E_PV[i] - data.E_batt[i]
                return sum + (loss < 0 ? 0 : loss)
              }, 0).toFixed(2)}
            </p>
            <p>
              Curtailment:{' '}
              {data.E_load.reduce((sum, curr, i) => {
                const curtailment = curr - data.E_diesel[i] - data.E_PV[i] - data.E_batt[i]
                return sum + (curtailment >= 0 ? 0 : -curtailment)
              }, 0).toFixed(2)}
            </p>
            <p>
              Diesel Usage:{' '}
              {data.E_diesel.reduce((sum, curr) => {
                return sum + curr
              }, 0).toFixed(2)}
            </p>
          </div>
        </div>

        {/* Donut Chart: MicroGrid Configuration */}
        <div className='h-96 bg-white shadow-lg rounded-lg p-6 pb-12 border border-gray-200'>
          <h2 className='text-2xl font-semibold mb-2'>Microgrid Configuration</h2>
          <div className='h-full'>
            <Plot
              // @ts-ignore
              data={microGridConfig.data}
              layout={microGridConfig.layout}
              // style={{ width: "100%", height: "100%" }}
            />
          </div>
        </div>
      </div>

      {/* Full Width Row: Line Chart for Energy Dispatch */}
      <div className='h-96 bg-white shadow-lg rounded-lg p-6 pb-10 border border-gray-200'>
        <h2 className='text-2xl font-semibold mb-2'>Energy Dispatch Over Time</h2>
        <div className='h-full'>
          <Plot
            // @ts-ignore
            data={energyDispatch.data}
            layout={energyDispatch.layout}
            style={{ width: '100%', height: '100%' }}
          />
        </div>
      </div>
    </div>
  )
}
