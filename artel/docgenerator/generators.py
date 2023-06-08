from abc import (
    ABC,
    abstractmethod
)
from typing import (
    Dict,
    Any
)

from django.db.models import Model
from docxtpl import DocxTemplate


class DocumentGeneratorInterface(ABC):
    @abstractmethod
    def load_template(self, path: str):
        ...
    
    @abstractmethod
    def get_extra_context(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    def generate_file(self, context: Dict[str, Any] = None):
        ...


class BaseDocumentGenerator(DocumentGeneratorInterface):
    
    def __init__(self, instance: Model) -> None:
        super().__init__()
        self.instance = instance

    def load_template(self, path: str):
        return DocxTemplate(path)
    
    def get_extra_context(self):
        return {}


class PdfFromDocGenerator(BaseDocumentGenerator):
    def generate_file(self, context: Dict[str, Any] = None):
        template = self.load_template()
        context.update(self.get_extra_context())
