import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'

export interface AssistantState {
  name: string;
  userName: string;
  version: string;
  plan: string;
  isVoiceUiOpen: boolean;
}
const initialState: AssistantState = {
  name: 'ADIS',
  userName: 'User',
  version: '1.0.0',
  plan: 'free',
  isVoiceUiOpen: false,
}

export const assistantSlice = createSlice({
  name: 'assistant',
  initialState,
  reducers: {
    changePlan: (state, action: PayloadAction<string>) => {
      state.plan = action.payload
    },
    changeVersion: (state, action: PayloadAction<string>) => {
      state.version = action.payload
    },
    setVoiceUiOpen: (state, action: PayloadAction<boolean>) => {
      state.isVoiceUiOpen = action.payload
    }
  },
})

export const { changePlan, changeVersion, setVoiceUiOpen } = assistantSlice.actions
export default assistantSlice.reducer