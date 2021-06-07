from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect, reverse

from .forms import DeliveryTimeForm, ServiceAddressForm, UserForm, AddressForm, UserUpdateForm
from .models import DeliveryTime
from .models import ServiceAddress
from .models import User
from .models import Address

# Create your views here.


class UserView:
    @classmethod
    def list_users(cls, request):
        return redirect('login')

    @classmethod
    def create_users(cls, request):
        if request.method == 'POST':
            form = UserForm(request.POST)
            password = request.POST['password']
            if form.is_valid():
                user = form.save()
                user.password = make_password(password)
                user.save()
                login(request, user)
                return redirect('home')
        else:
            form = UserForm()
        return render(request, 'registration/create_customer.html', {'form': form})

    @classmethod
    def update_users(cls, request, username):
        user = get_object_or_404(User, username=username)
        form = UserUpdateForm(request.POST or None, instance=user)

        if request.method == 'POST':
            if form.is_valid():
                user = form.save()
                return redirect('update_customer', user.username)

        return render(request, '../templates/registration/update_custumer.html', {'form': form})


class AddressView:

    @classmethod
    def create_address(cls, request, username):
        user = get_object_or_404(User, username=username)
        form = AddressForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                address = form.save()
                address.user = user
                address.save()
                return redirect('list_customer_address', user.username)
        return render(request, '../templates/address/create_address.html', {'form': form})

    @classmethod
    def list_address(cls, request, username):
        user = get_object_or_404(User, username=username)
        addresses = Address.objects.filter(user=user)

        return render(request, '../templates/address/list_address.html', {'addresses': addresses})


def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'email ou senha estão incorretos')

    return render(request, 'registration/login.html')


def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('home')
    return redirect('login')


def customer_home(request):
    if request.user.is_authenticated:
        return redirect('update_customer', request.user.username)
    return redirect('login')


def home(request):
    return render(request, 'home.html')


def admin_home(request):
    if request.user.is_authenticated:
        return render(request, 'admin/home.html')
    return redirect('login')


def list_admin(request):
    if request.user.is_authenticated:
        admins = User.objects.filter(is_admin=True)

        return render(request, 'admin/manage_admin.html', {
            "admins": admins,
        })
    return redirect('login')


def add_admin(request):
    if request.user.is_authenticated:
        users = User.objects.filter(is_admin=False)

        return render(request, 'admin/add_admin.html', {
            "users": users,
        })
    return redirect('login')


def seller_home(request):
    if request.user.is_authenticated:
        return render(request, 'seller/home_seller.html')
    return redirect('login')


