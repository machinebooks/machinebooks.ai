// Extraído de: LibroAIGateway/cap-26-gatewayclient-n7x-mcp.md
if (name === 'n7x_analyze_document') {
  const a = (args ?? {}) as { paths?: string[]; kind?: string; use_rag?: boolean };
  if (!Array.isArray(a.paths) || a.paths.length === 0) throw new Error('paths requerido');
  const jobId = randomUUID();
  const result = await analyzeDocument(gw, {
    paths: a.paths,
    kind: a.kind === 'private' ? 'private' : 'public',
    useRag: a.use_rag,
    jobId,
  });
  return done(name, jobId, result);
}
