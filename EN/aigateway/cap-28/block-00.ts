// Extracted from: LibroAIGateway/cap-28-admin-operations-ai.md
// admin-panel/src/App.tsx (route tree excerpt)
<Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
  <Route index element={<Dashboard />} />
  <Route path="users" element={<Users />} />
  <Route path="users/import" element={<UsersImport />} />
  <Route path="teams" element={<Teams />} />
  <Route path="licenses" element={<Licenses />} />
  <Route path="organizations" element={<Organizations />} />
  <Route path="ai-prompts" element={<AIPrompts />} />
  <Route path="llm-models" element={<LLMModelsHub />} />
  <Route path="semantic-cache" element={<SemanticCache />} />
  <Route path="ai-quality" element={<AIQuality />} />
  <Route path="ai-debug" element={<AIDebug />} />
  <Route path="ai-budget" element={<AIBudget />} />
  <Route path="chat-feedback" element={<ChatFeedback />} />
</Route>
