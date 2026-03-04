'use client';

import { Line, LineChart, CartesianGrid, Tooltip, XAxis, YAxis, ResponsiveContainer, BarChart, Bar, ScatterChart, Scatter } from 'recharts';

type Point = {
  date: string;
  fcr: number | null;
  mortality: number;
  avg_weight_g: number | null;
  biomass_kg: number | null;
  temperature_c: number | null;
  rain_mm: number | null;
};

export default function CycleCharts({ points }: { points: Point[] }) {
  return (
    <div className="grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
      <div className="card"><h3>FCR en el tiempo</h3><ResponsiveContainer width="100%" height={220}><LineChart data={points}><CartesianGrid stroke="#233"/><XAxis dataKey="date" hide /><YAxis /><Tooltip /><Line type="monotone" dataKey="fcr" stroke="#00d2ff" dot={false} /></LineChart></ResponsiveContainer></div>
      <div className="card"><h3>Mortalidad diaria</h3><ResponsiveContainer width="100%" height={220}><BarChart data={points}><CartesianGrid stroke="#233"/><XAxis dataKey="date" hide /><YAxis /><Tooltip /><Bar dataKey="mortality" fill="#ff6b6b"/></BarChart></ResponsiveContainer></div>
      <div className="card"><h3>Peso promedio y Biomasa</h3><ResponsiveContainer width="100%" height={220}><LineChart data={points}><CartesianGrid stroke="#233"/><XAxis dataKey="date" hide /><YAxis /><Tooltip /><Line type="monotone" dataKey="avg_weight_g" stroke="#82ca9d" dot={false}/><Line type="monotone" dataKey="biomass_kg" stroke="#ffc658" dot={false}/></LineChart></ResponsiveContainer></div>
      <div className="card"><h3>Clima vs FCR</h3><ResponsiveContainer width="100%" height={220}><ScatterChart><CartesianGrid stroke="#233"/><XAxis dataKey="temperature_c" name="Temp"/><YAxis dataKey="fcr" name="FCR"/><Tooltip cursor={{ strokeDasharray: '3 3' }} /><Scatter data={points.filter(p=>p.fcr && p.temperature_c)} fill="#8ec5ff"/></ScatterChart></ResponsiveContainer></div>
    </div>
  );
}
