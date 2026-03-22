# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
    def validate_excel(self, file_path: Path) -> tuple[pd.DataFrame, list[str]]:
        """Valida el fichero Excel antes de intentar cargarlo.

        Returns:
            Tuple de (DataFrame válido, lista de errores). Si hay errores,
            el DataFrame puede estar vacío.
        """
        errors = []

        try:
            df = pd.read_excel(file_path, dtype=str)
        except Exception as e:
            return pd.DataFrame(), [f"Error leyendo fichero Excel: {e}"]

        # Verificar columnas obligatorias
        missing_cols = self.REQUIRED_COLUMNS - set(df.columns)
        if missing_cols:
            errors.append(f"Columnas obligatorias faltantes: {missing_cols}")
            return df, errors

        # Validar que no hay filas vacías en campos críticos
        for col in ["codigo_servicio", "precio_base"]:
            empty_rows = df[df[col].isna() | (df[col].str.strip() == "")].index.tolist()
            if empty_rows:
                errors.append(
                    f"Columna '{col}' vacía en filas: {[r+2 for r in empty_rows]}"  # +2 por header y 0-index
                )

        # Validar formato de precio
        df_valid = df[df["precio_base"].notna()].copy()
        invalid_prices = df_valid[
            ~df_valid["precio_base"].str.match(r"^\d+(\.\d{1,2})?$")
        ].index.tolist()
        if invalid_prices:
            errors.append(
                f"Formato de precio inválido en filas: {[r+2 for r in invalid_prices]}"
            )

        return df, errors

