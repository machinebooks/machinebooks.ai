# Extraído de: LibroCyberrange/cap-07-redes-aislamiento.md
# Ejemplo didáctico: models.py — Topología de red

class TopologyDesign(Base):
    """Diseño de topología de red para un escenario."""
    __tablename__ = "topology_design"
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    owner_id = Column(Integer)
    workzone_id = Column(Integer, ForeignKey("workzone.id"))
    category = Column(String(64))  # "enterprise", "industrial", "cloud"

class TopologyNetTemplate(Base):
    """Red dentro de una topología."""
    __tablename__ = "topology_net_template"
    id = Column(Integer, primary_key=True)
    topology_id = Column(Integer, ForeignKey("topology_design.id"))
    network_template_id = Column(Integer,
                                  ForeignKey("network_template.id"))
    vlan = Column(Integer)  # Sub-VLAN dentro de la workzone

class TopologyEdgeTemplate(Base):
    """Conexión entre un nodo (VM) y una red."""
    __tablename__ = "topology_edge_template"
    id = Column(Integer, primary_key=True)
    topology_id = Column(Integer, ForeignKey("topology_design.id"))
    src_node_id = Column(Integer)  # VM de origen
    dst_node_id = Column(Integer)  # VM o red de destino
    net_id = Column(Integer)       # Red que conecta ambos

class NetworkTemplate(Base):
    """Plantilla de red reutilizable."""
    __tablename__ = "network_template"
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    network_type = Column(
        Enum('bridge', 'vlan', 'overlay'), default='bridge'
    )
    vlan_id = Column(Integer)
    subnet = Column(String(40))    # CIDR notation
    gateway = Column(String(45))
    dns_servers = Column(JSON)
