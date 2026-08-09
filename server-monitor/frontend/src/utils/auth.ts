export interface UserPayload {
  username: string;
  role: 'admin' | 'viewer';
}

export function getCurrentUserRole(): 'admin' | 'viewer' {
  const storedRole = localStorage.getItem('server_monitor_role');
  if (storedRole === 'admin' || storedRole === 'viewer') {
    return storedRole;
  }
  const token = localStorage.getItem('server_monitor_token');
  if (!token) return 'viewer';
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.role === 'admin' ? 'admin' : 'viewer';
  } catch (e) {
    return 'viewer';
  }
}
