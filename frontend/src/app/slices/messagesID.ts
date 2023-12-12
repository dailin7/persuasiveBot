import { createSlice } from '@reduxjs/toolkit'

export interface messagesID {
  IDs: number[][],
}

const initialState: messagesID = {
  // the id already existed in the database, for testing/demo only
  // should be something like: [[-1, -1]]
  IDs: [[6398852775, 1222]],
}

export const messagesIDSlice = createSlice({
  name: 'messages',
  initialState,
  reducers: {
    reload: (state, action ) => {
      return {IDs: action.payload}
    },
    reduce: (state, action) => {
      const index = state.IDs.indexOf(action.payload)
      state.IDs.splice(index, 1)
    },
  },
})

// Action creators are generated for each case reducer function
export const { reload, reduce } = messagesIDSlice.actions
export default messagesIDSlice.reducer