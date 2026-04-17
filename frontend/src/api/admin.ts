import { apiClient } from './client';

export interface SnapshotNormativo {
  id: string;
  smmlv: number;
  uvt: number;
  pct_salud: number;
  pct_pension: number;
  tabla_arl_json: string;
  vigencia_anio: number;
}

export interface SnapshotCreate {
  smmlv: number;
  uvt: number;
  pct_salud: number;
  pct_pension: number;
  tabla_arl_json: string;
  vigencia_anio: number;
}

export interface CIIU {
  codigo_ciiu: string;
  descripcion: string;
  pct_costos_presuntos: number;
  vigente_desde: string;
}

export interface CIIUCreate {
  codigo_ciiu: string;
  descripcion: string;
  pct_costos_presuntos: number;
  vigente_desde: string;
}

export async function listarSnapshots(): Promise<SnapshotNormativo[]> {
  const res = await apiClient.get<SnapshotNormativo[]>('/admin/parametros/snapshots');
  return res.data;
}

export async function crearSnapshot(data: SnapshotCreate): Promise<SnapshotNormativo> {
  const res = await apiClient.post<SnapshotNormativo>('/admin/parametros/snapshots', data);
  return res.data;
}

export async function listarCIIU(): Promise<CIIU[]> {
  const res = await apiClient.get<CIIU[]>('/admin/parametros/ciiu');
  return res.data;
}

export async function crearCIIU(data: CIIUCreate): Promise<CIIU> {
  const res = await apiClient.post<CIIU>('/admin/parametros/ciiu', data);
  return res.data;
}
