export type ThemeMode = 'dark' | 'light' | 'system';

export function getStoredTheme(): ThemeMode {
  const stored = localStorage.getItem('server-monitor-theme');
  if (stored === 'dark' || stored === 'light' || stored === 'system') {
    return stored;
  }
  return 'system';
}

export function resolveTheme(mode: ThemeMode): 'dark' | 'light' {
  if (mode === 'system') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return mode;
}

export function applyTheme(mode: ThemeMode) {
  localStorage.setItem('server-monitor-theme', mode);
  const resolved = resolveTheme(mode);
  document.documentElement.setAttribute('data-theme', resolved);
}
