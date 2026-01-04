from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Address

@login_required
def add_address(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        mobile = request.POST.get("mobile")
        address1 = request.POST.get("address1")
        address2 = request.POST.get("address2")
        landmark = request.POST.get("landmark")
        country = request.POST.get("country")
        state = request.POST.get("state")
        city = request.POST.get("city")
        pincode = request.POST.get("pincode")

        Address.objects.create(
            user=request.user,
            fullname=fullname,
            mobile=mobile,
            address1=address1,
            address2=address2,
            landmark=landmark,
            country=country,
            state=state,
            city=city,
            pincode=pincode
        )
        messages.success(request, "Address saved successfully!")
        return redirect("cartPage:cartPage")
    
    return render(request, "orders/add_address.html")


@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user).order_by("-id")  # latest first
    return render(request, "orders/address_list.html", {"addresses": addresses})

@login_required
def select_address(request, id):
    address = Address.objects.get(id=id, user=request.user)

    # unselect all
    Address.objects.filter(user=request.user).update(is_selected=False)

    # select chosen one
    address.is_selected = True
    address.save()

    return redirect('address:address_list')  # or your desired page


@login_required
def edit_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    if request.method == "POST":
        address.fullname = request.POST.get("fullname")
        address.mobile = request.POST.get("mobile")
        address.address1 = request.POST.get("address1")
        address.address2 = request.POST.get("address2")
        address.landmark = request.POST.get("landmark")
        address.country = request.POST.get("country")
        address.state = request.POST.get("state")
        address.city = request.POST.get("city")
        address.pincode = request.POST.get("pincode")
        address.save()
        messages.success(request, "Address updated successfully!")
        return redirect("address:address_list")
    
    return render(request, "orders/add_address.html", {"address": address})


@login_required
def delete_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully!")
    return redirect("address:address_list")
