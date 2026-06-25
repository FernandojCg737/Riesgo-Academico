"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Mic, MicOff, Send, Volume2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { apiClient, ApiError } from "@/lib/api-client";
import type { ChatMessage } from "@/lib/types";
import { useDataset } from "@/contexts/dataset-context";

interface SpeechRecognitionResultLike {
  resultIndex: number;
  results: { length: number; [index: number]: { isFinal: boolean; [index: number]: { transcript: string } } };
}

// Tiempo de silencio para asumir que la persona terminó de hablar y disparar
// el envío solo; antes de la primera palabra se tolera más espera (arranque).
const SILENCIO_TRAS_HABLAR_MS = 1800;
const SILENCIO_INICIAL_MS = 6000;

const ERRORES_RECONOCIMIENTO: Record<string, string> = {
  "no-speech": "No se detectó voz. Acercate al micrófono e intentá de nuevo.",
  "audio-capture": "No se encontró un micrófono disponible.",
  "not-allowed": "Permiso de micrófono denegado. Habilitalo en el navegador.",
  network: "Error de red en el reconocimiento de voz. Revisá tu conexión.",
  aborted: "",
};

const PREGUNTAS_SUGERIDAS: { categoria: string; preguntas: string[] }[] = [
  {
    categoria: "Datos académicos",
    preguntas: [
      "¿Cuál es la tasa de riesgo académico en el dataset histórico?",
      "¿Qué carrera tiene el mayor porcentaje de estudiantes en riesgo?",
      "¿Cómo influye el PPA y el PPAC en el riesgo académico?",
      "¿Repetir una materia aumenta la probabilidad de riesgo?",
    ],
  },
  {
    categoria: "Modelo predictivo",
    preguntas: [
      "¿Qué modelo ganó y por qué se eligió sobre los demás?",
      "¿Qué significa el Recall y por qué es la métrica más importante aquí?",
      "¿Cuál es el Accuracy y el F1-Score del modelo final?",
      "¿Qué variables usa el modelo para predecir el riesgo académico?",
    ],
  },
  {
    categoria: "Encuesta de IA",
    preguntas: [
      "¿Cómo se relaciona el uso de IA con el riesgo académico?",
      "¿Qué variable de la encuesta se correlaciona más con el riesgo?",
      "¿La dependencia de IA está asociada a peor rendimiento?",
    ],
  },
  {
    categoria: "Metodología",
    preguntas: [
      "¿Cómo se calcula el umbral de aprobación (51%)?",
      "¿Qué es SHAP y cómo explica una predicción individual?",
      "¿Por qué se usó GridSearchCV para entrenar los modelos?",
      "¿Cuáles son los criterios definidos en el dataset?",
    ],
  },
];

