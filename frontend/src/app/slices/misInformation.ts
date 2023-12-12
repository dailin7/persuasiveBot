import { createSlice } from '@reduxjs/toolkit'

export interface Misinformation {
  id: number[],
  user_id: string,
  content: string,
  res_1: string,
  res_2: string,
  final: string,
}

export const initialState: Misinformation = {
  id: [-1, -1],
  user_id: '',
  content: 'choose a message from left panel',
  res_1: 'choose a message from left panel',
  res_2: 'choose a message from left panel',
  final: 'choose a message from left panel',
}

export const misinformationSlice = createSlice({
  name: 'misinformation',
  initialState,
  reducers: {
    edit: (state, action) => {
      state.final = action.payload
    },
    quickEdit: (state, action) => {
      if (action.payload=='res_1') {
        state.final = state.res_1
      }
      else if (action.payload=='res_2') {
        state.final = state.res_2
      }
      else {
        state.final = ''
      }
    },
    reload: (state, action) => {
      const data = action.payload
      return {id: [data.user_id, data.user_message_id],
              user_id: data.user_id,
              content: data.misinformation.user_message_text,
              res_1: data.message_draft,
              res_2: data.message_draft,
              final: data.message_final}
    },
    clear: (state) => {
      return initialState
    },
  },
})

// Action creators are generated for each case reducer function
export const { edit, quickEdit, reload, clear } = misinformationSlice.actions

export default misinformationSlice.reducer