'use client'

import React from 'react'
import dynamic from 'next/dynamic'
import { OptimizationResult } from '@/app/optimization/types'
import { MICROGRID_CONFIG } from './config'
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

export default function LoadDispatch({
  E_PV,
  E_Hydro,
  E_diesel,
  E_load,
  E_batt,
  C_batt
}: OptimizationResult) {
  const timestamps = generateHourlyTimestampsUTC(
    MICROGRID_CONFIG.startDate,
    MICROGRID_CONFIG.numDays
  )

  const energyDispatch = {
    data: [
      {
        name: 'Demand Load',
        y: E_load,
        x: timestamps,
        type: 'scatter', // Line chart type in Plotly is 'scatter'
        mode: 'lines+markers',
        line: { color: MICROGRID_CONFIG.colors.demand }, // Line color
        marker: { color: MICROGRID_CONFIG.colors.demand } // Marker color
      },
      {
        name: 'Diesel Energy',
        y: E_diesel,
        x: timestamps,
        type: 'scatter', // Line chart type in Plotly is 'scatter'
        mode: 'lines+markers',
        line: { color: MICROGRID_CONFIG.colors.diesel },
        marker: { color: MICROGRID_CONFIG.colors.diesel }
      },
      {
        name: 'Solar Energy',
        y: E_PV,
        x: timestamps,
        type: 'scatter', // Line chart type in Plotly is 'scatter'
        mode: 'lines+markers',
        line: { color: MICROGRID_CONFIG.colors.pv },
        marker: { color: MICROGRID_CONFIG.colors.pv }
      },
      {
        name: 'Hydroelectric',
        y: E_Hydro,
        x: timestamps,
        type: 'scatter', // Line chart type in Plotly is 'scatter'
        mode: 'lines+markers',
        line: { color: MICROGRID_CONFIG.colors.hydro },
        marker: { color: MICROGRID_CONFIG.colors.hydro }
      },
      {
        name: 'Battery Charge',
        y: C_batt,
        x: timestamps,
        type: 'scatter', // Line chart type in Plotly is 'scatter'
        mode: 'lines+markers',
        line: { color: MICROGRID_CONFIG.colors.battery.charge },
        marker: { color: MICROGRID_CONFIG.colors.battery.charge }
      },
      {
        name: 'Battery Discharge',
        y: E_batt,
        x: timestamps,
        type: 'scatter', // Line chart type in Plotly is 'scatter'
        mode: 'lines+markers',
        line: { color: MICROGRID_CONFIG.colors.battery.discharge },
        marker: { color: MICROGRID_CONFIG.colors.battery.discharge }
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
  )
}
