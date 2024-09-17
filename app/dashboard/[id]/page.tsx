"use client";

import React from "react";
import { ResponsiveLine } from "@nivo/line";
import { ResponsivePie } from "@nivo/pie";
import { villages } from "../../data/villages";

// Data types
interface MicroGridConfig {
  component: string;
  size: number;
}

interface EnergyDispatch {
  time: string;
  solar: number;
  wind: number;
  battery: number;
}

interface MicroGridInfo {
  name: string;
  region: string;
  township: string;
  population: number;
  microGridConfig: MicroGridConfig[];
  energyDispatch: EnergyDispatch[];
}

// Sample Data (You can replace this with actual data)
const microGridData: MicroGridInfo = {
  name: "Sample MicroGrid",
  region: "Northern Region",
  township: "Sunshine Town",
  population: 2000,
  microGridConfig: [
    { component: "Solar Panels", size: 40 },
    { component: "Wind Turbines", size: 30 },
    { component: "Battery Storage", size: 30 },
  ],
  energyDispatch: [
    { time: "08:00", solar: 20, wind: 10, battery: 5 },
    { time: "09:00", solar: 50, wind: 20, battery: 10 },
    { time: "10:00", solar: 35, wind: 30, battery: 15 },
    { time: "11:00", solar: 60, wind: 40, battery: 20 },
    { time: "12:00", solar: 80, wind: 60, battery: 25 },
  ],
};

export default function Page({ params }: { params: { id: string } }) {
  const id = parseInt(params.id);
  const village = villages.find((village) => village.village_cluster_id === id);
  if (!village) return <div>No data found</div>;
  // Line chart data for energy dispatch (multiple lines)
  const energyDispatchData = [
    {
      id: "Solar Energy",
      data: microGridData.energyDispatch.map((dispatch) => ({
        x: dispatch.time,
        y: dispatch.solar,
      })),
    },
    {
      id: "Wind Energy",
      data: microGridData.energyDispatch.map((dispatch) => ({
        x: dispatch.time,
        y: dispatch.wind,
      })),
    },
    {
      id: "Battery Storage",
      data: microGridData.energyDispatch.map((dispatch) => ({
        x: dispatch.time,
        y: dispatch.battery,
      })),
    },
  ];

  // Donut chart data for micro grid configuration
  const microGridConfigData = microGridData.microGridConfig.map((config) => ({
    id: config.component,
    label: config.component,
    value: config.size,
  }));

  return (
    <div className="p-10">
      {/* Row: Micro Grid Info Section and Donut Chart */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {/* Micro Grid Info Section */}
        <div>
          <h1 className="text-4xl font-bold mb-4">{village.name}</h1>
          <p>
            <strong>Admin level 1:</strong> {village.admin1 ?? "-"}
          </p>
          <p>
            <strong>Admin level 2:</strong> {village.admin2 ?? "-"}
          </p>
          <p>
            <strong>Admin level 3:</strong> {village.admin3 ?? "-"}
          </p>
          <p>
            <strong>Population:</strong> {Math.ceil(village.Pop)}
          </p>
        </div>

        {/* Donut Chart: MicroGrid Configuration */}
        <div className="h-96 bg-white shadow-lg rounded-lg p-6 border border-gray-200">
          <h2 className="text-2xl font-semibold mb-4">
            Micro Grid Configuration
          </h2>
          <div className="h-full">
            <ResponsivePie
              data={microGridConfigData}
              margin={{ top: 40, right: 80, bottom: 80, left: 80 }}
              innerRadius={0.5}
              padAngle={0.7}
              cornerRadius={3}
              activeOuterRadiusOffset={8}
              borderWidth={1}
              borderColor={{ from: "color", modifiers: [["darker", 0.2]] }}
              arcLinkLabelsSkipAngle={10}
              arcLinkLabelsTextColor="#333333"
              arcLinkLabelsThickness={2}
              arcLinkLabelsColor={{ from: "color" }}
              arcLabelsSkipAngle={10}
              arcLabelsTextColor={{ from: "color", modifiers: [["darker", 2]] }}
            />
          </div>
        </div>
      </div>

      {/* Full Width Row: Line Chart for Energy Dispatch */}
      <div className="h-96 bg-white shadow-lg rounded-lg p-6 pb-10 border border-gray-200">
        <h2 className="text-2xl font-semibold mb-2">
          Energy Dispatch Over Time
        </h2>
        <div className="h-full">
          <ResponsiveLine
            data={energyDispatchData}
            margin={{ top: 50, right: 150, bottom: 50, left: 60 }}
            xScale={{ type: "point" }}
            yScale={{
              type: "linear",
              min: "auto",
              max: "auto",
              stacked: false,
              reverse: false,
            }}
            axisBottom={{
              tickSize: 5,
              tickPadding: 5,
              tickRotation: 0,
              legend: "Time",
              legendOffset: 36,
              legendPosition: "middle",
            }}
            axisLeft={{
              tickSize: 5,
              tickPadding: 5,
              tickRotation: 0,
              legend: "Energy (kWh)",
              legendOffset: -40,
              legendPosition: "middle",
            }}
            pointSize={10}
            pointColor={{ theme: "background" }}
            pointBorderWidth={2}
            pointBorderColor={{ from: "serieColor" }}
            pointLabelYOffset={-12}
            useMesh={true}
            legends={[
              {
                anchor: "top-right",
                direction: "column",
                justify: false,
                translateX: 100,
                translateY: 0,
                itemsSpacing: 0,
                itemDirection: "left-to-right",
                itemWidth: 80,
                itemHeight: 20,
                itemOpacity: 0.75,
                symbolSize: 12,
                symbolShape: "circle",
                symbolBorderColor: "rgba(0, 0, 0, .5)",
                effects: [
                  {
                    on: "hover",
                    style: {
                      itemBackground: "rgba(0, 0, 0, .03)",
                      itemOpacity: 1,
                    },
                  },
                ],
              },
            ]}
          />
        </div>
      </div>
    </div>
  );
}
