// Extraído de: LibroPQC/cap-20-chat-ia.md
import { useState, useRef, useEffect, useCallback } from 'react'
import { Box, Paper, TextField, IconButton, Typography,
         Chip, CircularProgress, Accordion, AccordionSummary,
         AccordionDetails, Switch, FormControlLabel } from '@mui/material'
import { Send as SendIcon, SmartToy as BotIcon,
         FolderOpen as FolderIcon, Search as SearchIcon,
         Security as SecurityIcon } from '@mui/icons-material'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { sendChatMessage, sendAgentMessage,
         getRepoCachePath } from '../../api/aiAnalysis'

// Mapeo de herramientas del agente a iconos visuales
const toolIcons = {
  'list_files':        <FolderIcon fontSize="small" />,
  'read_file':         <FileIcon fontSize="small" />,
  'search_code':       <SearchIcon fontSize="small" />,
  'find_crypto_usage': <SecurityIcon fontSize="small" />,
  'get_file_summary':  <TreeIcon fontSize="small" />,
}

// Nombres legibles para el usuario
const toolNames = {
  'list_files':        'Explorando archivos',
  'read_file':         'Leyendo archivo',
  'search_code':       'Buscando código',
  'find_crypto_usage': 'Detectando criptografía',
  'get_file_summary':  'Analizando estructura',
}

export default function AIChat({
  codeContext = null,     // { code, filename, language }
  filesContext = [],      // [{ path, content }]
  repoUrl = '',
  defaultProvider = 'auto',
  // Props para persistencia desde el contenedor
  externalMessages = null,
  onMessagesChange = null,
  conversationId = null,
  initialAgentMode = true,
}) {
  // Estado dual: mensajes locales o externos (del contenedor)
  const [localMessages, setLocalMessages] = useState([
    { role: 'assistant',
      content: '¡Hola! Soy tu asistente de seguridad criptográfica PQC...' }
  ])
  const messages = externalMessages ?? localMessages
  const setMessages = onMessagesChange || setLocalMessages

  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [agentMode, setAgentMode] = useState(initialAgentMode)
  const [repoCachePath, setRepoCachePath] = useState(null)
  const [currentAction, setCurrentAction] = useState(null)

  // Proveedor de IA configurable
  const [provider, setProvider] = useState(defaultProvider)
  const [model, setModel] = useState('')
  const [customUrl, setCustomUrl] = useState('')

  // ... (efectos para scroll, carga de modelos, etc.)
