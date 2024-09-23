'use client'

import React from 'react'
import dynamic from 'next/dynamic'

const MapWithNoSSR = dynamic(() => import('./components/Map'), {
  ssr: false
})

const App: React.FC = () => {
  return (
    <div>
      <MapWithNoSSR />
    </div>
  )
}

export default App
