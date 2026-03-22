# Extraído de: LibroTecnico/cap-12-rag-produccion.md
# Ejemplo didáctico: patrones/rag/hierarchical_retriever.py
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

def create_hierarchical_retriever(vectorstore, docstore=None):
    """
    Parent Document Retriever: recupera por chunks pequeños pero
    devuelve el documento padre completo al modelo para mayor contexto.
    Ideal para documentos técnicos donde el detalle importa.
    """
    # Chunks pequeños para recuperación precisa (mayor similitud semántica)
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
    )
    # Documento padre de mayor tamaño para contexto completo al modelo
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
    )

    if docstore is None:
        docstore = InMemoryStore()  # En prod: Redis o almacenamiento persistente

    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=docstore,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
        search_kwargs={"k": 6},  # Recuperar 6 chunks padre para contexto amplio
    )
    return retriever
