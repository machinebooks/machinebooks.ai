# Extraído de: LibroCyberrange/cap-11-base-datos.md
# Estructura lógica de los 90 modelos del Cyber Range
# Fichero: backend/models.py

# ------- Catálogos -------
# VMTemplate, ActionTemplate
# Templates reutilizables que definen la base de VMs y acciones de ataque

# ------- Usuarios / Workzones -------
# Workzone, User, Team, VCenterResource, WorkzoneInstance
# El núcleo organizativo: quién está dónde y qué recursos tiene

# ------- Diseños de topología -------
# TopologyDesign, TopologyNodeTemplate, TopologyNetTemplate, TopologyEdgeTemplate
# Representación del canvas de red que el usuario diseña visualmente

# ------- Escenarios -------
# Scenario, ScenarioTemplate, ScenarioDeployment, ScenarioInstance
# Desde la plantilla hasta el despliegue real en infraestructura

# ------- Ataques -------
# AttackExecution, ScheduledAttackExecution, AttackLog
# Ejecución de ataques inmediatos, programados y recurrentes

# ------- Auditoría & Gamificación -------
# AuditSession, AuditEvent, ScoreLog
# Sesiones de usuario, eventos granulares, puntuaciones

# ------- CTF & Challenges -------
# Challenge, ChallengeInstance, CtfFlag, CtfCapture, CtfHint, CtfHintUse
# El motor completo de Capture The Flag con flags dinámicas

# ------- MITRE ATT&CK -------
# MitreTactic, MitreTechnique, MitreSubtechnique,
# MitreTacticTechnique, ChallengeMitreTechnique
# Catálogo completo con relaciones muchos-a-muchos

# ------- Perfiles y habilidades -------
# Skill, SkillLevelConfig, Badge, BadgeChallenge, ChallengeSkill,
# FlagSkill, UserSkill, UserBadge, UserActivityLog
# Sistema de progresión con skills, badges y log de actividad

# ------- Proxmox Management -------
# ProxmoxCluster, ProxmoxNode, ProxmoxVM, ProxmoxTemplate,
# ProxmoxSnapshot, ProxmoxPool, ProxmoxTask, ProxmoxSyncLog
# Espejo completo de la infraestructura Proxmox

# ------- Gestión de base de datos -------
# DatabaseConnection, DatabaseQueryHistory, DatabasePerformanceMetric,
# DatabaseBackup, DatabaseAlert
# Auto-monitoreo y gestión de la propia base de datos

# ------- Auditoría completa -------
# AuditLog, AuditLogArchive, SecurityAlert
# Sistema de auditoría con archivado y alertas de seguridad
