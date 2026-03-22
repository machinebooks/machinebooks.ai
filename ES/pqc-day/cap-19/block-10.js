// Extraído de: LibroPQC/cap-19-dashboard.md
import { configureStore } from '@reduxjs/toolkit'
import authReducer from './slices/authSlice'
import clientsReducer from './slices/clientsSlice'
import usersReducer from './slices/usersSlice'

const store = configureStore({
  reducer: {
    auth: authReducer,      // Token, usuario, organización
    clients: clientsReducer, // Lista de clientes, selección activa
    users: usersReducer,     // Lista de usuarios del sistema
  },
})

export default store
