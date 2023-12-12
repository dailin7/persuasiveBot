"use client" 
import Dashboard from "@/components/Dashboard"
import { store } from './store'
import { Provider } from 'react-redux'

export default function Home() {
  return (
    <Provider store={store}>
      <Dashboard></Dashboard>
    </Provider>
  )
}
