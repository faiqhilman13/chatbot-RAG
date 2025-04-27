import { Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import HomePage from './pages/HomePage';
import SummarizationBot from './pages/SummarizationBot';
import VisualizationBot from './pages/VisualizationBot';
import ExtractionBot from './pages/ExtractionBot';
import FAQ from './pages/FAQ';

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="summarization" element={<SummarizationBot />} />
        <Route path="visualization" element={<VisualizationBot />} />
        <Route path="extraction" element={<ExtractionBot />} />
        <Route path="faq" element={<FAQ />} />
      </Route>
    </Routes>
  );
}

export default App; 