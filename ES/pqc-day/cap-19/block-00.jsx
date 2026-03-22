// Extraído de: LibroPQC/cap-19-dashboard.md
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import { ThemeProvider, CssBaseline } from '@mui/material'
import App from './App'
import store from './store'
import theme from './theme'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}>        {/* 1. Estado global */}
      <BrowserRouter>               {/* 2. Enrutamiento */}
        <ThemeProvider theme={theme}> {/* 3. Tema visual */}
          <CssBaseline />            {/* 4. Reset CSS */}
          <App />                    {/* 5. Aplicación */}
        </ThemeProvider>
      </BrowserRouter>
    </Provider>
  </React.StrictMode>
)
