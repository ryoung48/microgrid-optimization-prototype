import React from 'react'

interface StatsCardProps {
  subtitle: string
  value: string | number
}

const StatsCard: React.FC<StatsCardProps> = ({ subtitle, value }) => {
  return (
    <div className='bg-white p-3 rounded-lg shadow-lg flex flex-col justify-between w-64 h-full'>
      {/* Subtitle */}
      <div className='text-gray-500 text-sm font-medium mb-2'>{subtitle}</div>

      {/* Value */}
      <div className='text-6xl font-bold text-gray-800 text-center flex-grow flex items-center justify-center'>
        {value}
      </div>
    </div>
  )
}

export default StatsCard
