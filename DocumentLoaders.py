#This file includes code snippets derived from Generative AI with LangChain, First Edition, which is licensed under the MIT License.
#
#Copyright (c) 2024 Ben Auffarth
#
#https://github.com/benman1/generative_ai_with_langchain/tree/softupdate
#
#The MIT License applies to the original snippets. See the full license in the LICENSE file.

import pathlib
from typing import Any

from langchain_community.document_loaders.epub import UnstructuredEPubLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.word_document import UnstructuredWordDocumentLoader
from langchain_core.documents import Document

class EpubReader(UnstructuredEPubLoader):
    def __init__(self, file_path: str | list[str], **unstructured_kwargs: Any):
        super().__init__(file_path, **unstructured_kwargs, mode="elements", strategy="fast")


class DocumentLoaderException(Exception):
    pass


class DocumentLoader(object):
    """Loads in a document with a supported extension."""

    supported_extensions = {
        ".pdf": PyPDFLoader,
        ".txt": TextLoader,
        ".epub": EpubReader,
        ".docx": UnstructuredWordDocumentLoader,
        ".doc": UnstructuredWordDocumentLoader,
    }


def load_document(temp_filepath: str) -> list[Document]:
    """Load a file and return it as a list of documents.

    Doesn't handle a lot of errors at the moment.
    """
    ext = pathlib.Path(temp_filepath).suffix
    loader = DocumentLoader.supported_extensions.get(ext)
    if not loader:
        raise DocumentLoaderException(
            f"Invalid extension type {ext}, cannot load this type of file"
        )

    loaded = loader(temp_filepath)
    docs = loaded.load()
    return docs