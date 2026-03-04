'use client';

import { useEffect, useState } from 'react';
import { API_URL, apiFetch } from '@/components/api';

type Cycle = { id: number; code: string; status: string };

export default function ReportsPage() {
  const [cycles, setCycles] = useState<Cycle[]>([]);
  const [cycleId, setCycleId] = useState<number | null>(null);

  useEffect(() => {
    apiFetch<Cycle[]>('/cycles').then((data) => {
      setCycles(data);
      if (data.length) setCycleId(data[0].id);
    });
  }, []);

  const download = () => {
    if (!cycleId) return;
    window.open(`${API_URL}/reports/export?cycle_id=${cycleId}`, '_blank');
  };

  return (
    <div className="card">
      <h2>Reports</h2>
      <p>Seleccione ciclo para exportar CSV ejecutivo + historial de alertas.</p>
      <select value={cycleId ?? ''} onChange={(e) => setCycleId(Number(e.target.value))}>
        {cycles.map((c) => <option key={c.id} value={c.id}>{c.code} ({c.status})</option>)}
      </select>
      <button style={{ marginLeft: 8 }} onClick={download}>Descargar CSV</button>
    </div>
  );
}
