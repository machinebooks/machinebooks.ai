# Extraído de: LibroTecnico/cap-12-rag-produccion.md
    def load_document(self, file_path: str, mime_type: str) -> list:
        """
        Carga el documento según su tipo, con fallback a OCR para PDFs escaneados.
        Devuelve una lista de objetos Document de LangChain.
        """
        if mime_type == "application/pdf":
            if self.is_scanned_pdf(file_path):
                # OCR con Tesseract para PDFs escaneados
                return self._ocr_pdf(file_path)
            else:
                loader = PyPDFLoader(file_path)
                return loader.load()

        elif mime_type in (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        ):
            loader = UnstructuredWordDocumentLoader(
                file_path, mode="elements"
            )
            return loader.load()

        elif mime_type in (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
        ):
            loader = UnstructuredExcelLoader(
                file_path, mode="elements"
            )
            return loader.load()

        elif mime_type in (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.ms-powerpoint",
        ):
            loader = UnstructuredPowerPointLoader(
                file_path, mode="elements"
            )
            return loader.load()

        else:
            raise ValueError(f"Tipo de documento no soportado: {mime_type}")

