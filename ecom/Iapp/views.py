# Create your views here.

from datetime import datetime
import json
import time
from django.shortcuts import render, redirect, get_object_or_404
from .models import *  # Import your Product model
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q 
from django.forms import formset_factory, inlineformset_factory, modelformset_factory
from rest_framework import mixins, viewsets 
from haystack.query import SearchQuerySet 
from .serializers import ProductSearchSerializer 
from haystack.generic_views import SearchView
from django.views.decorators.http import require_POST
from .utils import send_otp
import pyotp

def test(request):
    return render(request, 'base.html', {})

def home(request):
    products = Products.objects.filter(deleted_at__isnull=True)
    unique_product_ids = set()
    filtered_images = []

    for image in ProductsImages.objects.all():
        if image.product_id not in unique_product_ids:
            unique_product_ids.add(image.product_id)
            filtered_images.append(image)

        # Fetch quantity from ProductsInventory based on product_id
    # product_ids = [product.id for product in products]
    # inventory_data = Products_variation.objects.filter(product__id__in=product_ids)

    # # Create a dictionary mapping product_id to quantity
    # inventory_dict = {item.product.id: item.quantity for item in inventory_data}

    # # Attach quantity information to each product
    # for product in products:
    #     product.quantity = inventory_dict.get(product.id, 0) 

    return render(request, "home.html", {'products': products, 'images':filtered_images})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Send an email to the site owner (you)
            subject_owner = f'New Contact Form Submission from {name}'
            body_owner = f"Name: {name}\nEmail: {email}\nMessage: {message}"
            sender_email_owner = 'ifourengineering@gmail.com'  # Update with your email address

            send_mail(subject_owner, body_owner, 'settings.EMAIL_HOST_USER', [sender_email_owner])

            # Send a confirmation email to the user
            subject_user = 'Thank you for your feedback!'
            body_user = 'Dear {},\n\nThank you for your feedback! We have received your message and will get back to you soon.'.format(name)
            sender_email_user = 'ifourengineering@gmail.com'  # Update with your email address

            send_mail(subject_user, body_user, sender_email_user, [email])

            # Redirect to a success page
            return HttpResponseRedirect(reverse('success'))
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


def success(request):
    return render(request, 'success.html')


def register(request):
    if request.method == 'POST':
        user_form = RegistrationForm(request.POST)
        address_form = AddressForm(request.POST)

        if user_form.is_valid() and address_form.is_valid():
            # Save the user data to the User table in the session
            request.session['user_data'] = user_form.cleaned_data

            # Save the address data to the Address table in the session
            request.session['address_data'] = address_form.cleaned_data

            send_otp(request)
            return redirect('verify_otp')

    else:
        user_form = RegistrationForm()
        address_form = AddressForm()

    return render(request, 'register.html', {'user_form': user_form, 'address_form': address_form})

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        otp_secret_key = request.session.get('otp_secret_key')
        otp_valid_date = request.session.get('otp_valid_date')

        if otp_secret_key and otp_valid_date is not None:
            valid_until = datetime.fromisoformat(otp_valid_date)

            if valid_until > datetime.now():
                totp = pyotp.TOTP(otp_secret_key, interval=60)
                if totp.verify(entered_otp):
                    # Save the form contents after OTP verification
                    user_form = RegistrationForm(request.session['user_data'])
                    address_form = AddressForm(request.session['address_data'])

                    if user_form.is_valid() and address_form.is_valid():
                        user = user_form.save()
                        address = address_form.save(commit=False)
                        address.user = user
                        address.save()

                        login(request, user)

                        del request.session['otp_secret_key']
                        del request.session['otp_valid_date']
                        del request.session['user_data']
                        del request.session['address_data']
                        return redirect('home')
                    else:
                        return render(request, 'failure.html')
                else:
                    return render(request, 'failure.html')

    return render(request, 'otp.html')


@login_required(login_url="/login")
def account(request):
    user = request.user
    address = UsersAddress.objects.get(user=user)
    return render(request, 'account.html', {'user':user, 'info':address})


@login_required(login_url="/login")
def modify_account(request):
    user = request.user
    address = UsersAddress.objects.get(user=user)
    if request.method == 'POST':
        address_form = AddressForm(request.POST, instance=address)

        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = user
            address.save()

            messages.success(request, 'Account updated successfully.')
            return redirect('account')
    else:
        address_form = AddressForm(instance=address)

    return render(request, 'modify_account.html', {'address_form': address_form})


