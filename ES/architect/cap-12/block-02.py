# Extraído de: LibroTecnico/cap-12-rag-produccion.md
    def _ocr_pdf(self, file_path: str) -> list:
        """
        Extrae texto de PDFs escaneados usando Tesseract OCR.
        Requiere poppler-utils instalado en el sistema.
        """
        from langchain.schema import Document  # Import local para evitar dependencia global de OCR
        import pdf2image

        pages = pdf2image.convert_from_path(file_path, dpi=300)
        documents = []
        for i, page_image in enumerate(pages):
            text = pytesseract.image_to_string(
                page_image,
                lang="spa+eng",  # Español e inglés
                config="--psm 3",  # Segmentación automática de página
            )
            if text.strip():
                documents.append(Document(
                    page_content=text,
                    metadata={"page": i + 1, "source": file_path, "ocr": True}
                ))
        return documents
