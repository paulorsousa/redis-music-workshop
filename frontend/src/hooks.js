import { useState, useEffect, useCallback } from 'react';

/**
 * Hook for a section that fetches data independently with loading/error/timing state.
 */
export function useSection(fetchFn, deps = []) {
  const [state, setState] = useState({ loading: true, data: null, error: null, elapsed: null });

  const refresh = useCallback(() => {
    setState(s => ({ ...s, loading: true, error: null }));
    fetchFn()
      .then(({ data, elapsed }) => {
        setState({ loading: false, data, error: null, elapsed });
      })
      .catch(err => {
        setState(s => ({ loading: false, data: s.data, error: err.message, elapsed: null }));
      });
  }, deps);

  useEffect(() => { refresh(); }, [refresh]);

  return { ...state, refresh };
}

export function formatTime(ms) {
  if (ms == null) return '';
  if (ms < 1000) return `${Math.round(ms)} ms`;
  return `${(ms / 1000).toFixed(1)} s`;
}
