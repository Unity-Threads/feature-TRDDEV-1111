from django.shortcuts import render, redirect
from django.contrib import auth
# shop/views.py
from django.http import JsonResponse
from .models import Category

def get_enabled_categories(request):
    categories = Category.objects.filter(is_enabled=True)
    data = [
        {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "images": category.image_urls,
            "link": category.link
        }
        for category in categories
    ]
    return JsonResponse({"categories": data})

# -------------------------------
# Home / Landing
# -------------------------------
def home(request):
    categories = Category.objects.filter(is_enabled=True).order_by('order')
    return render(request, 'landing/landing.html', {'categories': categories})

def landing(request):
    categories = Category.objects.filter(is_enabled=True).order_by('order')
    return render(request, "registration/landing.html", {'categories': categories})
# <<<<<<< HEAD

# =======
def update_username(request):
    mobile_view_user_name=getElementByClassName("user-name")
    mobile_view_user_name.innerHTML=request.user.username
    return JsonResponse({"success": True})
    
# -------------------------------
# Pages
# -------------------------------
def shop_by_season(request):
    return render(request, 'cartPage/shopbyseason.html')

def high_vibes(request):
    return render(request, 'cartPage/highvibes.html')

def low_vibes(request):
    return render(request, 'cartPage/lowvibes.html')

def accessories(request):
    return render(request, 'cartPage/accessories.html')

def shop_now(request):
    return render(request, 'cartPage/shopnow.html')
# >>>>>>> 025ad7353ca71db9ed4fe07f4c1a9ab52b62df89

def logout_page(request):
    auth.logout(request)
    return redirect("home")
