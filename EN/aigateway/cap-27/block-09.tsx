// Extracted from: LibroAIGateway/cap-27-frontend-architecture-realtime.md
// admin-panel/src/App.tsx — admin routing (simplified form)
import { BrowserRouter, Routes, Route } from 'react-router-dom';

const Dashboard   = lazy(() => import('./pages/Dashboard'));
const ModelConfig = lazy(() => import('./pages/ModelConfig'));

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/models" element={<ModelConfig />} />
      </Routes>
    </BrowserRouter>
  );
}
