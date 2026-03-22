// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
// AuthContext.tsx — Gestión centralizada de la sesión de usuario
import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import axiosClient from '../api/axiosClient';

interface UserProfile {
  id: number;
  email: string;
  full_name: string;
  current_app: string;         // 'operations' | 'analytics' | 'admin'
  role: string;
  permissions: Record<string, string[]>;
  ai_modules_access: string[];
}

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, appName: string) => Promise<void>;
  logout: () => void;
  hasPermission: (module: string, action: string) => boolean;
  hasAIAccess: (module: string) => boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

