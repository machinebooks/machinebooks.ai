// Extraído de: LibroAIGateway/cap-26-gatewayclient-n7x-mcp.md
async runResponses(args: {
  instructions: string; input: string; purpose: string; jobId?: string;
}): Promise<string> {
  const extra: Record<string, string> = {};
  if (args.jobId) extra['X-N7x-Job-Id'] = args.jobId;
  const data = await this.post<ResponsesResult>(
    '/v1/responses',
    { instructions: args.instructions, input: args.input, purpose: args.purpose, stream: false },
    extra,
  );
  return extractResponsesText(data);
}
