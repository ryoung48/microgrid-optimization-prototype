'use client'

import React from 'react'
import dynamic from 'next/dynamic'
import { OptimizationResult } from '@/app/optimization/types'
import { MICROGRID_CONFIG } from './config'
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false })

export default function GridConfiguration({ capacity }: OptimizationResult) {
  const { PV, battery, diesel, hydro } = capacity
  const microGridConfig = {
    data: [
      {
        type: 'pie',
        values: [PV, hydro, battery, diesel].map(x => parseFloat(x.toFixed(2))),
        labels: ['Solar Panels', 'Hydroelectric', 'Battery Storage', 'Diesel Generator'],
        hole: 0.4, // Creates the 'donut' hole in the middle
        textinfo: 'label+percent',
        insidetextorientation: 'radial',
        marker: {
          colors: [
            MICROGRID_CONFIG.colors.pv,
            MICROGRID_CONFIG.colors.hydro,
            MICROGRID_CONFIG.colors.battery.charge,
            MICROGRID_CONFIG.colors.diesel
          ]
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
      margin: { l: 0, r: 0, b: 30, t: 60 }, // Adjusts margins to make the chart bigger inside the container
      height: 350, // Adjust the height inside the plotly container
      width: 550 // Adjust the width inside the plotly container
    }
  }

  return (
    <div className='h-full bg-white shadow-lg rounded-lg p-4 pb-12 border border-gray-200'>
      <h2 className='text-2xl font-semibold mb-2'>Microgrid Capacity Configuration</h2>
      <div className='h-full'>
        <Plot
          // @ts-ignore
          data={microGridConfig.data}
          layout={microGridConfig.layout}
        />
      </div>
    </div>
  )
}
