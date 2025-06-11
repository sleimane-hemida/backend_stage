import fitz  # PyMuPDF
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')




file_pathe = "C://Users//lapto//Downloads//AVIS_D.pdf"

def extract_info_from_pdf(file_pathe):
    with fitz.open(file_pathe) as doc:
        text = ""
        for page in doc:
            text += page.get_text()

    # Nettoyage éventuel
    text = text.replace('\n', ' ').strip()

    # Regex pour chercher les infos
    montant = re.findall(r"Montant\s*:\s*([\d\s\.,]+)", text)
    contact = re.findall(r"Contact\s*:\s*(.+?)(?=Email|Téléphone|$)", text)
    email = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    telephone = re.findall(r"(?:\+?\d[\d\s\-/]{7,}\d)", text)

    # Extraire un extrait de texte (ex. les 500 premiers caractères)
    extrait = text[:500]

    return {
        "montant": montant[0] if montant else "Non trouvé",
        "contact": contact[0].strip() if contact else "Non trouvé",
        "email": email[0] if email else "Non trouvé",
        "telephone": telephone[0] if telephone else "Non trouvé",
        "extrait": extrait,
    }
print(extract_info_from_pdf(file_pathe))
