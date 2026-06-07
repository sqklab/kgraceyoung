export const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export function token(){ if (typeof window === 'undefined') return ''; return localStorage.getItem('gy_admin_token') || ''; }
export function authHeaders(extra: Record<string,string> = {}){ return { ...extra, Authorization: `Bearer ${token()}`}; }
export async function api(path: string, options: RequestInit = {}){
  const headers = new Headers(options.headers || {});
  if (!headers.has('Authorization')) headers.set('Authorization', `Bearer ${token()}`);
  if (options.body && !headers.has('Content-Type') && !(options.body instanceof FormData)) headers.set('Content-Type', 'application/json');
  const res = await fetch(`${API}/api/v1${path}`, { ...options, headers });
  const text = await res.text();
  let json: any = null; try { json = text ? JSON.parse(text) : null; } catch { json = text; }
  if (!res.ok) throw new Error(typeof json?.detail === 'string' ? json.detail : text || `HTTP ${res.status}`);
  return json;
}
export function money(v:any){ const n = Number(v || 0); return `$${n.toFixed(2)}`; }
export function short(id?: string){ return id ? id.slice(0,8) : '-'; }
