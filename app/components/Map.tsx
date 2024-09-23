'use client'

import React from 'react'
import { Icon } from 'leaflet'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import MarkerClusterGroup from 'react-leaflet-cluster'
import 'leaflet/dist/leaflet.css'
import { villages } from '../data/villages'

const iconTemplate = (path: string) => {
  return new Icon({
    iconUrl: path,
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  })
}

const tiny = iconTemplate(
  'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png'
)
const small = iconTemplate(
  'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-yellow.png'
)
const medium = iconTemplate(
  'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png'
)
const large = iconTemplate(
  'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png'
)

const MyanmarMap: React.FC = () => {
  const position: [number, number] = [18.5162, 95.956] // Center of Myanmar

  return (
    <MapContainer center={position} zoom={6} style={{ height: '98vh', width: '100%' }}>
      <TileLayer
        attribution='&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
        url='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
      />
      <MarkerClusterGroup chunkedLoading>
        {villages.map((point, idx) => {
          return (
            <Marker
              key={idx}
              position={[point.Y_deg, point.X_deg]}
              icon={
                point.Pop > 1000 ? large : point.Pop > 500 ? medium : point.Pop > 100 ? small : tiny
              }
              title={point.village_cluster_id.toString()}
            >
              <Popup>
                <div className='max-w-sm mx-auto bg-white rounded-lg overflow-hidden'>
                  <div className='p-2'>
                    <h2 className='text-2xl font-bold mb-1'>{point.name}</h2>
                    <h3 className='text-mb text-gray-600 mb-4'>
                      {point.admin1}
                      {point.admin2 ? `, ${point.admin2}` : ''}
                      {point.admin3 ? `, ${point.admin3}` : ''}
                    </h3>
                    <p className='text-gray-700 mb-6'>Population: {Math.ceil(point.Pop)}</p>
                    <button
                      className='px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600'
                      onClick={async () => {
                        window.open(`/dashboard/${point.village_cluster_id}`, '_blank')
                      }}
                    >
                      Analyze
                    </button>
                  </div>
                </div>
              </Popup>
            </Marker>
          )
        })}
      </MarkerClusterGroup>
    </MapContainer>
  )
}

export default MyanmarMap
