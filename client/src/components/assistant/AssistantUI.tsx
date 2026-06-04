import { useRef, useEffect, useState, useCallback } from "react";
import { Canvas } from "@react-three/fiber";
import { X, Mic, MicOff, MessageSquare } from "lucide-react";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";
import { setVoiceUiOpen } from "../../features/assistant/assistantSlice";
import { RootState } from "../../app/store";
import ParticleSphere from "./ParticleSphere";
import AnimatedCaption from "./AnimatedCaption";

// ─── main component ────────────────────────────────────────────────────────────
export default function VoiceAssistantUI() {
  const dispatch = useDispatch();
  const { session_id } = useParams<{ session_id?: string }>();
  const { user } = useSelector((state: RootState) => state.user);

  const [appState, setAppState] = useState<"idle" | "listening" | "responding">(
    "idle",
  );
  const [showCC, setShowCC] = useState(
    localStorage.getItem("showCC") === "true" ? true : false,
  );
  const [transcript, setTranscript] = useState("");
  const [interim, setInterim] = useState("");
  const [currentLineIndex, setCurrentLineIndex] = useState(0);

  const amplitudeRef = useRef(0);

  // ── Mic (listening) refs ───────────────────────────────────────────────────
  const streamRef = useRef<MediaStream | null>(null);
  const micAnalyserRef = useRef<AnalyserNode | null>(null);
  const micDataRef = useRef<Uint8Array<ArrayBuffer> | null>(null);

  // ── TTS audio (responding) refs ────────────────────────────────────────────
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const ttsAnalyserRef = useRef<AnalyserNode | null>(null);
  const ttsDataRef = useRef<Uint8Array<ArrayBuffer> | null>(null);

  // ── Misc ───────────────────────────────────────────────────────────────────
  const abortControllerRef = useRef<AbortController | null>(null);

  // ── Session management ─────────────────────────────────────────────────────
  const createNewSession = useCallback(async (userEmail: string) => {
    try {
      const res = await fetch(
        `${import.meta.env.VITE_SERVER_URL}/api/session/create`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            email: userEmail,
          }),
        },
      );

      const data = await res.json();
      return data.data;
    } catch (e) {
      console.log(e);
    }
  }, []);

  const getVoiceResponse = useCallback(
    async (signal: AbortSignal, currentSessionId: string) => {
      try {
        const res = await fetch(
          `${import.meta.env.VITE_SERVER_URL}/api/voice/completion`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            signal: signal,
            credentials: "include",
            body: JSON.stringify({
              email: user?.email!,
              session: parseInt(currentSessionId),
            }),
          },
        );

        const data = await res.json();
        // console.log("voice completion data",data);
        return data;
      } catch (error) {
        console.error("Error in Voice Response: ", error);
      }
    },
    [],
  );

  useEffect(() => {
    localStorage.setItem("showCC", showCC.toString());
  }, [showCC]);

  // Auto-start on mount
  useEffect(() => {
    startListening();
    return () => {
      stopAll();
    };
  }, []);

  // ── RAF loop: reads whichever analyser is active + track audio progress ────
  useEffect(() => {
    let id: number;
    const loop = () => {
      if (
        appState === "listening" &&
        micAnalyserRef.current &&
        micDataRef.current
      ) {
        // Real mic data — FIX: amplify by ×6 then clamp so particles visibly move
        micAnalyserRef.current.getByteFrequencyData(micDataRef.current);
        const sum = micDataRef.current.reduce((a, b) => a + b, 0);
        const raw = Math.min((sum / (micDataRef.current.length * 255)) * 6, 1);
        amplitudeRef.current = amplitudeRef.current * 0.8 + raw * 0.4 * 0.2;
      } else if (
        appState === "responding" &&
        ttsAnalyserRef.current &&
        ttsDataRef.current
      ) {
        // Real TTS audio data — no more fake Math.sin simulation
        ttsAnalyserRef.current.getByteFrequencyData(ttsDataRef.current);
        const sum = ttsDataRef.current.reduce((a, b) => a + b, 0);
        const raw = Math.min((sum / (ttsDataRef.current.length * 255)) * 6, 1);
        amplitudeRef.current = amplitudeRef.current * 0.85 + raw * 0.4 * 0.15;

        // Track audio playback and sync line index
        if (audioRef.current && transcript) {
          const { currentTime, duration } = audioRef.current;
          if (!isNaN(duration) && duration > 0) {
            const lines = transcript
              .split("\n")
              .filter((line) => line.trim() !== "");
            // Calculate which line should be displayed based on playback progress
            const progress = currentTime / duration;
            const lineIdx = Math.floor(progress * lines.length);
            setCurrentLineIndex(Math.min(lineIdx, lines.length - 1));
          }
        }
      } else {
        // Idle: decay back to perfect sphere
        amplitudeRef.current *= 0.88;
      }
      id = requestAnimationFrame(loop);
    };
    id = requestAnimationFrame(loop);
    return () => {
      cancelAnimationFrame(id);
    };
  }, [appState, transcript]);

  // ── Start listening ────────────────────────────────────────────────────────
  const startListening = async () => {
    // Handle session creation if needed
    let currentSessionId = session_id;
    if (!currentSessionId || currentSessionId.length === 0) {
      const s_id = await createNewSession(user?.email!);
      if (s_id) {
        currentSessionId = s_id.toString();
      } else {
        setTranscript("Error: Could not create session");
        stopAll();
        return;
      }
    }

    try {
      if (abortControllerRef.current) abortControllerRef.current.abort();
      abortControllerRef.current = new AbortController();

      // Open mic for amplitude visualisation only
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const micCtx = new AudioContext();
      const src = micCtx.createMediaStreamSource(stream);
      const micAnalyser = micCtx.createAnalyser();
      micAnalyser.fftSize = 256;
      src.connect(micAnalyser);
      micAnalyserRef.current = micAnalyser;
      micDataRef.current = new Uint8Array(micAnalyser.frequencyBinCount);

      setAppState("listening");
      setTranscript("");
      setInterim("Listening...");
      try {
        const data = await getVoiceResponse(
          abortControllerRef.current.signal,
          currentSessionId!,
        );

        if (data.audio_b64) {
          // ── Decode base64 → Blob → Object URL ────────────────────────────
          const audioBytes = Uint8Array.from(atob(data.audio_b64), (c) =>
            c.charCodeAt(0),
          );
          const blob = new Blob([audioBytes], { type: "audio/mpeg" });
          const url = URL.createObjectURL(blob);

          // ── Wire up Web Audio analyser for real responding amplitude ──────
          const audio = new Audio(url);
          audioRef.current = audio;

          const audioCtx = new AudioContext();
          audioCtxRef.current = audioCtx;

          const mediaSource = audioCtx.createMediaElementSource(audio);
          const ttsAnalyser = audioCtx.createAnalyser();
          ttsAnalyser.fftSize = 256;

          // source → analyser → destination (must reach destination to be heard)
          mediaSource.connect(ttsAnalyser);
          ttsAnalyser.connect(audioCtx.destination);

          ttsAnalyserRef.current = ttsAnalyser;
          ttsDataRef.current = new Uint8Array(ttsAnalyser.frequencyBinCount);

          setInterim("");
          setAppState("responding");
          setTranscript(data.text);
          setCurrentLineIndex(0);

          // ── audio.onended is the single source of truth for going idle ────
          audio.onended = () => {
            URL.revokeObjectURL(url);
            audioRef.current = null;
            ttsAnalyserRef.current = null;
            ttsDataRef.current = null;
            audioCtx.close();
            audioCtxRef.current = null;
            setAppState("idle");
            setTranscript("");
            setInterim("");
            setCurrentLineIndex(0);

            // // start listening again after a delay
            // setTimeout(() => {
            //   startListening();
            // }, 2000);
          };

          await audio.play();
        } else if (data.error) {
          setTranscript("Error: " + data.error);
          setInterim("");
          stopAll();
        }
      } catch (err: any) {
        if (err.name === "AbortError") {
          console.log("Fetch aborted");
        } else {
          console.error("API Error:", err);
          setTranscript("Connection error");
          setInterim("");
          stopAll();
        }
      } finally {
        abortControllerRef.current = null;
      }
    } catch (e) {
      console.warn("Microphone access denied:", e);
      setAppState("idle");
    }
  };

  // ── Stop everything ────────────────────────────────────────────────────────
  const stopAll = () => {
    // Mic
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    micAnalyserRef.current = null;
    micDataRef.current = null;

    // TTS audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.onended = null;
      audioRef.current = null;
    }
    if (audioCtxRef.current) {
      audioCtxRef.current.close();
      audioCtxRef.current = null;
    }
    ttsAnalyserRef.current = null;
    ttsDataRef.current = null;

    // In-flight fetch
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    setAppState("idle");
    setInterim("");
  };

  // ── Handlers ──────────────────────────────────────────────────────────────
  const handleMicToggle = () => {
    if (appState === "listening") {
      stopAll();
    } else {
      stopAll();
      startListening();
    }
  };

  const displayText =
    interim ||
    transcript ||
    (appState === "listening"
      ? "Listening..."
      : appState === "responding"
        ? "Responding..."
        : "Say something...");

  return (
    <>
      <div className="animate-fade-in-up-delay-1 h-full flex flex-col items-center justify-center gap-4 w-full bg-[#000017] font-sans overflow-hidden transition-all duration-500 relative">
        {/* ── CC Toggle ── */}
        <button
          onClick={() => setShowCC((v) => !v)}
          title={showCC ? "Hide captions" : "Show captions"}
          className="absolute top-[22px] right-[22px] z-30 flex items-center gap-[6px] px-3 py-[6px] rounded-lg text-xs tracking-[0.05em] cursor-pointer transition-all"
          style={{
            background: showCC ? "rgba(59,130,246,0.13)" : "transparent",
            border: `1px solid ${showCC ? "rgba(96,165,250,0.38)" : "rgba(55,65,81,0.55)"}`,
            color: showCC ? "#93c5fd" : "#4b5563",
          }}
        >
          <MessageSquare size={14} strokeWidth={1.6} />
          CC
        </button>

        {/* ── 3D Canvas ── */}
        <div className="w-[500px] h-[400px] relative z-10 transition-shadow duration-500">
          <Canvas
            camera={{ position: [0, 0, 5.5], fov: 55 }}
            style={{ background: "transparent" }}
          >
            <ParticleSphere amplitudeRef={amplitudeRef} appState={appState} />
          </Canvas>
        </div>

        {/* ── Status / caption text ── */}
        <div className="z-10 min-h-[160px] w-full max-w-[500px] text-center px-5 flex flex-col items-center justify-center gap-3">
          {showCC ? (
            <>
              {appState !== "idle" && (
                <div className="flex items-center gap-2 animate-fade-in-up">
                  <span
                    className="w-[7px] h-[7px] rounded-full inline-block shrink-0"
                    style={{
                      backgroundColor:
                        appState === "listening" ? "#eab308" : "#22c55e",
                      animation: "blink-dot 1s ease-in-out infinite",
                    }}
                  />
                  <span className="text-[11px] font-semibold uppercase tracking-widest text-gray-500">
                    {appState === "listening" ? "Listening" : "Responding"}
                  </span>
                </div>
              )}
              <AnimatedCaption
                text={displayText}
                isListening={appState === "listening"}
                currentLineIndex={currentLineIndex}
              />
            </>
          ) : (
            <p className="text-[#4b5563] text-xs m-0">Captions off</p>
          )}
        </div>

        {/* ── Action buttons ── */}
        <div className="flex items-center gap-5 z-10 mb-10">
          {/* Close */}
          <button
            onClick={() => {
              stopAll();
              dispatch(setVoiceUiOpen(false));
            }}
            aria-label="Close"
            className="w-14 h-14 rounded-full bg-[#0c111e] border border-[rgba(31,41,55,0.9)] flex items-center justify-center cursor-pointer transition-all duration-200 hover:bg-[#12192f]"
          >
            <X size={20} strokeWidth={1.5} className="text-[#4b5563]" />
          </button>

          {/* Mic toggle */}
          <button
            onClick={handleMicToggle}
            aria-label={
              appState === "listening" ? "Stop listening" : "Start listening"
            }
            className="w-16 h-16 rounded-full flex items-center justify-center cursor-pointer"
            style={{
              background:
                appState === "listening" ? "rgba(234,179,8,0.18)" : "#0c111e",
              border:
                appState === "listening"
                  ? "2px solid rgba(234,179,8,0.6)"
                  : "1px solid rgba(31,41,55,0.9)",
              transition: "all 0.25s",
              animation:
                appState === "listening"
                  ? "pulse-ring 1.6s ease-out infinite"
                  : "none",
            }}
          >
            {appState === "listening" ? (
              <MicOff size={22} strokeWidth={1.5} className="text-[#eab308]" />
            ) : (
              <Mic size={22} strokeWidth={1.5} className="text-[#4b5563]" />
            )}
          </button>
        </div>
      </div>
    </>
  );
}