export function ChatPanel() {
  const { datasetId } = useDataset();
  const [mensajes, setMensajes] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [escuchando, setEscuchando] = useState(false);
  const [reconocimientoDisponible, setReconocimientoDisponible] = useState(true);
  const reconocimientoRef = useRef<unknown>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [mensajes]);

  useEffect(() => {
    const SpeechRecognitionCtor =
      (window as unknown as { SpeechRecognition?: unknown; webkitSpeechRecognition?: unknown }).SpeechRecognition ||
      (window as unknown as { webkitSpeechRecognition?: unknown }).webkitSpeechRecognition;
    setReconocimientoDisponible(!!SpeechRecognitionCtor);
  }, []);

  async function enviarMensaje(texto: string, autoHablar = false) {
    if (!texto.trim() || enviando) return;
    const nuevoHistorial: ChatMessage[] = [...mensajes, { role: "user", content: texto }];
    setMensajes(nuevoHistorial);
    setInput("");
    setEnviando(true);
    try {
      const { respuesta } = await apiClient.post<{ respuesta: string }>("/api/chatbot/ask", {
        messages: nuevoHistorial,
        dataset_id: datasetId,
      });
      setMensajes([...nuevoHistorial, { role: "assistant", content: respuesta }]);
      if (autoHablar) leerEnVozAlta(respuesta);
    } catch (err) {
      const mensaje = err instanceof ApiError ? err.message : "Error de red al consultar el chatbot";
      toast.error("No se pudo obtener respuesta", { description: mensaje });
      setMensajes(nuevoHistorial);
    } finally {
      setEnviando(false);
    }
  }

  function alternarMicrofono() {
    if (!reconocimientoDisponible) return;

    if (escuchando) {
      (reconocimientoRef.current as { stop: () => void } | null)?.stop();
      setEscuchando(false);
      return;
    }

    const SpeechRecognitionCtor =
      (window as unknown as { SpeechRecognition?: new () => unknown }).SpeechRecognition ||
      (window as unknown as { webkitSpeechRecognition?: new () => unknown }).webkitSpeechRecognition;
    if (!SpeechRecognitionCtor) return;

    const reconocimiento = new (SpeechRecognitionCtor as new () => {
      lang: string;
      interimResults: boolean;
      continuous: boolean;
      onresult: (e: SpeechRecognitionResultLike) => void;
      onend: () => void;
      onerror: (e: { error: string }) => void;
      start: () => void;
      stop: () => void;
    })();

    // "continuous" evita que el reconocimiento se corte ante una pausa natural
    // al hablar; en su lugar, un temporizador propio de silencio decide cuándo
    // la persona terminó de hablar y detiene la escucha automáticamente.
    reconocimiento.lang = "es-BO";
    reconocimiento.interimResults = true;
    reconocimiento.continuous = true;

    const fragmentos: string[] = [];
    let silenceTimer: ReturnType<typeof setTimeout>;
    const armarTimerSilencio = (ms: number) => {
      clearTimeout(silenceTimer);
      silenceTimer = setTimeout(() => reconocimiento.stop(), ms);
    };

    reconocimiento.onresult = (event: SpeechRecognitionResultLike) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          fragmentos.push(event.results[i][0].transcript);
        }
      }
      // Cualquier resultado (interino o final) indica que la persona sigue
      // hablando: reiniciamos la cuenta de silencio.
      armarTimerSilencio(SILENCIO_TRAS_HABLAR_MS);
    };
    reconocimiento.onend = () => {
      clearTimeout(silenceTimer);
      setEscuchando(false);
      const texto = fragmentos.join(" ").trim();
      if (texto) enviarMensaje(texto, true);
    };
    reconocimiento.onerror = (event: { error: string }) => {
      clearTimeout(silenceTimer);
      setEscuchando(false);
      const mensaje = ERRORES_RECONOCIMIENTO[event.error];
      if (mensaje) toast.error("Reconocimiento de voz", { description: mensaje });
    };

    reconocimientoRef.current = reconocimiento;
    reconocimiento.start();
    armarTimerSilencio(SILENCIO_INICIAL_MS);
    setEscuchando(true);
  }

  function leerEnVozAlta(texto: string) {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(texto);
    utterance.lang = "es-ES";
    window.speechSynthesis.speak(utterance);
  }

  return (
    <div className="flex flex-col h-[70vh] border rounded-lg bg-card">
      <ScrollArea className="flex-1 p-4">
        {mensajes.length === 0 && (
          <div className="py-6 space-y-6">
            <p className="text-sm text-muted-foreground text-center">
              Preguntame sobre los datos académicos, el modelo predictivo o sus métricas. Tocá el micrófono, hablá tu
              pregunta y dejá de hablar: se envía sola apenas detecto el silencio, y te respondo también por voz.
            </p>
            <div className="space-y-4">
              <p className="text-xs font-medium text-muted-foreground text-center">
                O probá con alguna de estas preguntas:
              </p>
              {PREGUNTAS_SUGERIDAS.map((grupo) => (
                <div key={grupo.categoria}>
                  <p className="text-xs font-medium text-muted-foreground mb-1.5">{grupo.categoria}</p>
                  <div className="flex flex-wrap gap-2">
                    {grupo.preguntas.map((pregunta) => (
                      <button
                        key={pregunta}
                        type="button"
                        onClick={() => enviarMensaje(pregunta, true)}
                        disabled={enviando}
                        className="rounded-full border bg-muted/50 px-3 py-1.5 text-xs text-left hover:bg-muted disabled:opacity-50 transition-colors"
                      >
                        {pregunta}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        <div className="space-y-4">
          {mensajes.map((m, i) => (
            <div key={i} className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              {m.role === "assistant" && (
                <Avatar className="h-8 w-8 shrink-0">
                  <AvatarFallback className="bg-primary text-primary-foreground text-xs">IA</AvatarFallback>
                </Avatar>
              )}
              <div
                className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                  m.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                }`}
              >
                <div className="prose prose-sm dark:prose-invert max-w-none [&_p]:m-0">
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                </div>
                {m.role === "assistant" && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 px-1 mt-1 text-muted-foreground"
                    onClick={() => leerEnVozAlta(m.content)}
                  >
                    <Volume2 className="h-3 w-3" />
                  </Button>
                )}
              </div>
            </div>
          ))}
          {enviando && <p className="text-xs text-muted-foreground">Pensando...</p>}
        </div>
        <div ref={scrollRef} />
      </ScrollArea>

      <div className="border-t p-3 flex gap-2 items-end">
        <Button
          type="button"
          variant={escuchando ? "default" : "outline"}
          size="icon"
          onClick={alternarMicrofono}
          disabled={!reconocimientoDisponible}
          title={reconocimientoDisponible ? "Dictar pregunta" : "Tu navegador no soporta reconocimiento de voz"}
        >
          {escuchando ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
        </Button>
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              enviarMensaje(input);
            }
          }}
          placeholder="Escribí o dictá tu pregunta..."
          className="min-h-10 resize-none"
          rows={1}
        />
        <Button type="button" size="icon" onClick={() => enviarMensaje(input)} disabled={enviando || !input.trim()}>
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
