# Extraído de: LibroTecnico/cap-23-inteligencia-comercial.md
class ExcelImportPipeline:
    """
    Pipeline de importación multi-hoja con validación, reconciliación
    y registro de auditoría. Diseñado para ser ejecutado como tarea
    Celery en segundo plano dado que archivos grandes pueden tardar minutos.
    """

    EXPECTED_SHEETS = {
        'competidores': CompetitorImportValidator,
        'iniciativas': InitiativeImportValidator,
        'okr_targets': OKRTargetImportValidator,
        'presupuesto': BudgetImportValidator
    }

    def process(self, file_path: str, user_id: int) -> ImportResult:
        try:
            # NOTA: La validación de tipo MIME y tamaño máximo del archivo se realiza
            # en el endpoint de recepción, antes de llegar a este pipeline
            workbook = pd.read_excel(file_path, sheet_name=None,
                                     engine='openpyxl')
        except Exception as e:
            return ImportResult(success=False,
                               error=f'Error leyendo archivo: {str(e)}')

        results = {}
        errors = []

        for sheet_name, validator_class in self.EXPECTED_SHEETS.items():
            if sheet_name not in workbook:
                # Hoja opcional: no es error, se registra como omitida
                results[sheet_name] = SheetResult(status='skipped')
                continue

            df = workbook[sheet_name]
            validator = validator_class(df)

            if not validator.is_valid():
                errors.extend(validator.get_errors())
                results[sheet_name] = SheetResult(
                    status='validation_failed',
                    errors=validator.get_errors()
                )
                continue

            # Reconciliación: identificar nuevos vs modificados
            reconciled = self._reconcile(sheet_name, validator.get_records())

            # Solo insertar/actualizar registros con cambios reales
            inserted = self._bulk_upsert(sheet_name, reconciled.changed)

            # Registrar auditoría de cambios
            _log_import_audit(sheet_name, reconciled, user_id)

            results[sheet_name] = SheetResult(
                status='success',
                inserted=len(reconciled.new_records),
                updated=len(reconciled.updated_records),
                unchanged=len(reconciled.unchanged_records)
            )

        return ImportResult(
            success=len(errors) == 0,
            sheet_results=results,
            errors=errors
        )
