import { useState, useEffect, useCallback, useRef } from "react";

/**
 * Hook for a section that fetches data independently with loading/error/timing state.
 */
export function useSection(fetchFn, deps = []) {
  const [state, setState] = useState({
    loading: true,
    data: null,
    error: null,
    elapsed: null,
  });

  const abortRef = useRef(null);

  const refresh = useCallback(() => {
    // Abort any in-flight request before starting a new one
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setState((s) => ({ ...s, loading: true, error: null }));
    fetchFn(controller.signal)
      .then(({ data, elapsed }) => {
        if (controller.signal.aborted) return;
        setState({ loading: false, data, error: null, elapsed });
      })
      .catch((err) => {
        if (controller.signal.aborted) return;
        setState((s) => ({
          loading: false,
          data: s.data,
          error: err.message,
          elapsed: null,
        }));
      });
  }, deps);

  useEffect(() => {
    refresh();
    return () => {
      // Abort on unmount / before re-running the effect (StrictMode)
      if (abortRef.current) abortRef.current.abort();
    };
  }, [refresh]);

  return { ...state, refresh };
}

export function formatTime(ms) {
  if (ms == null) return "";
  if (ms < 1000) return `${Math.round(ms)} ms`;
  return `${(ms / 1000).toFixed(1)} s`;
}
