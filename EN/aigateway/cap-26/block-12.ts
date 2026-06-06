// Extracted from: LibroAIGateway/cap-26-gatewayclient-n7x-mcp.md
const JOB_META: Record<string, { type: string; subtype: string; title: string; activityKey: string }> = {
  n7x_evaluate_proposal: { type: 'evaluation', subtype: 'evaluation', title: 'Evaluación de propuesta', activityKey: 'evaluar-propuesta' },
  n7x_analyze_document: { type: 'document', subtype: 'document_analysis', title: 'Análisis de documento', activityKey: 'analizar-documento' },
  // ... ~15 more entries
};

async function done(toolName: string, jobId: string, result: unknown) {
  const meta = JOB_META[toolName];
  if (meta) {
    const status = (result as { status?: string } | null)?.status === 'failed' ? 'failed' : 'completed';
    try {
      await gw.persistJob({ id: jobId, type: meta.type, subtype: meta.subtype, title: meta.title, resultJson: result, status, activityKey: meta.activityKey });
    } catch {
      /* best-effort: the portal won't show this job, but the result already goes to Claude */
    }
  }
  const header = meta ? `job_id: ${jobId}\\n\\n` : '';
  return { content: [{ type: 'text', text: header + JSON.stringify(result, null, 2) }] };
}
