import React, { useRef, useMemo, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { X, Mic, MicOff, MessageSquare } from 'lucide-react';
import { useDispatch } from 'react-redux';
import { setVoiceUiOpen } from '../features/assistant/assistantSlice';

// ─── constants ───────────────────────────────────────────────────────────────
const COUNT  = 3800;
const RADIUS = 2.6;

// ─── 3D particle sphere ───────────────────────────────────────────────────────
const ParticleSphere = ({ amplitudeRef }) => {
  const ref = useRef(null);

  // Build geometry buffers once
  const { orig, pos, phases } = useMemo(() => {
    const orig   = new Float32Array(COUNT * 3);
    const pos    = new Float32Array(COUNT * 3);
    const phases = new Float32Array(COUNT);
    for (let i = 0; i < COUNT; i++) {
      const theta = Math.random() * 2 * Math.PI;
      const phi   = Math.acos(2 * Math.random() - 1);
      const r     = Math.cbrt(Math.random()) * RADIUS;
      const x = r * Math.sin(phi) * Math.cos(theta);
      const y = r * Math.cos(phi);
      const z = r * Math.sin(phi) * Math.sin(theta);
      orig[i*3]   = pos[i*3]   = x;
      orig[i*3+1] = pos[i*3+1] = y;
      orig[i*3+2] = pos[i*3+2] = z;
      phases[i] = Math.random() * Math.PI * 2;
    }
    return { orig, pos, phases };
  }, []);

  useFrame(({ clock }) => {
    if (!ref.current) return;
    const t   = clock.getElapsedTime();
    const amp = amplitudeRef.current;

    // Slow rotation
    ref.current.rotation.y = t * 0.14;
    ref.current.rotation.x = t * 0.07;

    // Displace particles outward based on voice amplitude + per-particle wave
    const attr = ref.current.geometry.attributes.position;
    const arr  = attr.array;
    for (let i = 0; i < COUNT; i++) {
      const ox = orig[i*3], oy = orig[i*3+1], oz = orig[i*3+2];
      // Each particle has its own oscillation phase so the sphere "breathes" unevenly
      const wave = 0.5 + 0.5 * Math.sin(t * 5.5 + phases[i]);
      const push = 1 + amp * 2.4 * wave;
      arr[i*3]   = ox * push;
      arr[i*3+1] = oy * push;
      arr[i*3+2] = oz * push;
    }
    attr.needsUpdate = true;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={1500}
          array={pos}
          itemSize={3}//dimension
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.065}
        color="white"
        transparent
        opacity={0.89}
        sizeAttenuation
        depthWrite={false}
      />
    </points>
  );
};


// ─── main component ────────────────────────────────────────────────────────────
export default function VoiceAssistantNewUI() {
  const dispatch = useDispatch();
  const [listening, setListening]   = useState(false);
  const [showCC, setShowCC]      = useState(localStorage.getItem("showCC") === "true" ? true : false);
  const [transcript, setTranscript]  = useState('');
  const [interim, setInterim]     = useState('');
  // const [opened, setOpened]      = useState(status);

  const amplitudeRef = useRef(0);
  const analyserRef  = useRef(null);
  const dataRef      = useRef(null);
  const streamRef    = useRef(null);
  const recRef       = useRef(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    localStorage.setItem("showCC", showCC.toString());
  }, [showCC]);
  // useEffect(() => {
  // console.log("interim: ", interim)
  // console.log("transcript: ",transcript)

  // }, [interim, transcript])

  // ── Always-running RAF loop: reads analyser or slowly decays amplitude ──────
  useEffect(() => {
    let id;
    const loop = () => {
      if (analyserRef.current && dataRef.current) {
        analyserRef.current.getByteFrequencyData(dataRef.current);
        const sum = dataRef.current.reduce((a, b) => a + b, 0);
        const raw = sum / (dataRef.current.length * 255);
        // Exponential smoothing
        amplitudeRef.current = amplitudeRef.current * 0.80 + raw * 0.20;
      } else {
        amplitudeRef.current *= 0.88;  // decay when not listening
      }
      id = requestAnimationFrame(loop);
    };
    id = requestAnimationFrame(loop);
    return () => {
      cancelAnimationFrame(id);
      streamRef.current?.getTracks().forEach(t => t.stop());
      try { recRef.current?.stop(); } catch (_) {}
    };
  }, []);

  // ── Start mic + speech recognition ─────────────────────────────────────────
  const startListening = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Web Audio API for amplitude
      const ctx      = new AudioContext();
      const src      = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 256;
      src.connect(analyser);
      analyserRef.current = analyser;
      dataRef.current     = new Uint8Array(analyser.frequencyBinCount);

      setListening(true);
      setTranscript('');
      setInterim('Listening...');

      // Abort previous request if any
      if (abortControllerRef.current) abortControllerRef.current.abort();
      abortControllerRef.current = new AbortController();

      // Call Backend API for transcription
      try {
        const response = await fetch(`${import.meta.env.VITE_SERVER_URL}/api/voice/listen`, {
          signal: abortControllerRef.current.signal,
          credentials: "include",
        });
        const data = await response.json();
        
        if (data.text) {
          console.log("data text: ",data.text)
          setTranscript(data.text);
          setInterim('');
        } else if (data.error) {
          setTranscript('Error: ' + data.error);
          setInterim('');
        }
      } catch (err: any) {
        if (err.name === 'AbortError') {
          console.log('Fetch aborted');
        } else {
          console.error('API Error:', err);
          setTranscript('Connection error');
          setInterim('');
        }
      } finally {
        setListening(false);
        stopListening();
        abortControllerRef.current = null;
      }

    } catch (e) {
      console.warn('Microphone access denied:', e);
    }
  };

  const handleSpeak = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_SERVER_URL}/api/voice/speak`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: String(transcript) }),
        credentials: "include",
      });
      const data = await response.json();
      if (data.error) {
        console.error('Data Error:', data.error);
      }
      console.log(data.status)
    } catch (err) {
      console.error('Error:', err);
    }
  };

  useEffect(() => {
    console.log("transcript: ", transcript)
    // if (transcript && transcript.length > 0 && !listening) {
    //   handleSpeak();
    // }
  }, [transcript]);

  // ── Stop mic + recognition ──────────────────────────────────────────────────
  const stopListening = () => {
    streamRef.current?.getTracks().forEach(t => t.stop());
    streamRef.current  = null;
    analyserRef.current = null;
    dataRef.current    = null;
    try { recRef.current?.stop(); } catch (_) {}
    recRef.current = null;
    
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    setListening(false);
    setInterim('');
  };

  const handleMicToggle = () => listening ? stopListening() : startListening();

  const handleStop = () => {
    stopListening();
    setTranscript('');
    setInterim('');
  };

  // ── derived UI values ───────────────────────────────────────────────────────
  const accentBlue  = `rgba(96, 165, 250, 0.85)`;
  const dimBlue     = `rgba(30, 58, 138, 0.55)`;
  const displayText = interim || transcript || (listening ? 'Listening...' : 'Say something...');

  return (
    <>
      <div className={`
        animate-fade-in-up-delay-1 border-0 border-red-500 flex flex-col items-center justify-center gap-4 w-full bg-[#000017] font-sans overflow-hidden transition-all duration-500
      `}>

        {/* ── Top-right Caption Toggle ── */}
        <button
          onClick={() => setShowCC(v => !v)}
          title={showCC ? 'Hide captions' : 'Show captions'}
          className={`
            absolute top-[22px] right-[22px] z-30 flex items-center gap-[6px]
            px-3 py-[6px] rounded-lg text-xs tracking-[0.05em] cursor-pointer transition-all duration-[250ms]
          `}
          style={{
            background: showCC ? 'rgba(59,130,246,0.13)' : 'transparent',
            border: `1px solid ${showCC ? 'rgba(96,165,250,0.38)' : 'rgba(55,65,81,0.55)'}`,
            color: showCC ? '#93c5fd' : '#4b5563',
          }}
        >
          <MessageSquare size={14} strokeWidth={1.6} />
          CC
        </button>

        {/* ── 3D Canvas with styled frame ── */}
        <div className="p-10 w-200 h-100 relative z-10 transition-shadow duration-500">
          <Canvas
            camera={{ position: [0, 0, 5.5], fov: 55 }}
            style={{ background: 'transparent' }}
          >
            <ParticleSphere amplitudeRef={amplitudeRef} />
          </Canvas>
        </div>

        {/* ── Live status / caption text ── */}
        <div className="z-10 min-h-[30px] max-w-[480px] text-center px-5 flex items-center justify-center gap-2">
          {listening && (
            <span
              className="w-[7px] h-[7px] rounded-full bg-[#60a5fa] inline-block shrink-0"
              style={{ animation: 'blink-dot 1s ease-in-out infinite' }}
            />
          )}
          {showCC ? (
            <p
              className="text-[15px] font-normal tracking-[0.05em] m-0 transition-colors duration-250"
              style={{ color: interim ? '#a5c8fd' : '#3a5a9e' }}
            >
              {displayText}
            </p>
          ) : (
            <p className="text-[#252525] text-xs m-0">
              Captions off
            </p>
          )}
        </div>

        {/* ── Action buttons ── */}
        <div className="flex items-center gap-5 z-10 mb-10">

          {/* Stop & clear button */}
          <button
            onClick={handleStop}
            aria-label="Stop and clear"
            className="
              w-16 h-16 rounded-full bg-[#0c111e]
              border border-[rgba(31,41,55,0.9)]
              flex items-center justify-center cursor-pointer
              transition-all duration-200 hover:bg-[#12192f]
            "
          >
            <X onClick={() => dispatch(setVoiceUiOpen(false))} size={22} strokeWidth={1.5} className="text-[#4b5563]" />
          </button>

          {/* Mic toggle — pulses when listening */}
          <button
            onClick={handleMicToggle}
            aria-label={listening ? 'Stop listening' : 'Start listening'}
            className="w-16 h-16 rounded-full flex items-center justify-center cursor-pointer"
            style={{
              background: listening ? 'rgba(59,130,246,0.18)' : '#0c111e',
              border: listening
                ? '2px solid rgba(96,165,250,0.6)'
                : '1px solid rgba(31,41,55,0.9)',
              transition: 'background 0.25s, border 0.25s',
              animation: listening ? 'pulse-ring 1.6s ease-out infinite' : 'none',
            }}
          >
            {listening
              ? <MicOff size={22} strokeWidth={1.5} className="text-[#60a5fa]" />
              : <Mic size={22} strokeWidth={1.5} className="text-[#4b5563]" />
            }
          </button>
        </div>

      </div>
    </>
  );
}