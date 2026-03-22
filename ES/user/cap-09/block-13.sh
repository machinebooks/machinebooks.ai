# Extraído de: LibroUsuario/cap-09-conectar-todo.md
# Gmail
claude mcp add gmail -- npx -y @modelcontextprotocol/server-gmail

# Google Drive
claude mcp add google-drive -- npx -y @modelcontextprotocol/server-google-drive

# Slack
claude mcp add slack --env SLACK_TOKEN=xoxp-tu-token -- npx -y @modelcontextprotocol/server-slack

# GitHub
claude mcp add github --env GITHUB_TOKEN=ghp_tu_token -- npx -y @modelcontextprotocol/server-github

# Jira
claude mcp add jira --env JIRA_URL=https://tu-empresa.atlassian.net --env JIRA_EMAIL=tu@email.com --env JIRA_API_TOKEN=tu-token -- npx -y @modelcontextprotocol/server-jira
