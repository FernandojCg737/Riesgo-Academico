import { PageHeader } from "@/components/layout/page-header";
import { ChatPanel } from "@/components/chat/chat-panel";

export default function ChatbotPage() {
  return (
    <div>
      <PageHeader
        title="Chatbot Analítico"
        description="Preguntá en lenguaje natural (o por voz) sobre los datos académicos, el modelo predictivo y sus métricas."
      />
      <ChatPanel />
    </div>
  );
}
