import {
  Bot,
  Mic,
  Volume2,
  Sparkles,
  MessageSquare,
  Cpu,
  Terminal,
  Zap,
  Sliders,
  BrainCircuit,
  Type,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { RootState } from "../../app/store";
import { SendNotification } from "../SendNotification";

export default function AssistantSettings() {
  const { name: assistantName } = useSelector(
    (state: RootState) => state.assistant,
  );
  const { user } = useSelector((state: RootState) => state.user);
  console.log(user);
  const [toneStyle, setToneStyle] = useState("friendly");
  const [systemPrompt, setSystemPrompt] = useState("");

  // State for Model Configuration
  const llmProviderOptions = ["gemini", "groq", "cerebras"];
  const [llmModelOptions, setLlmModelOptions] = useState([
    "gemini-2.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
  ]);
  const [llmProvider, setLlmProvider] = useState("gemini");
  const [modelSelection, setModelSelection] = useState("gemini-2.5-flash-lite");
  const [creativity, setCreativity] = useState(50);
  const [maxTokens, setMaxTokens] = useState(2048);

  // State for Chat Behavior
  const [autoScroll, setAutoScroll] = useState(true);
  const [enterToSend, setEnterToSend] = useState(true);
  const [markdownRendering, setMarkdownRendering] = useState(true);
  const [codeHighlighting, setCodeHighlighting] = useState(true);

  // State for Voice Settings
  const [alwaysListening, setAlwaysListening] = useState(true);
  const [spokenResponses, setSpokenResponses] = useState(false);

  const loadPreferences = async () => {
    try {
      const req = await fetch(
        `${import.meta.env.VITE_SERVER_URL}/api/user/${user?.email}/preferences`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        },
      );
      const res = await req.json();
      if (res.success) {
        console.log(res.data);
        setLlmProvider(res.data.llm_provider);
        setModelSelection(res.data.llm_model);
        setToneStyle(res.data.tone);
        setSystemPrompt(res.data.system_prompt);
        setMaxTokens(res.data.max_tokens);
        setCreativity(res.data.temperature * 100);
      }
    } catch (error) {
      console.error("Error loading assistant settings:", error);
      SendNotification("Failed to load assistant settings", "error");
    }
  };

  useEffect(() => {
    loadPreferences();
  }, [user?.email]);

  const handleUpdateSettings = async () => {
    try {
      const req = await fetch(
        `${import.meta.env.VITE_SERVER_URL}/api/user/preferences`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: user?.email,
            llm_provider: llmProvider,
            llm_model: modelSelection,
            api_key: "",
            tone: toneStyle,
            language: "en",
            max_tokens: maxTokens,
            temperature: creativity / 100,
            system_prompt: systemPrompt,
          }),
        },
      );
      const res = await req.json();
      console.log(res);
      SendNotification(res.message, res.success ? "success" : "error");
    } catch (error) {
      console.error("Error updating assistant settings:", error);
      SendNotification("Failed to update assistant settings", "error");
    }
  };

  const handleTestVoice = () => {
    SendNotification("Voice testing started...", "default");
    // Voice testing logic would go here
  };

  const handleLLMProviderChange = (provider: string) => {
    const ProviderOptions = {
      gemini: [
        "gemini-2.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-2.5-flash",
      ],
      groq: [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
      ],
      cerebras: [
        "gpt-oss-120b",
        "llama3.1-8b",
        "qwen-3-235b-a22b-instruct-2507",
        "zai-glm-4.7",
      ],
    } as const;
    setLlmProvider(provider);
    const options =
      ProviderOptions[provider as keyof typeof ProviderOptions] || [];
    setLlmModelOptions(options as unknown as string[]);
    if (options.length > 0 && !options.includes(modelSelection as never)) {
      setModelSelection(options[0]);
    }
  };
  useEffect(() => {
    handleLLMProviderChange(llmProvider);
  }, [llmProvider]);

  return (
    <div className="space-y-8 animate-fade-in-up pb-10">
      <div className="border-b border-border-divider pb-6">
        <h2 className="text-3xl font-bold tracking-tight text-primary">
          Assistant Settings
        </h2>
        <p className="text-secondary mt-2 text-sm">
          Fine-tune your AI's personality, intelligence, and behavior.
        </p>
      </div>
      <div className="space-y-6">
        {/* Personality & Prompt Section */}
        <section className="bg-card border border-border-card rounded-2xl p-6 shadow-card hover:border-border-card-hover transition-colors">
          <div className="flex items-center gap-4 mb-8">
            <div className="p-3 bg-indigo-500/10 text-accent-primary rounded-xl border border-indigo-500/20">
              <Sparkles size={24} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-primary">
                AI Personality
              </h3>
              <p className="text-text-muted text-sm">
                Define how the assistant communicates
              </p>
            </div>
          </div>

          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <label className="text-sm font-medium text-text-secondary flex items-center gap-2">
                  <Bot size={16} /> Assistant Name
                </label>
                <input
                  type="text"
                  value={assistantName}
                  readOnly
                  onClick={() => {
                    SendNotification(
                      "Sorry! you can't change the name of ADIS",
                      "error",
                    );
                  }}
                  className="w-full bg-input border border-border-input rounded-lg px-4 py-2.5 text-primary focus:outline-none focus:border-border-input-focus transition-all"
                />
              </div>
              <div className="space-y-3">
                <label className="text-sm font-medium text-text-secondary flex items-center gap-2">
                  <Type size={16} /> Tone Style
                </label>
                <select
                  value={toneStyle}
                  onChange={(e) => setToneStyle(e.target.value)}
                  className="capitalize w-full bg-input border border-border-input rounded-lg px-4 py-2.5 text-primary focus:outline-none focus:border-border-input-focus transition-all appearance-none cursor-pointer"
                >
                  <option className="capitalize bg-app text-primary">
                    friendly
                  </option>
                  <option className="capitalize bg-app text-primary">
                    formal
                  </option>
                  <option className="capitalize bg-app text-primary">
                    concise
                  </option>
                </select>
              </div>
            </div>

            <div className="space-y-3">
              <label className="text-sm font-medium text-text-secondary flex items-center gap-2">
                <Terminal size={16} /> Custom Instructions
              </label>
              <textarea
                  rows={4}
                  value={systemPrompt ?? ""}
                  onChange={(e) => setSystemPrompt(e.target.value)}
                  placeholder="You are a helpful AI assistant that provides accurate information..."
                  className="w-full bg-input border border-border-input rounded-lg px-4 py-3 text-primary placeholder-placeholder focus:outline-none focus:border-border-input-focus transition-all resize-none font-mono text-sm"
                />
              <p className="text-[10px] text-text-muted">
                This prompt defines the base behavior and rules for your AI.
              </p>
            </div>
          </div>
        </section>

        {/* Model Configuration Section */}
        <section className="bg-card border border-border-card rounded-2xl p-6 shadow-card hover:border-border-card-hover transition-colors">
          <div className="flex items-center gap-4 mb-8">
            <div className="p-3 bg-amber-500/10 text-amber-400 rounded-xl border border-amber-500/20">
              <Cpu size={24} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-primary">
                Model Configuration
              </h3>
              <p className="text-text-muted text-sm">
                Select the brain of your assistant
              </p>
            </div>
          </div>

          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <label className="text-sm font-medium text-text-secondary">
                  LLM Provider
                </label>
                <select
                  value={llmProvider}
                  onChange={(e) => handleLLMProviderChange(e.target.value)}
                  className="w-full bg-input border border-border-input rounded-lg px-4 py-2.5 text-primary focus:outline-none focus:border-border-input-focus transition-all cursor-pointer"
                >
                  {llmProviderOptions.map((provider, index) => (
                    <option key={index} className="bg-app text-primary">
                      {provider}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-3">
                <label className="text-sm font-medium text-text-secondary">
                  Model Selection
                </label>
                <select
                  value={modelSelection}
                  onChange={(e) => setModelSelection(e.target.value)}
                  className="w-full bg-input border border-border-input rounded-lg px-4 py-2.5 text-primary focus:outline-none focus:border-border-input-focus transition-all cursor-pointer"
                >
                  {llmModelOptions.map((model, index) => (
                    <option key={index} className="bg-app text-primary">
                      {model}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-medium text-text-secondary flex items-center gap-2">
                    <BrainCircuit size={16} /> Creativity (Temp)
                  </label>
                  <span className="text-xs bg-sidebar-item-active px-2 py-1 rounded text-accent font-medium border border-border-divider">
                    {creativity / 100}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={creativity}
                  onChange={(e) => setCreativity(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-input rounded-lg appearance-none cursor-pointer accent-accent-primary outline-none transition-all"
                />
                <div className="flex justify-between text-[10px] text-text-muted font-medium">
                  <span>Precise</span>
                  <span>Creative</span>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-medium text-text-secondary flex items-center gap-2">
                    <Zap size={16} /> Max Tokens
                  </label>
                  <span className="text-xs bg-sidebar-item-active px-2 py-1 rounded text-accent font-medium border border-border-divider">
                    {maxTokens}
                  </span>
                </div>
                <input
                  type="range"
                  min="256"
                  max="4096"
                  step="256"
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-input rounded-lg appearance-none cursor-pointer accent-accent-primary outline-none transition-all"
                />
                <div className="flex justify-between text-[10px] text-text-muted font-medium">
                  <span>Short</span>
                  <span>Long</span>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-8 flex justify-end gap-4">
            <button
              onClick={handleUpdateSettings}
              className="px-5 py-2.5 bg-accent-primary hover:bg-accent-secondary text-white font-medium rounded-lg transition-colors shadow-glow active:scale-95"
            >
              Update Settings
            </button>
          </div>
        </section>

        {/* Chat Behavior Section: HIDDEN */}
        <section className="hidden bg-card border border-border-card rounded-2xl p-6 shadow-card hover:border-border-card-hover transition-colors">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-purple-500/10 text-purple-400 rounded-xl border border-purple-500/20">
              <Sliders size={24} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-primary">
                Chat Behavior
              </h3>
              <p className="text-text-muted text-sm">
                Customize interaction patterns
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center justify-between p-4 rounded-xl bg-input border border-border-input transition-all">
              <div>
                <h4 className="text-sm font-medium text-primary">
                  Auto-scroll
                </h4>
                <p className="text-xs text-text-muted">
                  Scroll to bottom on new message
                </p>
              </div>
              <div
                onClick={() => setAutoScroll(!autoScroll)}
                className={`relative inline-block w-12 h-6 rounded-full transition-colors cursor-pointer ${autoScroll ? "bg-accent-primary shadow-glow" : "bg-[#454853]"}`}
              >
                <span
                  className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all shadow-sm ${autoScroll ? "left-[26px]" : "left-1"}`}
                ></span>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 rounded-xl bg-input border border-border-input transition-all">
              <div>
                <h4 className="text-sm font-medium text-primary">
                  Enter to Send
                </h4>
                <p className="text-xs text-text-muted">
                  Press Enter to send message
                </p>
              </div>
              <div
                onClick={() => setEnterToSend(!enterToSend)}
                className={`relative inline-block w-12 h-6 rounded-full transition-colors cursor-pointer ${enterToSend ? "bg-accent-primary shadow-glow" : "bg-[#454853]"}`}
              >
                <span
                  className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all shadow-sm ${enterToSend ? "left-[26px]" : "left-1"}`}
                ></span>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 rounded-xl bg-input border border-border-input transition-all">
              <div>
                <h4 className="text-sm font-medium text-primary">
                  Markdown Rendering
                </h4>
                <p className="text-xs text-text-muted">
                  Format AI responses with MD
                </p>
              </div>
              <div
                onClick={() => setMarkdownRendering(!markdownRendering)}
                className={`relative inline-block w-12 h-6 rounded-full transition-colors cursor-pointer ${markdownRendering ? "bg-accent-primary shadow-glow" : "bg-[#454853]"}`}
              >
                <span
                  className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all shadow-sm ${markdownRendering ? "left-[26px]" : "left-1"}`}
                ></span>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 rounded-xl bg-input border border-border-input transition-all">
              <div>
                <h4 className="text-sm font-medium text-primary">
                  Code Highlighting
                </h4>
                <p className="text-xs text-text-muted">
                  Syntax highlighting for code
                </p>
              </div>
              <div
                onClick={() => setCodeHighlighting(!codeHighlighting)}
                className={`relative inline-block w-12 h-6 rounded-full transition-colors cursor-pointer ${codeHighlighting ? "bg-accent-primary shadow-glow" : "bg-[#454853]"}`}
              >
                <span
                  className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all shadow-sm ${codeHighlighting ? "left-[26px]" : "left-1"}`}
                ></span>
              </div>
            </div>
          </div>
        </section>

        {/* Voice Section: HIDDEN */}
        <section className="hidden bg-card border border-border-card rounded-2xl p-6 shadow-card hover:border-border-card-hover transition-colors">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20">
              <Volume2 size={24} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-primary">
                Voice Settings
              </h3>
              <p className="text-text-muted text-sm">
                Configure speech and listening
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              onClick={() => setAlwaysListening(!alwaysListening)}
              className="flex items-center p-4 rounded-xl bg-input border border-border-input hover:border-border-input-focus transition-all cursor-pointer"
            >
              <div className="mr-4 p-2.5 bg-mic rounded-lg text-white shadow-mic border border-[#ffffff1a]">
                <Mic size={18} />
              </div>
              <div>
                <h4 className="text-sm font-medium text-primary">
                  Always Listening
                </h4>
                <p className="text-xs text-text-muted mt-0.5">
                  Wake word detection
                </p>
              </div>
              <div
                className={`ml-auto w-4 h-4 rounded border ${alwaysListening ? "border-border-input-focus bg-accent-primary shadow-glow" : "border-border-divider bg-transparent"} flex items-center justify-center transition-all`}
              >
                {alwaysListening && (
                  <div className="w-2 h-2 bg-white rounded-sm"></div>
                )}
              </div>
            </div>

            <div
              onClick={() => setSpokenResponses(!spokenResponses)}
              className="flex items-center p-4 rounded-xl bg-input border border-border-input hover:border-border-input-focus transition-all cursor-pointer"
            >
              <div className="mr-4 p-2.5 bg-[#ffffff0a] rounded-lg text-secondary border border-border-divider">
                <MessageSquare size={18} />
              </div>
              <div>
                <h4 className="text-sm font-medium text-primary">
                  Spoken Responses
                </h4>
                <p className="text-xs text-text-muted mt-0.5">
                  Read messages aloud
                </p>
              </div>
              <div
                className={`ml-auto w-4 h-4 rounded border ${spokenResponses ? "border-border-input-focus bg-accent-primary shadow-glow" : "border-border-divider bg-transparent"} flex items-center justify-center transition-all`}
              >
                {spokenResponses && (
                  <div className="w-2 h-2 bg-white rounded-sm"></div>
                )}
              </div>
            </div>
          </div>
          <div className="mt-8 flex justify-end gap-4">
            <button
              onClick={handleTestVoice}
              className="px-5 py-2.5 bg-sidebar-item-active border border-border-card hover:bg-sidebar-item-hover text-primary font-medium rounded-lg transition-colors hover:border-border-card-hover"
            >
              Test Voice
            </button>
            <button
              onClick={handleUpdateSettings}
              className="px-5 py-2.5 bg-accent-primary hover:bg-accent-secondary text-white font-medium rounded-lg transition-colors shadow-glow active:scale-95"
            >
              Update Settings
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}
