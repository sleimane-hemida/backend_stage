import fitz  # PyMuPDF
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')



with fitz.open("C://Users//lapto//Downloads//AVIS_D.pdf") as doc:
    text = ""
    for page in doc:
        text += page.get_text()

print("----- TEXTE EXTRAIT DU PDF -----")
print(text[:1000])  # Affiche les 1000 premiers caractères
