from django.shortcuts import render
from .models import FAQCategory
from django.http import JsonResponse
from .models import FAQCategory

def faq_page(request):
    categories = FAQCategory.objects.prefetch_related('faqs').all()
    return render(request, 'faqpage/faq.html', {'categories': categories})

def get_faqs_by_category(request, cat_id):
    category = FAQCategory.objects.get(id=cat_id)
    faqs = category.faqs.all()

    data = {
        "faqs": [
            {
                "question": f.question,
                "answer": f.answer
            }
            for f in faqs
        ]
    }
    return JsonResponse(data)
