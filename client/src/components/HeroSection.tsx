import InputField from "./InputField";
import AudioLinesIcon from "./AudioLinesIcon";
import { useSelector } from "react-redux";
import { RootState } from "../app/store";

const HeroSection = ({
  setOpened,
}: {
  setOpened: (opened: boolean) => void;
}) => {
  const { user } = useSelector((state: RootState) => state.user);
  const { name: AssistantName, userName: UserName } = useSelector(
    (state: RootState) => state.assistant
  );
  const displayName = user?.full_name || UserName || "User";
  return (
    <main className="h-screen flex-1 flex flex-col justify-between overflow-hidden p-8 border-0">
      <section className="w-full border-0 flex flex-col items-center text-center relative z-1 gap-4">
        <div className="relative w-[120px] h-[120px] mb-6 animate-fade-in-up">
          <div
            className="relative w-full h-full flex items-center justify-center rounded-full"
            style={{
              background: "var(--color-bg-orb-inner)",
              border: "1px solid var(--color-border-orb)",
            }}
          >
            <AudioLinesIcon size={60} infinite={true} />
          </div>
        </div>
        <h1
          className="text-[2.75rem] font-extrabold leading-tight tracking-tight animate-fade-in-up-delay-1"
          style={{ color: "var(--color-text-primary)" }}
        >
          <div
            className="absolute -inset-full rounded-full blur-2xl"
            style={{ background: "var(--color-bg-orb)" }}
          />
          Hey {displayName.split(" ")[0]}, I'm{" "}
          <span className="text-gradient-accent capitalize">
            {AssistantName}
          </span>
          .
        </h1>

        <p
          className="text-base font-normal max-w-[380px] leading-relaxed animate-fade-in-up-delay-2"
          style={{ color: "var(--color-text-secondary)" }}
        >
          How can I help you today? I'm ready to listen, plan, or just chat.
        </p>
      </section>

      <section className="w-full flex justify-center border-0 border-red-500">
        <InputField setOpened={setOpened} session_id={''} />
      </section>
    </main>
  );
};

export default HeroSection;
