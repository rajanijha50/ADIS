import React from "react";
import { LogOut, SlidersHorizontal, UserCircle2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { clearUser } from "../features/user/userSlice";

const MoreOptions = ({ refMe }: { refMe: React.Ref<HTMLDivElement> }) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleLogout = async (e: React.MouseEvent) => {
    e.preventDefault();
    try {
      await fetch(`${import.meta.env.VITE_SERVER_URL}/api/auth/logout`, {
        method: "POST",
        credentials: "include",
      });
      localStorage.removeItem("auth_token");
      dispatch(clearUser());
      navigate("/auth");
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  const Options = [
    { icon: UserCircle2, name: "General", href: "/settings/general", isDanger: false },
    { icon: SlidersHorizontal, name: "Assistant", href: "/settings/assistant", isDanger: false },
    { icon: LogOut, name: "Log out", onClick: handleLogout, isDanger: true },
  ];

  return (
    <div
      ref={refMe}
      className="absolute bottom-[calc(100%+8px)] left-0 w-full min-w-56 rounded-xl p-2 z-100 shadow-lg border"
      style={{
        backgroundColor: "var(--color-bg-sidebar)",
        borderColor: "var(--color-border-divider, var(--color-border-sidebar))",
      }}
      onClick={(e) => e.stopPropagation()}
    >
      <div className="flex flex-col gap-1">
        {Options.map((item, id) => (
          <button
            key={id}
            onClick={item.href ? () => navigate(item.href) : item.onClick}
            className={`w-full p-2 rounded-lg flex items-center gap-3 transition-colors duration-150 text-left ${
              item.isDanger ? "text-red-500 hover:bg-red-500/10" : ""
            }`}
            style={!item.isDanger ? { color: "var(--color-text-primary)" } : {}}
            onMouseEnter={(e) => {
              if (!item.isDanger) {
                e.currentTarget.style.backgroundColor = "var(--color-bg-sidebar-item-hover)";
              }
            }}
            onMouseLeave={(e) => {
              if (!item.isDanger) {
                e.currentTarget.style.backgroundColor = "transparent";
              }
            }}
          >
            <item.icon size={18} strokeWidth={1.5} />
            <span className="text-[14px] font-medium">{item.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default MoreOptions;