def request_seller(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            sale_description = request.POST['sale_description']
            if (sale_description is None):
                messages.error(request, 'A descrição é o obrigatoria!')
            else:
                if request.user.is_authenticated:
                    user = request.user
                    user.seller_status = 'P'  # request permision
                    user.sale_description = sale_description
                    user.save()

        return render(request, 'seller/home_seller.html')
    return redirect('login')


def manage_seller(request):
    if request.user.is_authenticated:
        sellers = User.objects.filter(seller_status='P')
        return render(request, 'seller/manage_request_seller.html', {
            "sellers": sellers,
        })
    return redirect('login')


def view_seller_request(request, user_id):
    if request.user.is_authenticated:
        user = User.objects.get(pk=user_id)
        return render(request, 'seller/view_request_seller.html', {
            "user": user,
        })
    return redirect('login')


def refuse_seller_request(request):
    if request.user.is_authenticated:
        service_address_id = None
        if request.method == 'POST':
            user_id = request.POST['user_id']
            user = User.objects.get(pk=user_id)
            user.is_seller = False
            user.seller_status = 'R'
            user.save()

        return HttpResponseRedirect(reverse('seller_manage'))
    return redirect('login')


def approve_seller_request(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            user_id = request.POST['user_id']
            user = User.objects.get(pk=user_id)
            user.is_seller = True
            user.seller_status = 'A'
            user.save()

        return HttpResponseRedirect(reverse('seller_manage'))
    return redirect('login')


def make_admin(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            user_id = request.POST['user_id']
            user = User.objects.get(pk=user_id)
            user.is_admin = True
            user.save()

        return HttpResponseRedirect(reverse('manage_admin'))
    return redirect('login')


def remove_admin(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            admin_id = request.POST['admin_id']
            user = User.objects.get(pk=admin_id)
            user.is_admin = False
            user.save()

        return HttpResponseRedirect(reverse('manage_admin'))
    return redirect('login')


class ServiceAddressView:
    @classmethod
    def list_service_address(cls, request):
        if request.user.is_authenticated:
            user = request.user
            if user.id:
                service_address = ServiceAddress.objects.filter(user=user.id)
            else:
                service_address = ServiceAddress.objects.all()

            return render(request, 'service_address/home.html', {
                "services_address": service_address,
            })
        return redirect('login')

    @classmethod
    def create_service_address(cls, request):
        form = ServiceAddressForm()
        if request.user.is_authenticated:
            user = request.user
            if request.method == 'POST':
                form = ServiceAddressForm(request.POST or None)
                if form.is_valid():
                    service_address = form.save(commit=False)
                    service_address.user = user
                    service_address.save()

                    return redirect('list_service_address')

            return render(request, '../templates/service_address/create.html', {
                'form': form,
                'user_id': user
            })
        return redirect('login')

    @classmethod
    def update_service_address(cls, request, service_address_id):
        service_address = get_object_or_404(
            ServiceAddress, id=service_address_id)
        if request.user.is_authenticated:
            form = ServiceAddressForm(instance=service_address)
            user = request.user
            if request.method == 'POST':
                form = ServiceAddressForm(
                    request.POST, instance=service_address)
                if form.is_valid():
                    service_address = form.save(commit=False)
                    service_address.user = user
                    service_address.save()

                    return redirect('list_service_address')

            return render(request, '../templates/service_address/create.html', {
                'form': form,
                'post': service_address,
                'service_address': service_address
            })
        return redirect('login')

    @classmethod
    def delete_service_address(cls, request):
        if request.user.is_authenticated:
            if request.method == 'POST':
                service_address_id = request.POST['service_address_id']
                service_address = get_object_or_404(
                    ServiceAddress, id=service_address_id)

                service_address.delete()
                return redirect('list_service_address')
        return redirect('login')


class DeliveryTimeView:
    @classmethod
    def list_delivery_time(cls, request, service_address_id):
        if request.user.is_authenticated:
            if service_address_id:
                delivery_time = DeliveryTime.objects.filter(
                    service_address=service_address_id)
            else:
                delivery_time = DeliveryTime.objects.all()

            return render(request, '../templates/delivery_time/home.html', {
                "delivery_times": delivery_time,
                'service_address_id': service_address_id,
            })
        return redirect('login')

    @classmethod
    def create_delivery_time(cls, request, service_address_id):
        if request.user.is_authenticated:
            service_address = get_object_or_404(
                ServiceAddress, id=service_address_id)
            form = DeliveryTimeForm()

            if request.method == 'POST':
                form = DeliveryTimeForm(request.POST or None)
                if form.is_valid():
                    delivery_time = form.save(commit=False)
                    delivery_time.service_address = service_address
                    delivery_time.save()

                    return redirect('list_delivery_time', service_address_id=service_address_id)

            return render(request, '../templates/delivery_time/create.html', {
                'form': form,
                'service_address_id': service_address_id
            })
        return redirect('login')

    @classmethod
    def update_delivery_time(cls, request, delivery_time_id):
        if request.user.is_authenticated:
            delivery_time = get_object_or_404(
                DeliveryTime, id=delivery_time_id)
            service_address = delivery_time.service_address
            form = DeliveryTimeForm(instance=delivery_time)

            if request.method == 'POST':
                form = DeliveryTimeForm(request.POST, instance=delivery_time)
                if form.is_valid():
                    delivery_time = form.save(commit=False)
                    delivery_time.service_address = service_address
                    delivery_time.save()

                    return redirect(
                        'list_delivery_time', service_address_id=delivery_time.service_address.id)

            return render(request, '../templates/delivery_time/create.html', {
                'form': form,
                'post': delivery_time,
                'delivery_time': delivery_time
            })
        return redirect('login')

    @classmethod
    def delete_delivery_time(cls, request):
        if request.user.is_authenticated:
            service_address_id = None
            if request.method == 'POST':
                delivery_time_id = request.POST['delivery_time_id']
                delivery_time = get_object_or_404(
                    DeliveryTime, id=delivery_time_id)
                service_address_id = delivery_time.service_address.id

                delivery_time.delete()

            return redirect('list_delivery_time', service_address_id=service_address_id)
        return redirect('login')
