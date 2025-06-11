from pdf2image import convert_from_path
import pytesseract
import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# Chemin vers tesseract.exe sur ta machine
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# Variable d'environnement obligatoire pour que Tesseract trouve ses données de langue
os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR\tessdata"

def extract_all_text_from_pdf(pdf_path):
    print("Conversion du PDF en images...")
    images = convert_from_path(pdf_path, poppler_path=r"C:\poppler\Library\bin")

    full_text = ""
    for i, image in enumerate(images):
        print(f"OCR de la page {i+1}...")
        text = pytesseract.image_to_string(image, lang='fra')  # langue française
        full_text += text + "\n"

    return full_text

def analyze_text(texte):
    # Montant avec détection étendue
    montant_matches = re.findall(
        r"(?:(?:\b(?:montant|budget|salaire|subvention|coût|prix|enveloppe|financement|dotation|valeur)\b)[^\n:]*?(?:s['’]élève\s+à|est\s+de|de|:|-)?)?\s*([0-9]{1,3}(?:[ \.\u202f]?[0-9]{3})*(?:[.,][0-9]+)?)(?:\s*\(([^)]+)\))?\s*(FCFA|MRU|€|DHS|TTC)?",
        texte,
        re.IGNORECASE
    )
    montant = None
    for value, lettres, currency in montant_matches:
        digits = re.sub(r"[^\d]", "", value)
        if digits and len(digits) >= 6:  # au moins 6 chiffres (ex : 100000)
            montant = f"{value.strip()} ({lettres}) {currency}".strip() if lettres else f"{value.strip()} {currency}".strip()
            break

    # Emails
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", texte)
    email = emails[0] if emails else None

    # Téléphones
    phones = re.findall(r"\+?\d{1,3}[\s\-]?\d{2,3}[\s\-]?\d{2,3}[\s\-]?\d{2,3}", texte)
    telephone = next((p for p in phones if len(re.sub(r"\D", "", p)) >= 8), None)

    # Date limite
    dates = re.findall(r"(?:date\s*(limite|butoir|clôture|dépôt|livraison)[^:\n]*[:\-]?\s*)(\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4})", texte, re.IGNORECASE)
    date_limite = dates[0][1] if dates else None

    # Objet
    objet_match = re.search(r"(objet\s*[:\-]?\s*)(.+?)(?=\n|\.)", texte, re.IGNORECASE)
    objet = objet_match.group(2).strip() if objet_match else None

    return {
        "montant": montant,
        "email": email,
        "téléphone": telephone,
        "date_limite": date_limite,
        "objet": objet
    }

if __name__ == "__main__":
    pdf_path = r"C:\Users\lapto\Downloads\8370.pdf"  # Change ici si besoin
    texte_complet = extract_all_text_from_pdf(pdf_path)

    print("\n--- TEXTE EXTRACTE ---\n")
    print(texte_complet)

    print("\n--- ANALYSE ---\n")
    resultats = analyze_text(texte_complet)
    for cle, val in resultats.items():
        print(f"{cle.capitalize()} : {val}")
