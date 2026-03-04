import CycleCharts from '@/components/cycle-charts';
import { apiFetch } from '@/components/api';

type Metrics = {
  cycle_id: number; feed_total_kg: number; biomass_gain_kg: number; estimated_biomass_kg: number;
  survival_rate: number; adg_g_per_day: number; fcr: number; cost_per_lb: number; estimated_margin_per_lb: number;
};
type Alert = { date: string; severity: string; message: string; metric: string };
type Dashboard = { cycle_id: number; points: any[] };

export default async function CyclePage({ params }: { params: { id: string } }) {
  const id = Number(params.id);
  const [metrics, alerts, dashboard] = await Promise.all([
    apiFetch<Metrics>(`/metrics?cycle_id=${id}`),
    apiFetch<Alert[]>(`/alerts?cycle_id=${id}`),
    apiFetch<Dashboard>(`/cycles/${id}/dashboard`),
  ]);

  return (
    <div className="grid">
      <div className="card">
        <h2>Cycle Dashboard #{id}</h2>
        <div className="grid grid-4">
          <div className="card"><strong>FCR</strong><p>{metrics.fcr}</p></div>
          <div className="card"><strong>Supervivencia</strong><p>{(metrics.survival_rate * 100).toFixed(2)}%</p></div>
          <div className="card"><strong>Biomasa est.</strong><p>{metrics.estimated_biomass_kg} kg</p></div>
          <div className="card"><strong>Margen/lb</strong><p>${metrics.estimated_margin_per_lb}</p></div>
        </div>
      </div>
      <CycleCharts points={dashboard.points} />
      <div className="card">
        <h3>Historial de alertas ciclo</h3>
        <table className="table">
          <thead><tr><th>Fecha</th><th>Severidad</th><th>Métrica</th><th>Mensaje</th></tr></thead>
          <tbody>
            {alerts.map((a, idx) => <tr key={idx}><td>{a.date}</td><td className={a.severity==='CRITICAL'?'badge-critical':'badge-warning'}>{a.severity}</td><td>{a.metric}</td><td>{a.message}</td></tr>)}
          </tbody>
        </table>
      </div>
    </div>
  );
}
