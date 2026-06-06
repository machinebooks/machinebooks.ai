// Extraído de: LibroAIGateway/cap-30-portal-usuario.md
// admin-panel/src/portal/usePortalData.tsx
export function PortalDataProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<State>({ status: 'loading' });
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false;
    portalApi.get('/api/v1/me/portal')
      .then((r) => {
        if (!cancelled) return;
        setState({ status: 'ready', data: r.data.data });
      })
      .catch(() => { if (!cancelled) setState({ status: 'error' }); });
    return () => { cancelled = true; };
  }, [tick]);

  return (
    <PortalDataContext.Provider value={{ state, reload: () => setTick(n => n + 1) }}>
      {children}
    </PortalDataContext.Provider>
  );
}
