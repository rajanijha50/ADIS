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

const initialState: MessageState = {
  message: [
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
