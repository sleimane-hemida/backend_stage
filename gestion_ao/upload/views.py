from django.shortcuts import render
from .parser import PDFParser

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']
            parser = PDFParser()
            extracted_data = parser.parse_pdf(file)
            
            return render(request, 'upload/result.html', {
                'data': extracted_data,
                'filename': file.name
            })
            
        except Exception as e:
            return render(request, 'upload/upload.html', {
                'error': f"Erreur lors du traitement : {str(e)}"
            })
    
    return render(request, 'upload/upload.html')