# Extraído de: LibroPQC/cap-04-requisito-arquitectura.md
class AnalysisResource(Resource):
    @jwt_required()                        # 1. ¿Está autenticado?
    @require_permission('run_analysis')    # 2. ¿Tiene permiso?
    @check_plan_limit('analysis')          # 3. ¿Le quedan análisis?
    @check_feature('ai_semantic')          # 4. ¿Su plan incluye esta funcionalidad?
    def post(self):
        """Crear un nuevo análisis PQC — con todas las verificaciones."""
        user = User.query.get(get_jwt_identity())
        # ... lógica de creación del análisis ...
