from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import UserProfile
from orders.models import Address, Order
from orders.forms import AddressForm
from shop.models import Wishlist


def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('shop:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Welcome! Your account has been created successfully.')
            return redirect('shop:home')
        else:
            # Show error toast for form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_label = form.fields.get(field).label if field in form.fields else field
                        messages.error(request, f'{field_label}: {error}')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('shop:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'shop:home')
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('shop:home')


@login_required
def dashboard(request):
    """User dashboard"""
    recent_orders = Order.objects.filter(user=request.user)[:5]
    wishlist_items = Wishlist.objects.filter(user=request.user)[:4]
    addresses = Address.objects.filter(user=request.user)[:2]
    
    context = {
        'recent_orders': recent_orders,
        'wishlist_items': wishlist_items,
        'addresses': addresses,
        'total_orders': Order.objects.filter(user=request.user).count(),
        'wishlist_count': Wishlist.objects.filter(user=request.user).count(),
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile(request):
    """User profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update user fields
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.save()
        
        # Update profile fields
        profile.phone = request.POST.get('phone', '')
        date_of_birth = request.POST.get('date_of_birth', '')
        if date_of_birth:
            profile.date_of_birth = date_of_birth
        else:
            profile.date_of_birth = None
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def addresses(request):
    """Manage addresses"""
    addresses = Address.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('accounts:addresses')
    else:
        form = AddressForm()
    
    context = {
        'addresses': addresses,
        'form': form,
    }
    return render(request, 'accounts/addresses.html', context)


@login_required
def add_address(request):
    """Add new address"""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            # If this is the first address or is_default is checked, set as default
            if not Address.objects.filter(user=request.user).exists() or form.cleaned_data.get('is_default'):
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
                address.is_default = True
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('accounts:addresses')
    else:
        form = AddressForm()
    
    return render(request, 'accounts/address_form.html', {'form': form})


@login_required
def edit_address(request, address_id):
    """Edit address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('accounts:addresses')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'accounts/address_form.html', {'form': form, 'address': address})


@login_required
def delete_address(request, address_id):
    """Delete address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully!')
    return redirect('accounts:addresses')


@login_required
def set_default_address(request, address_id):
    """Set default address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    address.is_default = True
    address.save()
    messages.success(request, 'Default address updated!')
    return redirect('accounts:addresses')


@login_required
def wishlist(request):
    """View wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    return render(request, 'accounts/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def order_history(request):
    """Order history"""
    orders = Order.objects.filter(user=request.user)
    
    return render(request, 'accounts/order_history.html', {'orders': orders})


@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})
