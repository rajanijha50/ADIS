import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface MessageState {
  message: {
    message_id: number;
    content: string;
    role: "user" | "assistant";
    created_at: string;
  }[];
  // message: string | null;
  loading: boolean;
}

const formatMessage = (message: string): string => {
  let formattedMessage = message;

  // Replace **text** with <strong>text</strong> for bold
  formattedMessage = formattedMessage.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Preserve newlines by converting \n to <br>
  formattedMessage = formattedMessage.replace(/\n/g, '<br>');

  // Optional: Replace *text* with <em>text</em> for italic
  formattedMessage = formattedMessage.replace(/\*(.*?)\*/g, '<em>$1</em>');

  // Optional: Replace # Header with <h1>, ## with <h2>, etc.
  formattedMessage = formattedMessage.replace(/^(#{1,6})\s+(.*)$/gm, (_, hashes, text) => {
    const level = hashes.length;
    return `<h${level}>${text}</h${level}>`;
  });

  // Optional: Replace - list items with <ul><li>
  formattedMessage = formattedMessage.replace(/^-\s+(.*)$/gm, '<li>$1</li>');
  formattedMessage = formattedMessage.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

  return formattedMessage;
};

const initialState: MessageState = {
  message: [
//     {
//       message: `**What is Programming?**

// Programming is the process of designing, writing, testing, and maintaining the instructions that a computer follows to perform a specific task. It involves creating a set of instructions, called a program or software, that tells the computer what to do, how to do it, and when to do it.

// Think of programming like writing a recipe for making your favorite dish. Just as a recipe outlines the steps to follow to create a delicious meal, a program outlines the steps a computer should follow to produce the desired output.

// here is a test list:
// - item 1
// - item 2
// - item 3`,
//       sender: "assistant",
//     },
  ],
  loading: true,
};

export const messageSlice = createSlice({
  name: "message",
  initialState,
  reducers: {
    setMessage: (state, action: PayloadAction<any>) => {
      state.message.push(action.payload);
      state.loading = false;
    },
    clearMessage: (state) => {
      state.message = [];
      state.loading = false;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
  },
});

export const { setMessage, clearMessage, setLoading } = messageSlice.actions;

export default messageSlice.reducer;
