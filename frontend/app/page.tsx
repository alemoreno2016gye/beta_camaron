import Link from 'next/link';
import { apiFetch } from '@/components/api';

type Farm = { id: number; name: string; location: string };
type Cycle = { id: number; pond_id: number; code: string; status: string };

export default async function HomePage() {
  const farms = await apiFetch<Farm[]>('/farms');
  const cycles = await apiFetch<Cycle[]>('/cycles');

  const activeCycles = cycles.filter((c) => c.status === 'active');

  return (
    <div className="grid">
      <div className="card">
        <h2>Resumen Ejecutivo</h2>
        <div className="grid grid-4">
          <div className="card"><strong>Fincas</strong><p>{farms.length}</p></div>
          <div className="card"><strong>Ciclos activos</strong><p>{activeCycles.length}</p></div>
          <div className="card"><strong>Total ciclos</strong><p>{cycles.length}</p></div>
          <div className="card"><strong>Alertas críticas demo</strong><p>3+</p></div>
        </div>
      </div>

      <div className="card">
        <h3>Fincas</h3>
        <table className="table">
          <thead><tr><th>Finca</th><th>Ubicación</th><th>Acción</th></tr></thead>
          <tbody>
            {farms.map((farm) => (
              <tr key={farm.id}>
                <td>{farm.name}</td>
                <td>{farm.location}</td>
                <td><Link href={`/farm/${farm.id}`}>Ver detalle</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
