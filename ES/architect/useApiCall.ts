// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
// useApiCall.ts — Hook genérico para llamadas a la API con manejo de errores
import { useState, useCallback } from 'react';
import toast from 'react-hot-toast';
import { AxiosError } from 'axios';

interface ApiCallState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}

type ApiFunction<T, A extends unknown[]> = (...args: A) => Promise<T>;

export function useApiCall<T, A extends unknown[]>(
  apiFn: ApiFunction<T, A>,
  options: {
    successMessage?: string;
    errorMessage?: string;
    showSuccessToast?: boolean;
  } = {}
) {
  const [state, setState] = useState<ApiCallState<T>>({
    data: null,
    isLoading: false,
    error: null,
  });

