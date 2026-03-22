// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// WorkzoneCanvas — Estado del componente
const WorkzoneCanvas: React.FC<WorkzoneCanvasProps> = ({
  workzoneId, onDeploy
}) => {
  const { t } = useTranslation();
  const { state: machineState, actions: machineActions } = useMachineContext();
  const { updateWorkzoneInfo, addLog, setLoading } = useFooter();

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [nodes, setNodes] = useState<CanvasNode[]>([]);
  const [edges, setEdges] = useState<CanvasEdge[]>([]);
  const [networks, setNetworks] = useState<NetworkContainer[]>([]);

  // Estados de interacción
  const [selectedNode, setSelectedNode] = useState<CanvasNode | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedNetwork, setSelectedNetwork] = useState<string | null>(null);
  const [isResizingNetwork, setIsResizingNetwork] = useState(false);
  const [resizeHandle, setResizeHandle] =
    useState<'se' | 'sw' | 'ne' | 'nw' | null>(null);

  // Estado de despliegue
  const [isDeploying, setIsDeploying] = useState(false);
  const [hasWorkzoneError, setHasWorkzoneError] = useState(false);
};
