import { Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';
import SummarizationBot from './pages/SummarizationBot';
import VisualizationBot from './pages/VisualizationBot';
import ExtractionBot from './pages/ExtractionBot';
import FAQ from './pages/FAQ';
import SqlAgent from './pages/SqlAgent';
import ReportGeneration from './pages/ReportGeneration';
import DocumentReview from './pages/DocumentReview';
import Classification from './pages/Classification';

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="summarization" element={<SummarizationBot />} />
        <Route path="visualization" element={<VisualizationBot />} />
        <Route path="extraction" element={<ExtractionBot />} />
        <Route path="sql-agent" element={<SqlAgent />} />
        <Route path="report-generation" element={<ReportGeneration />} />
        <Route path="document-review" element={<DocumentReview />} />
        <Route path="classification" element={<Classification />} />
        <Route path="faq" element={<FAQ />} />
      </Route>
    </Routes>
  );
}

export default App; 