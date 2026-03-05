/**
 * EngiPro API Client
 */
const API_BASE = '/api/v1';
let _token = localStorage.getItem('engipro_token') || null;
export const auth = {
  setToken: (t) => { _token = t; if (t) localStorage.setItem('engipro_token', t); else localStorage.removeItem('engipro_token'); },
  getToken: () => _token,
  isLoggedIn: () => !!_token,
};
async function req(method, path, body = null) {
  const headers = { 'Content-Type': 'application/json' };
  if (_token) headers['Authorization'] = `Bearer ${_token}`;
  const res = await fetch(`${API_BASE}${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined });
  if (res.status === 401) { auth.setToken(null); window.location.reload(); }
  if (!res.ok) { const err = await res.json().catch(() => ({ detail: res.statusText })); throw new Error(err.detail || 'Errore API'); }
  if (res.status === 204) return null;
  return res.json();
}
const get  = (path)       => req('GET',    path);
const post = (path, body) => req('POST',   path, body);
const put  = (path, body) => req('PUT',    path, body);
const del  = (path)       => req('DELETE', path);
export const apiAuth      = { login: (e,p) => post('/auth/login', {email:e,password:p}), me: () => get('/auth/me'), logout: () => post('/auth/logout',{}) };
export const apiCompanies = { list: (p={}) => get('/companies?'+new URLSearchParams(p)), get: (id) => get(`/companies/${id}`), create: (d) => post('/companies',d), update: (id,d) => put(`/companies/${id}`,d), delete: (id) => del(`/companies/${id}`) };
export const apiWorkers   = { list: (p={}) => get('/workers?'+new URLSearchParams(p)), get: (id) => get(`/workers/${id}`), create: (d) => post('/workers',d), update: (id,d) => put(`/workers/${id}`,d), delete: (id) => del(`/workers/${id}`), search: (q) => get(`/workers/search?q=${encodeURIComponent(q)}`) };
export const apiDeadlines = { list: (p={}) => get('/deadlines?'+new URLSearchParams(p)), create: (d) => post('/deadlines',d), update: (id,d) => put(`/deadlines/${id}`,d), delete: (id) => del(`/deadlines/${id}`), complete: (id) => post(`/deadlines/${id}/complete`,{}) };
export const apiDocuments = { list: (p={}) => get('/documents?'+new URLSearchParams(p)), create: (d) => post('/documents',d), update: (id,d) => put(`/documents/${id}`,d), delete: (id) => del(`/documents/${id}`) };
export const apiTraining  = { courses: (p={}) => get('/training/courses?'+new URLSearchParams(p)), createCourse: (d) => post('/training/courses',d), editions: (p={}) => get('/training/editions?'+new URLSearchParams(p)), createEdition: (d) => post('/training/editions',d), participations: (p={}) => get('/training/participations?'+new URLSearchParams(p)), createParticipation: (d) => post('/training/participations',d) };
export const apiMedical   = { protocols: (p={}) => get('/medical/protocols?'+new URLSearchParams(p)), createProtocol: (d) => post('/medical/protocols',d), visits: (p={}) => get('/medical/visits?'+new URLSearchParams(p)), createVisit: (d) => post('/medical/visits',d), completeVisit: (id,d) => post(`/medical/visits/${id}/complete`,d), cancelVisit: (id) => post(`/medical/visits/${id}/cancel`,{}) };
export const apiDPI       = { items: (p={}) => get('/dpi/items?'+new URLSearchParams(p)), createItem: (d) => post('/dpi/items',d), assignments: (p={}) => get('/dpi/assignments?'+new URLSearchParams(p)), createAssignment: (d) => post('/dpi/assignments',d), returnAssignment: (id) => post(`/dpi/assignments/${id}/return`,{}) };
export const apiAttendance= { timbrature: (p={}) => get('/attendance/timbrature?'+new URLSearchParams(p)), createTimbratura: (d) => post('/attendance/timbrature',d), records: (p={}) => get('/attendance/records?'+new URLSearchParams(p)), approveRecord: (id) => post(`/attendance/records/${id}/approve`,{}) };
