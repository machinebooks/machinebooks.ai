# Extraído de: LibroPQC/cap-07-analisis-codigo.md
from github import Github, GithubException
from git import Repo

class GitHubConnector(BaseConnector):
    """Conector para GitHub API"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.token = config.get('token')
        self.client = None

    def connect(self) -> bool:
        try:
            self.client = Github(self.token)
            user = self.client.get_user()
            # Validar que el token es funcional
            _ = user.login
            self.connection = self.client
            return True
        except GithubException:
            return False

    def test_connection(self) -> Dict:
        if self.connect():
            user = self.client.get_user()
            return {
                'status': 'success',
                'user': user.login,
                'name': user.name
            }
        return {'status': 'error', 'message': 'Conexión fallida'}

    def clone_repository(self, repo_full_name: str, local_path: str) -> bool:
        """Clona el repositorio a un directorio local"""
        try:
            repo = self.client.get_repo(repo_full_name)
            # Inyectar token en la URL para repos privados:
            # https://<token>@github.com/owner/repo.git
            clone_url = repo.clone_url.replace(
                'https://', f'https://{self.token}@'
            ) if self.token else repo.clone_url
            # Clonar con --depth 1 para minimizar transferencia
            Repo.clone_from(clone_url, local_path, depth=1)
            return True
        except Exception:
            return False

    def get_file_content(self, repo_full_name: str,
                         file_path: str, branch: str = 'main') -> Optional[str]:
        """Obtiene el contenido de un fichero sin clonar"""
        try:
            repo = self.client.get_repo(repo_full_name)
            content = repo.get_contents(file_path, ref=branch)
            return content.decoded_content.decode('utf-8')
        except GithubException:
            return None

    def search_code(self, query: str,
                    org_name: Optional[str] = None) -> List[Dict]:
        """Busca código en repositorios de la organización"""
        if org_name:
            query = f"{query} org:{org_name}"
        results = []
        for result in self.client.search_code(query)[:100]:
            results.append({
                'name': result.name,
                'path': result.path,
                'repository': result.repository.full_name,
            })
        return results

    def disconnect(self):
        self.client = None
        self.connection = None
