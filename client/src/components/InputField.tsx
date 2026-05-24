import { Mic, Paperclip, ArrowUp } from "lucide-react";
import { useRef, useState, useCallback, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { setMessage, clearMessage } from "../features/message/messageSlice";
import { RootState } from "../app/store";
import { useNavigate, useLocation } from "react-router-dom";

interface InputFieldProps {
  setOpened: (opened: boolean) => void;
  session_id: string;
}

const InputField = ({
  setOpened,
  session_id
}: InputFieldProps) => {

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [value, setValue] = useState("");
  const { name: AssistantName } = useSelector((state: RootState) => state.assistant);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useSelector((state: RootState) => state.user);

  const hasTriggeredInitial = useRef(false);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setValue(e.target.value);
      const el = e.target;
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
    },
    [],
  );

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const getChatResponse = useCallback(async (value: string, currentSessionId: string) => {
    try {
      const res = await fetch(`${import.meta.env.VITE_SERVER_URL}/api/text/chat_completion`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          email: user?.email!,
          session: parseInt(currentSessionId),
          message: value,
        }),
      });

      const data = await res.json();
      // console.log("data: ", data);
      if (res.ok) {
        return data.data;
      }
    } catch (e) {
      console.log(e);
    }
  }, [user]);

  const createNewSession = useCallback(async (userEmail: string, message: string) => {
    try {
      const res = await fetch(`${import.meta.env.VITE_SERVER_URL}/api/text/create_session`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          email: userEmail,
          message: message,
        }),
      });

      const data = await res.json();
      return data.data;
    } catch (e) {
      console.log(e);
    }
  }, [user]);

  const handleSubmit = async () => {
    if (!value.trim()) return;

    let currentSessionId = session_id;
    const typedMessage = value;
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

    if (!currentSessionId || currentSessionId.length === 0) {
      const s_id = await createNewSession(user?.email!, typedMessage);
      if (s_id) {
        currentSessionId = s_id.toString();
        
        dispatch(clearMessage());
        
        
        navigate(`/chat/${currentSessionId}`, { state: { initialMessage: typedMessage } });
        return;
      }
    } else {
      dispatch(setMessage({ content: typedMessage, role: "user" }));
      const chat_response = await getChatResponse(typedMessage, currentSessionId);
      // console.log("chat_response(already have session_id): ", currentSessionId, chat_response);
      if (chat_response) {
        dispatch(setMessage({ content: chat_response, role: "assistant" }));
      }
    }
  };

  useEffect(() => {
    const initialMsg = location.state?.initialMessage;
    if (initialMsg && session_id && !hasTriggeredInitial.current) {
      hasTriggeredInitial.current = true;
      dispatch(setMessage({ content: initialMsg, role: "user" }));
      const fetchInitialResponse = async () => {
        const chat_response = await getChatResponse(initialMsg, session_id);
        // console.log("fetchInitialResponse: ", session_id, chat_response);
        if (chat_response) {
          dispatch(setMessage({ content: chat_response, role: "assistant" }));
        }
      };
      fetchInitialResponse();
      window.history.replaceState({}, document.title);
    }
  }, [session_id, location.state, getChatResponse, dispatch]);

  const hasText = value.trim().length > 0;

  return (
    <div className="bg-transparent mx-auto justify-self-center min-w-3/5 flex flex-col items-center gap-3 animate-fade-in-up-delay-4 border-0 w-fit">
      <div
        className="backdrop-blur-lg w-full flex items-end rounded-2xl py-2 px-3 gap-2 transition-all duration-200"
        id="chat-input-bar"
        style={{
          border: "1px solid var(--color-border-input)",
        }}
        onFocusCapture={(e) => {
          const bar = e.currentTarget;
          bar.style.borderColor = "var(--color-border-input-focus)";
          bar.style.backgroundColor = "var(--color-bg-input-focus)";
          bar.style.boxShadow = `0 0 20px var(--color-focus-glow)`;
        }}
        onBlurCapture={(e) => {
          if (!e.currentTarget.contains(e.relatedTarget as Node)) {
            const bar = e.currentTarget;
            bar.style.borderColor = "var(--color-border-input)";
            bar.style.backgroundColor = "var(--color-bg-input)";
            bar.style.boxShadow = "none";
          }
        }}
      >
        <button
          className="p-2 mb-1 hover:bg-white/20 hover:scale-105 w-10 h-10 flex items-center justify-center rounded-full shrink-0 transition-all duration-200 cursor-pointer"
          aria-label="Attach file"
          id="attach-btn"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          <Paperclip size={18} strokeWidth={1.5} />
        </button>

        <textarea
          ref={textareaRef}
          rows={1}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          autoFocus
          spellCheck={true}
          className="flex-1 min-h-[40px] max-h-[200px] py-2 px-1 text-sm font-normal bg-transparent focus:outline-none resize-none overflow-y-auto leading-relaxed "
          placeholder={`Message ${AssistantName}...`}
          id="chat-input" 
          style={{ color: "var(--color-text-primary)" }}
        />

        {hasText ? (
          <button
            onClick={handleSubmit}
            className="w-10 h-10 mb-1 flex items-center justify-center rounded-full shrink-0 transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer"
            aria-label="Send message"
            id="send-btn"
            style={{
              backgroundColor: "var(--color-bg-mic)",
              color: "var(--color-text-primary)",
              boxShadow: `0 4px 20px var(--color-shadow-mic)`,
            }}
            onMouseEnter={(e) =>
              (e.currentTarget.style.backgroundColor =
                "var(--color-bg-mic-hover)")
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.backgroundColor = "var(--color-bg-mic)")
            }
          >
            <ArrowUp size={18} strokeWidth={2.5} />
          </button>
        ) : (
          <button
            className="w-10 h-10 mb-1 flex items-center justify-center rounded-full shrink-0 transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer"
            aria-label="Voice input"
            id="mic-btn"
            style={{
              backgroundColor: "var(--color-bg-mic)",
              color: "var(--color-text-primary)",
              boxShadow: `0 4px 20px var(--color-shadow-mic)`,
            }}
            onMouseEnter={(e) =>
              (e.currentTarget.style.backgroundColor =
                "var(--color-bg-mic-hover)")
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.backgroundColor = "var(--color-bg-mic)")
            }
          >
            <Mic onClick={() => setOpened(true)} size={20} strokeWidth={2} />
          </button>
        )}
      </div>

      <p
        className="text-[11px] uppercase tracking-[0.2em] font-medium"
        style={{ color: "var(--color-text-footer)" }}
      >
        {AssistantName} uses secure voice recognition technology
      </p>
    </div>
  );
};

export default InputField;
