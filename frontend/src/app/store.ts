import { configureStore } from '@reduxjs/toolkit'
import MisinformationReducer from './slices/misInformation'
import MessagesIDReducer from './slices/messagesID'
import { botApi } from './slices/bot'

export const store = configureStore({
  reducer: {
    misinformation: MisinformationReducer,
    messagesID: MessagesIDReducer,
    [botApi.reducerPath]: botApi.reducer,
  },

  middleware: (getDefaultMiddleware) =>
  getDefaultMiddleware().concat(botApi.middleware),
})

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>
// Inferred type: {posts: PostsState, comments: CommentsState, users: UsersState}
export type AppDispatch = typeof store.dispatch

