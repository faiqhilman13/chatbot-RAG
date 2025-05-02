import DocumentUpload from '../components/DocumentUpload';
import Chat from '../components/Chat';

export default function ChatPage() {
  return (
    <div className="h-screen flex flex-col md:flex-row gap-4 p-4">
      {/* Document Upload Section */}
      <div className="md:w-1/3">
        <DocumentUpload />
      </div>

      {/* Chat Section */}
      <div className="flex-1 bg-white rounded-lg shadow">
        <Chat />
      </div>
    </div>
  );
} 