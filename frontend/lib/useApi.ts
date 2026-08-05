"use client";

import { useCallback, useEffect, useReducer, useState } from "react";
import { ApiError } from "./api";

interface State<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  notFound: boolean;
}

type Action<T> =
  | { type: "start" }
  | { type: "success"; data: T }
  | { type: "notFound" }
  | { type: "error"; message: string };

function reducer<T>(state: State<T>, action: Action<T>): State<T> {
  switch (action.type) {
    case "start":
      return { ...state, loading: true, error: null, notFound: false };
    case "success":
      return { data: action.data, loading: false, error: null, notFound: false };
    case "notFound":
      return { ...state, data: null, loading: false, notFound: true };
    case "error":
      return { ...state, loading: false, error: action.message };
  }
}

export function useApi<T>(fetcher: () => Promise<T>, deps: unknown[] = []) {
  const [state, dispatch] = useReducer(reducer<T>, {
    data: null,
    loading: true,
    error: null,
    notFound: false,
  });
  const [tick, setTick] = useState(0);

  const refetch = useCallback(() => setTick((t) => t + 1), []);

  useEffect(() => {
    let cancelled = false;
    dispatch({ type: "start" });

    fetcher()
      .then((result) => {
        if (!cancelled) dispatch({ type: "success", data: result });
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 404) {
          dispatch({ type: "notFound" });
        } else {
          dispatch({ type: "error", message: err instanceof Error ? err.message : "Unknown error" });
        }
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tick, ...deps]);

  return { ...state, refetch };
}
