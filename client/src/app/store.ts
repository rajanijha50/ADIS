import { configureStore } from '@reduxjs/toolkit'
import userReducer from '../features/user/userSlice'
import messageReducer from '../features/message/messageSlice'
import assistantReducer from '../features/assistant/assistantSlice'

export const store = configureStore({
  reducer: {
    user: userReducer,
    message: messageReducer,
    assistant: assistantReducer,

  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch