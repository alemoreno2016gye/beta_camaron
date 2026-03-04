import Link from 'next/link';
import { apiFetch } from '@/components/api';

type Pond = { id: number; farm_id: number; name: string; area_ha: number };
type Cycle = { id: number; pond_id: number; code: string; status: string };

export default async function FarmDetail({ params }: { params: { id: string } }) {
  const farmId = Number(params.id);
  const ponds = await apiFetch<Pond[]>(`/ponds?farm_id=${farmId}`);
  const cycles = await apiFetch<Cycle[]>('/cycles');

  return (
    <div className="card">
      <h2>Dashboard Operativo - Finca #{farmId}</h2>
      <table className="table">
        <thead><tr><th>Piscina</th><th>Área (ha)</th><th>Ciclo activo</th><th>Acciones</th></tr></thead>
        <tbody>
          {ponds.map((pond) => {
            const cycle = cycles.find((c) => c.pond_id === pond.id && c.status === 'active');
            return (
              <tr key={pond.id}>
                <td>{pond.name}</td>
                <td>{pond.area_ha}</td>
                <td>{cycle?.code || 'N/A'}</td>
                <td>{cycle ? <Link href={`/cycles/${cycle.id}`}>Abrir dashboard ciclo</Link> : '-'}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
