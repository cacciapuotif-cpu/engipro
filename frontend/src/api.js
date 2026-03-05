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
export const apiCompanies = { list: () => get('/companies'), get: (id) => get(`/companies/${id}`), create: (d) => post('/companies',d), update: (id,d) => put(`/companies/${id}`,d), delete: (id) => del(`/companies/${id}`) };
export const apiWorkers   = {
  list: () => get('/workers'),
  listByCompany: (cid) => get(`/workers/company/${cid}`),
  get: (id) => get(`/workers/${id}`),
  create: (d) => post('/workers',d),
  update: (id,d) => put(`/workers/${id}`,d),
  delete: (id) => del(`/workers/${id}`),
  search: (q) => get(`/workers/search?q=${encodeURIComponent(q)}`),
  setStatus: (id,s) => put(`/workers/${id}/status/${s}`),
};
export const apiDeadlines = { list: () => get('/deadlines'), create: (d) => post('/deadlines',d), update: (id,d) => put(`/deadlines/${id}`,d), delete: (id) => del(`/deadlines/${id}`), complete: (id) => post(`/deadlines/${id}/complete`,{}) };
export const apiDocuments = { list: () => get('/documents'), create: (d) => post('/documents',d), update: (id,d) => put(`/documents/${id}`,d), delete: (id) => del(`/documents/${id}`) };
export const apiTraining  = {
  courses: () => get('/training/courses'),
  createCourse: (d) => post('/training/courses',d),
  updateCourse: (id,d) => put(`/training/courses/${id}`,d),
  editionsByCourse: (cid) => get(`/training/courses/${cid}/editions`),
  createEdition: (d) => post('/training/editions',d),
  participationsByEdition: (eid) => get(`/training/editions/${eid}/participations`),
  participationsByWorker: (wid) => get(`/training/workers/${wid}/participations`),
  createParticipation: (d) => post('/training/participations',d),
};
export const apiMedical   = { protocols: () => get('/medical/protocols'), createProtocol: (d) => post('/medical/protocols',d), visits: () => get('/medical/visits'), createVisit: (d) => post('/medical/visits',d), completeVisit: (id,d) => post(`/medical/visits/${id}/complete`,d), cancelVisit: (id) => post(`/medical/visits/${id}/cancel`,{}) };
export const apiDPI       = { items: () => get('/dpi/items'), createItem: (d) => post('/dpi/items',d), assignmentsByWorker: (wid) => get(`/dpi/workers/${wid}/assignments`), createAssignment: (d) => post('/dpi/assignments',d), returnAssignment: (id) => post(`/dpi/assignments/${id}/return`,{}) };
export const apiAttendance= {
  timbratureByWorker: (wid) => get(`/attendance/timbrature/worker/${wid}`),
  timbratureByCompany: (cid) => get(`/attendance/timbrature/company/${cid}`),
  createTimbratura: (d) => post('/attendance/timbrature',d),
  records: () => get('/attendance/records'),
  approveRecord: (id) => post(`/attendance/records/${id}/approve`,{}),
};
