import { Copy, Share2, ThumbsDown, ThumbsUp } from "lucide-react";
import  React, { useState } from "react";
import { SendNotification } from "./SendNotification";

interface MessageFieldProps {
  message: string;
  sender: "user" | "assistant";
}

type ReactNode = string | React.ReactNode | ReactNode[];

export const formatMessage = (message: string): ReactNode[] => {
  const lines = message?.split('\n');
  const elements: ReactNode[] = [];

  let listBuffer: React.ReactNode[] = [];

  const flushList = () => {
    if (listBuffer.length > 0) {
      elements.push(<ul key={`ul-${elements.length}`}>{listBuffer}</ul>);
      listBuffer = [];
    }
  };

  const parseInline = (text: string): React.ReactNode => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        const content = part.slice(2, -2);
        return <strong key={index}>{content}</strong>;
      }
      if (part.startsWith('*') && part.endsWith('*') && part.length > 2) {
        const content = part.slice(1, -1);
        return <em key={index}>{content}</em>;
      }
      return <span key={index}>{part}</span>;
    });
  };

  lines.forEach((line, lineIndex) => {
    const headerMatch = line.match(/^(#{1,6})\s+(.*)$/);
    if (headerMatch) {
      flushList();
      const level = headerMatch[1].length;
      const content = parseInline(headerMatch[2]);
      elements.push(React.createElement(`h${level}`, { key: lineIndex }, content));
      return;
    }

    const listMatch = line.match(/^-\s+(.*)$/);
    if (listMatch) {
      flushList();
      const content = parseInline(listMatch[1]);
      listBuffer.push(<li key={`li-${lineIndex}`}>{content}</li>);
      return;
    }

    flushList();
    const content = parseInline(line);
    elements.push(content);
    
    if (lineIndex < lines.length - 1) {
      elements.push(<br key={`br-${lineIndex}`} />);
    }
  });

  flushList();

  return elements;
};


const handleCopyClick = async (message: string) => {
  SendNotification("Copied to clipboard", "success");
  await navigator.clipboard.writeText(message);
}

const handleLikeClick = async (_message: string) => {
  SendNotification("Liked", "success");
}

const handleDislikeClick = async (_message: string) => {
  SendNotification("Disliked", "success");
}

const handleShareClick = async (_message: string) => {
  SendNotification("Shared", "success");
}

const MessageField = ({ message, sender }: MessageFieldProps) => {
  const [hover, setHover] = useState(false);
  return (
    <>
      <div className={`max-w-4/5 w-fit border-0 relative py-0 animate-fade-in-up-delay-4 flex flex-col ${
    sender === "user" ? "ml-auto max-w-4/5" : "mr-auto max-w-full"
  }`}  onMouseLeave={() => setHover(false)}
  >
        <div
          className={`p-2.5 rounded-2xl ${sender === "user" ? "bg-message-user" : "bg-message-assistant"} selection:bg-white/20 animate-in`}
          onMouseEnter={() => setHover(true)}
        >
          {formatMessage(message)}
        </div>
        <div
          className={
            "z-100 absolute -bottom-8 left-0 w-fit flex justify-start items-center animate-fade-in-up-delay-1"
              
          }
        >
          {hover && (<button title="Copy" onClick={() => handleCopyClick(message)} className="p-1 hover:bg-white/20 hover:scale-105 w-8 h-8 flex items-center justify-center rounded-full shrink-0 transition-colors duration-200 cursor-pointer">
            <Copy size={15} strokeWidth={1.5} />
          </button>)}
          {sender === "assistant" && hover && (
            <>
              <button title="Like" onClick={() => handleLikeClick(message)} className="p-1 hover:bg-white/20 hover:scale-105 w-8 h-8 flex items-center justify-center rounded-full shrink-0 transition-colors duration-200 cursor-pointer">
                <ThumbsUp size={15} strokeWidth={1.5} />
              </button>
              <button title="Dislike" onClick={() => handleDislikeClick(message)} className="p-1 hover:bg-white/20 hover:scale-105 w-8 h-8 flex items-center justify-center rounded-full shrink-0 transition-colors duration-200 cursor-pointer">
                <ThumbsDown size={15} strokeWidth={1.5} />
              </button>
              <button title="Share" onClick={() => handleShareClick(message)} className="p-1 hover:bg-white/20 hover:scale-105 w-8 h-8 flex items-center justify-center rounded-full shrink-0 transition-colors duration-200 cursor-pointer">
                <Share2 size={15} strokeWidth={1.5} />
              </button>
            </>
          )}
        </div>
      </div>
    </>
  );
};

export default MessageField;
