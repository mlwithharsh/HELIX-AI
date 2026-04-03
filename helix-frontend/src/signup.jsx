import React from 'react'
import ReactDOM from 'react-dom/client'
import SignupPage from './pages/SignupPage'
import { Toaster } from 'react-hot-toast'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <SignupPage />
    <Toaster position="bottom-right" />
  </React.StrictMode>,
)
