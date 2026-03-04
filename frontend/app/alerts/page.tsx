import { apiFetch } from '@/components/api';

type Cycle = { id: number; status: string };
type Alert = { cycle_id: number; date: string; severity: string; metric: string; message: string };

export default async function AlertsPage({ searchParams }: { searchParams: { severity?: string } }) {
  const cycles = await apiFetch<Cycle[]>('/cycles');
  const active = cycles.filter((c) => c.status === 'active').slice(0, 8);
  const alertsNested = await Promise.all(active.map((c) => apiFetch<Alert[]>(`/alerts?cycle_id=${c.id}`)));
  let alerts = alertsNested.flat();
  if (searchParams.severity) alerts = alerts.filter((a) => a.severity === searchParams.severity);

  return (
    <div className="card">
      <h2>Alerts Center</h2>
      <p>Filtro rápido: <a href="/alerts?severity=CRITICAL">CRITICAL</a> | <a href="/alerts?severity=WARNING">WARNING</a> | <a href="/alerts">ALL</a></p>
      <table className="table">
        <thead><tr><th>Ciclo</th><th>Fecha</th><th>Severidad</th><th>Métrica</th><th>Mensaje</th></tr></thead>
        <tbody>{alerts.map((a, i) => <tr key={i}><td>{a.cycle_id}</td><td>{a.date}</td><td className={a.severity==='CRITICAL'?'badge-critical':'badge-warning'}>{a.severity}</td><td>{a.metric}</td><td>{a.message}</td></tr>)}</tbody>
      </table>
    </div>
  );
}
