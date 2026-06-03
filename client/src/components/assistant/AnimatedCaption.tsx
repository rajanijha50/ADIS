import { useEffect, useMemo, useRef } from "react";

export default function AnimatedCaption({
  text,
  isListening,
  currentLineIndex = 0,
}: {
  text: string;
  isListening: boolean;
  currentLineIndex?: number;
}) {
  const lines = useMemo(() => {
    if (!text) return [];
    return text.split("\n").filter((line) => line.trim() !== "");
  }, [text]);

  // Only show lines up to current index
  const visibleLines = lines.slice(0, currentLineIndex + 1);

  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTo({
        top: containerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [visibleLines]);

  // For short status or single line / active listening state, render with a standard fade
  if (lines.length <= 1 || isListening) {
    return (
      <p className="text-[15px] font-normal tracking-[0.05em] text-[#a5c8fd] max-w-[480px] m-0 text-center animate-fade-in-up">
        {visibleLines.join(" ")}
      </p>
    );
  }

  return (
    <div
      ref={containerRef}
      className="max-h-[140px] w-full max-w-[480px] overflow-y-auto px-4 py-2 flex flex-col gap-2 scroll-smooth text-center select-none"
      style={{
        maskImage:
          "linear-gradient(to bottom, transparent 0%, white 20%, white 80%, transparent 100%)",
        WebkitMaskImage:
          "linear-gradient(to bottom, transparent 0%, white 20%, white 80%, transparent 100%)",
      }}
    >
      {visibleLines.map((line, idx) => (
        <p
          key={`${idx}-${line.slice(0, 15)}`}
          className="text-[15px] font-normal tracking-[0.05em] text-[#a5c8fd] m-0 opacity-0"
          style={{
            animation: "fade-in-up 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards",
            animationDelay: `${idx * 120}ms`,
          }}
        >
          {line}
        </p>
      ))}
    </div>
  );
};