import re
from PyPDF2 import PdfReader
from datetime import datetime
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

class PDFParser:
    def __init__(self):
        self.patterns = {
            'reference': [
                r'(AO|AMI|DP)[\s-]?(N[°°]|Numéro)?\s?[:]?\s?([A-Z0-9-/]+)',
                r'Référence\s?[:]?\s?([A-Z0-9-/]+)'
            ],
            'date_limite': [
                r'date limite.*?(\d{1,2}[\/\s]\d{1,2}[\/\s]\d{2,4})',
                r'avant le (\d{1,2}/\d{1,2}/\d{4})'
            ],
            'autorite': [
                r'Autorité contractante\s?[:]?(.+?)\n',
                r'Maître d\'ouvrage\s?[:]?(.+?)\n'
            ],
            'montant': [
                r'Montant.*?(\d[\d\s]+,\d{2})\s?€',
                r'Budget.*?(\d[\d\s]+,\d{2})\s?€'
            ],
            'contact': [
                r'Contact\s?[:]?(.+?)\n',
                r'Personne à contacter\s?[:]?(.+?)\n'
            ],
            'email': [
                r'[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}'
            ],
            'telephone': [
                r'(?:\+?\d{1,3}[\s-]?)?\(?\d{2,3}\)?[\s-]?\d{2,3}[\s-]?\d{2,3}'
            ]
        }

    def parse_pdf(self, file) -> dict:
        """Gère tous les types de fichiers entrants"""
        try:
            # Si c'est un fichier uploadé Django
            if isinstance(file, InMemoryUploadedFile):
                return self._parse_uploaded_file(file)
            # Si c'est un chemin ou objet fichier standard
            else:
                return self._parse_generic_file(file)
        except Exception as e:
            return {'error': str(e)}

    def _parse_uploaded_file(self, file) -> dict:
        """Traitement spécifique pour les fichiers uploadés Django"""
        file_content = BytesIO()
        for chunk in file.chunks():
            file_content.write(chunk)
        file_content.seek(0)
        return self._extract_data(file_content)

    def _parse_generic_file(self, file) -> dict:
        """Traitement pour les autres types de fichiers"""
        return self._extract_data(file)

    def _extract_data(self, file) -> dict:
        """Extrait les données du PDF"""
        text = self._extract_text(file)
        doc_type = self._detect_document_type(text)
        
        results = {
            'type_document': doc_type,
            'texte_complet': text[:1000] + "..."
        }

        for field, patterns in self.patterns.items():
            results[field] = self._find_match(text, patterns)

        return results

    def _extract_text(self, file) -> str:
        """Extrait le texte du PDF"""
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

    # ... (gardez le reste des méthodes existantes _detect_document_type, _find_match, etc.)