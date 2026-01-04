from django.shortcuts import render
from .models import TermsPage

def terms_view(request):
    terms = TermsPage.objects.prefetch_related('categories').first()
    return render(request, 'terms_co/terms.html', {'terms': terms})
