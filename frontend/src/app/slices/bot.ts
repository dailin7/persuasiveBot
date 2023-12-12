import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import misInformation from './misInformation'

export interface Misinformation {
  id: number[],
  user_id: string,
  content: string,
  res_1: string,
  res_2: string,
  final: string,
}

export const botApi = createApi({
  reducerPath: 'botApi',
  //TODO: edit baseUrl
  baseQuery: fetchBaseQuery({ baseUrl: '' }),
  endpoints: (builder) => ({
    startBot: builder.query<void, void>({
      query: () => 'http://127.0.0.1:5000/start_bot/', 
    }),
    endBot: builder.query<void, void>({
      query: () => 'http://127.0.0.1:5000/end_bot/',
    }),
    getMessageIDs: builder.query<number[][], void>({
      query: () => 'http://127.0.0.1:5000/get_ids/', 
    }),
    getMisinformation: builder.query<Misinformation, number[]>({
      query: (id: number[]) => `http://127.0.0.1:5000/get_misinformation/${id[0]}/${id[1]}/`,
    }),
    sendResponse: builder.mutation({
      query: (misinformation:Misinformation) => ({
        url: 'http://127.0.0.1:5000/send_response/', 
        method: 'POST', 
        body: 
        { conversation_id: misinformation.id[0],
          message_id: misinformation.id[1],
          final_response: misinformation.final},
      }),
    }),
  }),
})

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useLazyStartBotQuery, useLazyEndBotQuery, useLazyGetMessageIDsQuery, useLazyGetMisinformationQuery, useSendResponseMutation } = botApi