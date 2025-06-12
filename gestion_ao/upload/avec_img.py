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
        r"(?:(?:\b(?:Montant|Montant total HT|Montant TTC|budget|subvention|prix|financement|dotation|valeur)\b)[^\n:]*?(?:s['’]élève\s+à|est\s+de|de|:|-)?)?\s*([0-9]{1,3}(?:[ \.\u202f]?[0-9]{3})*(?:[.,][0-9]+)?)(?:\s*\(([^)]+)\))?\s*(FCFA|MRU|€|DHS|TTC)?",
        texte,
        re.IGNORECASE
    )
    montant = None
    for value, lettres, currency in montant_matches:
        digits = re.sub(r"[^\d]", "", value)
        if digits and len(digits) >= 7:  # au moins 6 chiffres (ex : 100000)
            montant = f"{value.strip()} ({lettres}) {currency}".strip() if lettres else f"{value.strip()} {currency}".strip()
            break

    # Emails
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", texte)
    email = emails[0] if emails else None

    # Téléphones format Mauritanie +222 ou 00222 avec espaces/tirets
    phones = re.findall(r"((?:\+222|00222)[\s\-]*(?:\d{2}[\s\-]*){3,5})", texte)
    telephones = [re.sub(r"[\s\-]", "", p) for p in phones]

    def clean_number(num):
        return re.sub(r"^(?:\+222|00222)", "", num)

    telephone = None
    for num in telephones:
        if len(clean_number(num)) >= 8:
            telephone = num
            break


    # Date limite
    dates = re.findall(r"(?:date\s*(limite|butoir|clôture|dépôt|livraison|au plus tard|)[^:\n]*[:\-]?\s*)(\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4})", texte, re.IGNORECASE)
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



import re

def extract_selection_criteria(texte: str) -> list:
    text = texte.lower()
    """
    Extrait les critères de sélection ou de présélection à partir du texte brut.
    Retourne une liste de critères ou une chaîne vide si rien n'est trouvé.
    """
    # Normaliser le texte

    # Expressions possibles pour détecter le début des critères
    pattern_start = re.compile(
        r"(crit[eè]res\s+de\s+(pré)?sélection\s*:?|la\s+sélection\s+se\s+fera\s+sur\s+la\s+base\s+des\s+crit[eè]res\s+suivants\s*:?)"
    )

    # Trouver le début
    match = pattern_start.search(text)
    if not match:
        return []

    start_idx = match.end()

    # Extraire la partie du texte après l’indice trouvé (max 1000 caractères pour ne pas tout prendre)
    sub_text = text[start_idx:start_idx + 1000]

    # Couper à une fin probable (autre section)
    stop_words = [
        "composition du dossier", "durée", "mode de sélection", "adresse", "contact",
        "le dossier doit contenir", "dossier de candidature", "documents demandés"
    ]
    for word in stop_words:
        stop_idx = sub_text.find(word)
        if 0 < stop_idx < 500:
            sub_text = sub_text[:stop_idx]
            break

    # Extraire les lignes avec des puces ou tirets ou points-virgules
    lines = re.split(r'[\n\r]+|•|-|–|;', sub_text)

    # Nettoyer et filtrer
    cleaned_criteria = []
    for line in lines:
        line = line.strip(" :;.-\n\r\t")
        if len(line) > 20 and not line.startswith("le dossier"):
            cleaned_criteria.append(line.capitalize())

    return cleaned_criteria

def extract_selection_criteria_from_table(text: str) -> list:
    """
    Fonction qui tente d'extraire les lignes de critères même si elles proviennent de tableaux mal formatés.
    """
    text = text.lower()
    lines = text.split("\n")
    keywords = [
        "expérience", "qualification", "diplôme", "compétence", "formation",
        "références", "missions similaires", "année", "durée", "projet",
        "score", "note", "barème", "pondération", "%"
    ]

    extracted_lines = []
    for line in lines:
        line_clean = line.strip("•-–:\t ").strip()
        if any(k in line_clean for k in keywords) and len(line_clean) > 10:
            extracted_lines.append(line_clean)

    return extracted_lines



if __name__ == "__main__":
    pdf_path = r"C:\Users\lapto\Downloads\exemple1AMI.pdf"  # Change ici si besoin
    texte_complet = extract_all_text_from_pdf(pdf_path)

    print("\n--- TEXTE EXTRACTE ---\n")
    print(texte_complet)

    print("\n--- ANALYSE ---\n")
    resultats = analyze_text(texte_complet)
    for cle, val in resultats.items():
        print(f"{cle.capitalize()} : {val}")

    
    print("\n--- CRITÈRES DE SÉLECTION ---\n")
    criteres = extract_selection_criteria(texte_complet)

    if criteres:
        print("\n--- CRITÈRES DÉTECTÉS ---\n")
        for critere in criteres:
            print(f"- {critere}")
    else:
        print("\nAucun critère détecté via l'extraction standard. Recherche dans les tableaux...\n")
        criteres_tableau = extract_selection_criteria_from_table(texte_complet)

        if criteres_tableau:
            print("--- CRITÈRES DÉTECTÉS (TABLEAU) ---")
            for critere in criteres_tableau:
                print(f"- {critere}")
        else:
                print("Aucun critère trouvé, même dans les tableaux.")