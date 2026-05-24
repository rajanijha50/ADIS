import { useEffect, useRef, useState } from "react";
import {
  MessageSquare,
  SidebarClose,
  EditIcon,
  SidebarOpen,
} from "lucide-react";
import MoreOptions from "./MoreOptions";
import AudioLinesIcon from "./AudioLinesIcon";
import { useSelector } from "react-redux";
import { RootState } from "../app/store";
import { useNavigate, useParams } from "react-router-dom";

interface ChatItem {
  session_id: string;
  title: string;
  created_at: Date;
}

const Sidebar = () => {
  const { user } = useSelector((state: RootState) => state.user);
  const { name: AssistantName, userName: UserName, version: AssistantVersion } = useSelector(
    (state: RootState) => state.assistant
  );
  const navigate = useNavigate();
  const { session_id } = useParams<{ session_id?: string }>();
  const [recentChats, setRecentChats] = useState<ChatItem[]>([]);
  const [activeChat, setActiveChat] = useState<string>();
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(
    localStorage.getItem("sidebar_open") === "true" ? true : false,
  );
  const [isMoreOptionEnabled, setIsMoreOptionEnabled] =
    useState<boolean>(false);

  const displayName = user?.full_name || UserName || "User";
  const profilePic = user?.profile_pic;

  const childRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    localStorage.setItem("sidebar_open", isSidebarOpen.toString());
  }, [isSidebarOpen]);

  useEffect(() => {
    const handleClickOutside = (event: any) => {
      if (
        childRef.current &&
        !childRef.current.contains(event.target) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target)
      ) {
        setIsMoreOptionEnabled(false);
      }
    };
    if (isMoreOptionEnabled) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isMoreOptionEnabled]);

  const getAllChats = async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_SERVER_URL}/api/text/list_sessions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: user?.email
        }),
      })

      const data = await res.json();
      // console.log(data);
      if (res.ok) {
        setRecentChats(data.data)
      }

    } catch (error) {
      console.log(error);
    }
  }

  // Fetch recent chats whenever user logins or session_id changes (new chat created or switched)
  useEffect(() => {
    if (user?.email) {
      getAllChats();
    }
  }, [user, session_id]);

  // Synchronize activeChat state with the URL parameter session_id
  useEffect(() => {
    if (session_id) {
      setActiveChat(session_id);
    } else {
      setActiveChat(undefined);
    }
  }, [session_id]);

  // Navigate only when user clicked a chat that is different from current route
  useEffect(() => {
    if (activeChat && activeChat !== session_id) {
      // console.log(activeChat)
      navigate(`/chat/${activeChat}`)
    }
  }, [activeChat, session_id, navigate]);

  const handleNewChat = () => {
    setActiveChat(undefined);
    navigate("/");
  }

  return (
    <aside
      className={`h-screen flex flex-col relative z-50 transition-all duration-300 ease-in-out border-r border-border-sidebar bg-sidebar ${isSidebarOpen ? "w-72 p-5" : "w-16 px-2 py-5 cursor-ew-resize"
        }`}
      onMouseDown={(e) => {
        if (!isSidebarOpen) {
          const target = e.target as HTMLElement;
          if (
            target.closest("button") ||
            target.closest(".cursor-pointer")
          ) {
            return;
          }
          setIsSidebarOpen(true);
        }
      }}
    >
      {/* Brand / Logo */}
      <div
        className={`flex items-center gap-3 mb-5 ${isSidebarOpen ? "justify-between" : "justify-center"}`}
      >
        <div
          className={`rounded-[10px] flex items-center justify-center shrink-0 transition-all duration-300 ${isSidebarOpen
              ? "w-9 h-9"
              : "w-10 h-10 cursor-pointer hover:scale-105 active:scale-95"
            }`}
          style={{
            background: !isSidebarOpen ? "" : "var(--color-accent-gradient)",
          }}
          onClick={() => !isSidebarOpen && setIsSidebarOpen(true)}
        >
          {!isSidebarOpen ? (
            <SidebarOpen
              size={20}
              strokeWidth={1.5}
              className="text-primary"
            />
          ) : (
            <AudioLinesIcon size={isSidebarOpen ? 20 : 22} infinite={true} />
          )}
        </div>

        {isSidebarOpen && (
          <>
            <div className="flex flex-col flex-1 animate-in fade-in slide-in-from-left-2 duration-300">
              <span className="capitalize text-sm font-bold leading-tight text-primary tracking-wide">
                {AssistantName}
              </span>
              <span className="text-[10px] font-medium text-tertiary">
                {AssistantVersion}
              </span>
            </div>
            <button
              className="p-1.5 hover:bg-white/10 rounded-lg transition-colors group"
              onClick={() => setIsSidebarOpen(false)}
            >
              <SidebarClose
                size={20}
                className="text-tertiary group-hover:text-primary"
                strokeWidth={1.5}
              />
            </button>
          </>
        )}
      </div>

      {/* New Chat Button */}
      <button
        id="new-chat-btn"
        onClick={handleNewChat}
        className={`flex justify-center items-center gap-3 rounded-xl transition-all duration-300 group hover:-translate-y-0.5 active:translate-y-0 cursor-pointer shadow-lg shadow-black/20 ${isSidebarOpen ? "w-full py-3 px-4 mb-8" : "w-10 h-10 p-2 mx-auto mb-6"
          }`}
        style={{ backgroundColor: "var(--color-bg-new-chat)" }}
        onMouseEnter={(e) =>
        (e.currentTarget.style.backgroundColor =
          "var(--color-bg-new-chat-hover)")
        }
        onMouseLeave={(e) =>
          (e.currentTarget.style.backgroundColor = "var(--color-bg-new-chat)")
        }
      >
        <EditIcon
          size={isSidebarOpen ? 18 : 18}
          className="text-primary shrink-0"
        />
        {isSidebarOpen && (
          <span className="text-sm font-semibold tracking-wide text-primary overflow-hidden whitespace-nowrap animate-in fade-in slide-in-from-left-2">
            New Chat
          </span>
        )}
      </button>

      {/* Recent Activity Label */}
      {isSidebarOpen && (
        <>
          <p className="text-[10px] font-bold uppercase tracking-[0.12em] mb-4 pl-3 text-sidebar-label animate-in fade-in">
            Recent Activity
          </p>


          {/* Chat List */}
          <ul
            className={`flex-1 overflow-y-auto flex flex-col gap-1.5 custom-scrollbar ${!isSidebarOpen && "items-center"}`}
          >
            {recentChats.map((chat) => (
              <li
                key={chat.session_id}
                className={`group flex items-center gap-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 cursor-pointer ${isSidebarOpen ? "px-3" : "w-10 h-10 justify-center"
                  }`}
                style={{
                  backgroundColor:
                    activeChat === chat.session_id
                      ? "var(--color-bg-sidebar-item-active)"
                      : "transparent",
                  color:
                    activeChat === chat.session_id
                      ? "var(--color-text-primary)"
                      : "var(--color-text-secondary)",
                }}
                onClick={() => setActiveChat(chat.session_id)}
                onMouseEnter={(e) => {
                  if (activeChat !== chat.session_id) {
                    e.currentTarget.style.backgroundColor =
                      "var(--color-bg-sidebar-item-hover)";
                    e.currentTarget.style.color = "var(--color-text-primary)";
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeChat !== chat.session_id) {
                    e.currentTarget.style.backgroundColor = "transparent";
                    e.currentTarget.style.color = "var(--color-text-secondary)";
                  }
                }}
              >
                <MessageSquare
                  size={18}
                  strokeWidth={1.5}
                  className={`shrink-0 transition-colors duration-200 ${activeChat === chat.session_id
                      ? "text-accent"
                      : "text-tertiary group-hover:text-secondary"
                    }`}
                />
                {isSidebarOpen && (
                  <span className="truncate flex-1 animate-in fade-in slide-in-from-left-1">
                    {chat.title}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </>

      )}

      {/* User Profile */}
      <div
        className={`relative flex justify-center items-center transition-all duration-300 mt-auto hover:bg-white/20 ${isSidebarOpen
            ? "w-full h-12 gap-3 p-1 rounded-2xl bg-white/5"
            : "h-12 justify-center p-1 rounded-md"
          }`}
      >
        {isMoreOptionEnabled && <MoreOptions refMe={childRef} />}

        <div
          className={`transparent cursor-pointer rounded-full overflow-hidden flex items-center ${isSidebarOpen ? "justify-start" : "justify-center"} gap-4 font-bold text-white shadow-sm transition-all duration-300 w-full h-full`}
          onClick={(e) => {
            e.preventDefault()
            e.stopPropagation();
            setIsMoreOptionEnabled((prev) => !prev);
          }}
        >
          {profilePic ? (
            <img
              src={profilePic}
              alt={displayName}
              className="h-full object-cover rounded-full border-0"
            />
          ) : (
            <span className="w-10 h-full rounded-full flex justify-center items-center border border-gray-400">
              {displayName.charAt(0).toUpperCase()}
            </span>
          )}
          {isSidebarOpen && (
            <span className="text-sm font-bold text-primary truncate">
              {displayName}
            </span>
          )}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
