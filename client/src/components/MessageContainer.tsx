import MessageField from "./MessageField";
import InputField from "./InputField";
import { useDispatch, useSelector } from "react-redux";
import { setMessage, clearMessage } from "../features/message/messageSlice";
import { RootState } from "../app/store";
import { useEffect, useRef } from "react";
import { useParams } from "react-router-dom";

const MessageContainer = () => {
  const { session_id } = useParams();
  const { message } = useSelector((state: RootState) => state.message);
  const dispatch = useDispatch();


  async function getChatHistory(){
    try {
      const res = await fetch(`${import.meta.env.VITE_SERVER_URL}/api/text/get_messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({
          session_id
        })
      })
      const data = await res.json();
      // console.log(data.data)
      for (let i = 0; i < data.data.length; i++) {
        dispatch(setMessage(data.data[i]));
      }
    } catch (error) {
      console.log(error);
    }
    
  }
  
  useEffect(() => {
    dispatch(clearMessage());
    if (session_id) {
      getChatHistory();
    }
  }, [session_id]);

  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [message]);

  return (
    <div className="relative max-h-screen flex-1 flex flex-col justify-between border-0 border-red-500 ">
      <section className="h-[calc(100vh-100px)] overflow-y-auto scroll-smooth px-15 py-10 w-full flex flex-col items-between mb-0 gap-5 border-0 border-green-500">
        {message && message.length > 0 ?
          message.map((item, index) => (
              <MessageField
                key={index}
                message={item.content}
                sender={item.role as "user" | "assistant"}
              />
            ))
          : null}
        <div ref={endRef} />
      </section>
      <section className="w-full flex justify-center border-0 border-red-500">
        <InputField session_id={session_id!} setOpened={() => {}} />
      </section>
    </div>
  );
};

export default MessageContainer;