@user_passes_test(lambda u: u.is_superuser)
def add_category(request):
    if request.method == 'POST':
        form = AddCategoryform(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AddCategoryform()
    return render(request, 'add_category.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def add_product(request):
    VariationFormSet = formset_factory(AddVariationForm, extra=1)

    if request.method == 'POST':
        form = AddProductForm(request.POST)
        variation_formset = VariationFormSet(request.POST, prefix='variations')

        if form.is_valid() and variation_formset.is_valid():
            product = form.save()

            # Save variations
            for variation_form in variation_formset:
                if variation_form.is_valid():
                    variation = variation_form.save(commit=False)
                    variation.parent = product
                    variation.save()

            # Handle images as before
            images = request.FILES.getlist('images')
            for image in images:
                image_instance = ProductsImages.objects.create(
                    product=product,
                    image=image
                )


            return redirect('home')

    else:
        form = AddProductForm()
        variation_formset = VariationFormSet(prefix='variations')

    return render(request, 'add_product.html', {'form': form, 'variation_formset': variation_formset})


@user_passes_test(lambda u: u.is_superuser)
def delete_product(request, product_id):
    product = Products.objects.get(id=product_id)
    product.deleted_at = datetime.now()
    product.save()
    return redirect('home')


def search(request):
    query = request.GET.get('q', '')
    results = SearchQuerySet().filter(content=query).exclude(id__in=Products.objects.filter(deleted_at__isnull=False).values_list('id', flat=True))
    results += SearchQuerySet().filter(content=query).filter(id__in=Products_variation.objects.filter(deleted_at__isnull=True).values_list('parent', flat=True))
    images = ProductsImages.objects.all()


    return render(request, 'results.html', {'products': results, 'query': query, 'images':images})


def autocomplete_view(request):
    query = request.GET.get('q', '')
    results = SearchQuerySet().autocomplete(content_auto=query)[:5]  # Limit results to 5 for simplicity

    suggestions = [{'value': result.object.name, 'data': result.object.pk} for result in results]

    return JsonResponse({'suggestions': suggestions})

def view_product(request):
    parent = Products.objects.get(id=request.GET.get('id',''))
    products = Products_variation.objects.filter(parent=parent)
    image = ProductsImages.objects.filter(product=parent)

    return render(request, 'product_detail.html', {'parent':parent, 'products': products, 'images':image})


@user_passes_test(lambda u: u.is_superuser)
def modify_product(request):
    product_id = request.GET.get('id', '')  # Get the product ID from the URL parameter
    product = Products.objects.get(pk=product_id)
    image = ProductsImages.objects.filter(product=product)
    VariationFormSet = inlineformset_factory(Products, Products_variation, AddVariationForm, extra=0, can_delete=False)


    if request.method == 'POST':
        product_form = AddProductForm(request.POST, instance=product)
        variation_formset = VariationFormSet(request.POST, instance=product)

        if product_form.is_valid() and variation_formset.is_valid():
            product_form.save()
            variation_formset.save()

            return redirect(reverse('product_detail') + f'?id={product_id}')
    else:
        product_form = AddProductForm(instance=product)
        variation_formset = VariationFormSet(instance=product)

    return render(request, 'modify_product.html', {'product_form': product_form, 'product': product, 'image': image, 'variation_formset': variation_formset})
        

@login_required(login_url="/login")
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user).filter(order_id__isnull=True).select_related('product', 'order')
    orders = Orders.objects.filter(user=request.user)
    products = Cart.objects.filter(user=request.user).filter(order_id__isnull=False)
    return render(request, 'cart.html', {'cart_items': cart_items, 'orders':orders, 'products':products})


@login_required(login_url="/login")
def add_to_cart(request):
    product_id = request.GET.get('id', '')  # Get the product ID from the URL parameter
    product = Products_variation.objects.get(pk=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product, order_id__isnull=True)
    if created:
        cart_item.quantity = 1
        cart_item.subtotal = product.price * cart_item.quantity
        cart_item.save()
    else:
        cart_item.quantity += 1
        cart_item.subtotal = product.price * cart_item.quantity
        cart_item.save()
    return redirect('view_cart')

@login_required(login_url="/login")
def remove_from_cart(request):
    cart_item_id = request.GET.get('id', '')  # Get the cart item ID from the URL parameter
    cart_item = Cart.objects.get(id=cart_item_id)
    cart_item.delete()
    return redirect('view_cart')


@login_required(login_url="/login")
def adjust_quantity_view(request, item_id):
    change = int(request.GET.get('change', 0))
    cart_item = Cart.objects.get(id=item_id)
    product = cart_item.product
    inventory = Products_variation.objects.get(id=product)
    if change+cart_item.quantity > inventory.quantity:
        messages.error(request, "Not enough inventory available.")
    else:
        cart_item.quantity = max(0, cart_item.quantity + change)
        cart_item.subtotal = cart_item.quantity * cart_item.product.price
        cart_item.save()
    
    return redirect('view_cart')


@login_required(login_url="/login")
def tqorder(request):
    cart_items = Cart.objects.filter(user=request.user).filter(order_id__isnull=True).select_related('product', 'order')
    total = 0
    for item in cart_items:
        product = item.product
        inventory = Products_variation.objects.get(id=product)
        if item.quantity > inventory.quantity:
            item.quantity = inventory.quantity
            item.subtotal = item.quantity * product.price
            item.save()
            messages.error(request, f"Not enough inventory for { product.parent.name }{product.id}. Updated to maximum number.")
            total = 0
            return redirect('view_cart')
        else:
            total += item.product.price * item.quantity
    order = Orders.objects.create(user=request.user, total_amount=total)
    for item in cart_items:
        item.order_id = order
        item.save()

        inventory = Products_variation.objects.get(id=item.product)
        inventory.quantity -= item.quantity
        inventory.save()

        subject_owner = f'New Order Placed by {request.user}'
        body_owner = f'A new order has been placed by {request.user}. Order ID: {order.id} \n Kindly login and check.'
        sender_email = 'ifourengineering@gmail.com'

        send_mail(subject_owner, body_owner, 'settings.EMAIL_HOST_USER', [sender_email])

        email = request.user.email
        subject_user = f'Order Placed'
        body_user = f'Your order has been placed successfully. Order ID: {order.id} Total amount: RM {total}'
        send_mail(subject_user, body_user, 'settings.EMAIL_HOST_USER', [email])


    return render(request, 'tqorder.html')


@user_passes_test(lambda u: u.is_superuser)
def view_orders(request):
    orders = Orders.objects.filter(status='Pending').select_related('user')
    for order in orders:
        order.cart_items = Cart.objects.filter(order=order)
        order.userd = UsersAddress.objects.get(user_id=order.user_id)

    histories = Orders.objects.exclude(status='Pending').select_related('user')
    for history in histories:
        history.cart_items = Cart.objects.filter(order=history)
        history.userd = UsersAddress.objects.get(user_id=history.user_id)

    return render(request, 'orders.html', {'orders':orders, 'histories':histories})

@user_passes_test(lambda u: u.is_superuser)
def accept_order(request):
    order_id = request.GET.get('id', '')  # Get the order ID from the URL parameter
    order = Orders.objects.get(id=order_id)
    order.status = 'Accepted'
    order.save()

    subject_owner = f'Order from {order.user} Accepted'
    body_owner = f'You have accepted an order from {order.user}. Order ID: {order.id}'
    sender_email = 'ifourengineering@gmail.com'

    send_mail(subject_owner, body_owner, 'settings.EMAIL_HOST_USER', [sender_email])

    email = order.user.email
    subject_user = f'Order Accepted'
    body_user = f'{ order.user },Congratulations! Your order has been accepted by Seller. Order ID: {order.id}'
    send_mail(subject_user, body_user, 'settings.EMAIL_HOST_USER', [email])
    
    return redirect('orders')

@user_passes_test(lambda u: u.is_superuser)
def decline_order(request):
    order_id = request.GET.get('id', '')  # Get the order ID from the URL parameter
    order = Orders.objects.get(id=order_id)
    order.status = 'Declined'
    order.save()

    items = Cart.objects.filter(order=order)
    for item in items:
        inventory = Products_variation.objects.get(id=item.product)
        inventory.quantity += item.quantity
        inventory.save()

    subject_owner = f'Order from {order.user} Declined'
    body_owner = f'You have declined an order from {order.user}. Order ID: {order.id}'
    sender_email = 'ifourengineering@gmail.com'

    send_mail(subject_owner, body_owner, 'settings.EMAIL_HOST_USER', [sender_email])

    email = order.user.email
    subject_user = f'Order Declined'
    body_user = f'{ order.user },Sorry! Your order has been declined by Seller for some reasons. Order ID: {order.id}'
    send_mail(subject_user, body_user, 'settings.EMAIL_HOST_USER', [email])    
    

    return redirect('orders')

@user_passes_test(lambda u: u.is_superuser)
def done_order(request):
    order_id = request.GET.get('id', '')  # Get the order ID from the URL parameter
    order = Orders.objects.get(id=order_id)
    order.status = 'Done'
    order.save()

    subject_owner = f'Order from {order.user} Done'
    body_owner = f'Congratulations! You have done an order from {order.user}. Order ID: {order.id}'
    sender_email = 'ifourengineering@gmail.com'

    send_mail(subject_owner, body_owner, 'settings.EMAIL_HOST_USER', [sender_email])

    email = order.user.email
    subject_user = f'Order Done'
    body_user = f'{ order.user },Thank you for choosing us! Your order has done. Order ID: {order.id} \n Please come again.'
    send_mail(subject_user, body_user, 'settings.EMAIL_HOST_USER', [email])

    return redirect('orders')