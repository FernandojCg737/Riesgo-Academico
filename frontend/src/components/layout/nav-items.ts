import {
  LayoutDashboard,
  Database,
  Gauge,
  BrainCircuit,
  LineChart,
  Sparkles,
  FileText,
  BookOpen,
  MessageCircle,
} from "lucide-react";

export const NAV_ITEMS = [
  { href: "/", label: "Inicio", icon: LayoutDashboard },
  { href: "/datos-academicos", label: "Datos Académicos", icon: Database },
  { href: "/prediccion", label: "Predicción", icon: Gauge },
  { href: "/entrenamiento", label: "Entrenamiento", icon: BrainCircuit },
  { href: "/evaluacion", label: "Evaluación", icon: LineChart },
  { href: "/chatbot", label: "Chatbot Analítico", icon: MessageCircle },
  { href: "/encuesta", label: "Encuesta de IA", icon: Sparkles },
  { href: "/reportes", label: "Reportes", icon: FileText },
  { href: "/metodologia", label: "Metodología", icon: BookOpen },
];
