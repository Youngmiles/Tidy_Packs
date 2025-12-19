from django.shortcuts import render, redirect

# Create your views here.

def home(request):
    return render(request, 'index.html', {'name': 'home'})

def product_landing(request):
    return render(request, 'products.html', {'name': 'products'})


from django.shortcuts import render
from django.contrib import messages
from .models import Contact

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Basic validation
        if not name or not email or not message:
            messages.error(request, 'Please fill in all required fields.')
        else:
            try:
                # Save to database
                Contact.objects.create(
                    name=name,
                    email=email,
                    message=message
                )
                messages.success(request, 'Your message has been sent successfully!')
            except Exception as e:
                messages.error(request, 'An error occurred while sending your message. Please try again.')

    return render(request, 'contact.html', {'name': 'contact'})

from .forms import UserRegistrationForm
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserLoginForm
from .models import Contact
import logging

logger = logging.getLogger(__name__)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('login')  # Adjust to your home URL
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form, 'name': 'register'})



from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm


def user_login(request):
    if request.method == 'POST':
        logger.debug(f"POST data: {request.POST}")
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful!')
            next_url = request.POST.get('next', request.GET.get('next', 'dashboard'))
            return redirect(next_url)
        else:
            logger.debug(f"Form errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}" if field != '__all__' else error)
    else:
        form = UserLoginForm()
    
    next_url = request.GET.get('next', '')
    return render(request, 'login.html', {'form': form, 'next': next_url})
from django.http import JsonResponse

@login_required
def dashboard(request):
    active_orders = Order.objects.filter(
        user=request.user,
        status__in=['pending', 'processing', 'shipped']
    ).count()
    pending_quotes = Order.objects.filter(
        user=request.user,
        status='pending'
    ).count() if 'Order' in globals() else 0
    total_orders = Order.objects.filter(user=request.user).count()
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'active_orders': active_orders,
            'pending_quotes': pending_quotes,
            'total_orders': total_orders,
        })

    context = {
        'active_orders': active_orders,
        'pending_quotes': pending_quotes,
        'total_orders': total_orders,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard.html', context)

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

from .forms import UserLoginForm, AdminLoginForm


def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(data=request.POST)
        logger.debug(f"POST data: {request.POST}")
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser:
                login(request, user)
                messages.success(request, 'Admin login successful!')
               
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'This account is not a superuser account.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = AdminLoginForm()
    return render(request, 'admin_login.html', {'form': form})

from django.contrib.auth.decorators import login_required, user_passes_test


def admin_logout(request):
    logout(request)
    messages.success(request, 'Admin logged out successfully!')
    return redirect('admin_login')




from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Order
from .forms import OrderForm
from django.views.decorators.csrf import csrf_exempt
# views.py (Add this to your app's views.py file, assuming this is the client-facing views)
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Product, Order  # Import Product from earlier, and Order

def products(request):
    # Fetch all products from DB, ordered by newest first
    dynamic_products = Product.objects.all().order_by('-created_at')
    context = {
        'dynamic_products': dynamic_products,
    }
    return render(request, 'clientproduct.html', context)

@login_required
@require_http_methods(["POST"])
def create_order(request):
    try:
        product_name = request.POST.get('product_name')
        customer_name = request.POST.get('customer_name')
        email = request.POST.get('email')
        quantity = int(request.POST.get('quantity', 0))
        delivery_address = request.POST.get('delivery_address')
        notes = request.POST.get('notes', '')

        if not all([product_name, customer_name, email, delivery_address, quantity > 0]):
            return JsonResponse({'success': False, 'error': 'Missing required fields or invalid quantity.'}, status=400)

        # Create the order using the logged-in user
        order = Order.objects.create(
            user=request.user,
            product_name=product_name,
            quantity=quantity,
            delivery_address=delivery_address,
            notes=notes
        )
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'message': 'Swap request submitted successfully!'
        })
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid quantity.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'An error occurred while creating the order.'}, status=500)
    
@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'client_orders.html', {'orders': orders})

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from .models import Order
from .forms import OrderForm
from django.core.mail import send_mail

@login_required
def manage_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'manage_orders.html', {'orders': orders})

@login_required
def update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['pending', 'processing', 'shipped', 'delivered']:
            order.status = status
            order.save()
            # Send email notification
            send_mail(
                'Order Status Update',
                f'Your order (ID: {order.id}) for {order.product_name or "No Product"} is now {order.get_status_display()}.',
                'from@tidypack.ke',
                [order.user.email],
                fail_silently=True,
            )
        return redirect('manage_orders')
    return redirect('manage_orders')

@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.delete()
        return redirect('manage_orders')
    return redirect('manage_orders')


@login_required
def manage_users(request):
    users = User.objects.all().order_by('id')
    return render(request, 'manage_users.html', {'users': users})

@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        is_staff = request.POST.get('is_staff') == 'true'
        
        if User.objects.exclude(id=user_id).filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.exclude(id=user_id).filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            user.username = username
            user.email = email
            user.first_name = first_name
            user.is_staff = is_staff
            user.save()
            messages.success(request, f'User {user.username} updated successfully.')
        return redirect('manage_users')
    return redirect('manage_users')

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        if user.is_superuser:
            messages.error(request, 'Cannot delete a superuser.')
        else:
            user.delete()
            messages.success(request, f'User {user.username} deleted successfully.')
        return redirect('manage_users')
    return redirect('manage_users')


@login_required
def reports(request):
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_users = User.objects.count()
    recent_orders = Order.objects.order_by('-created_at')[:5]
    order_status_counts = {
        'pending': Order.objects.filter(status='pending').count(),
        'processing': Order.objects.filter(status='processing').count(),
        'shipped': Order.objects.filter(status='shipped').count(),
        'delivered': Order.objects.filter(status='delivered').count(),
    }
    return render(request, 'reports.html', {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_users': total_users,
        'recent_orders': recent_orders,
        'order_status_counts': order_status_counts
    })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access the admin dashboard.')
        return redirect('home')
    
    # Fetch dashboard metrics
    total_orders = Order.objects.count()
    pending_quotes = Order.objects.filter(status='pending').count() if Order else 0
    active_users = User.objects.filter(is_active=True).count()
    recent_orders = Order.objects.order_by('-created_at')[:5]  # Latest 5 orders
    
    context = {
        'total_orders': total_orders,
        'pending_quotes': pending_quotes,
        'active_users': active_users,
        'recent_orders': recent_orders,
    }
    return render(request, 'admin_dashboard.html', context)
# views.py (Full cleaned-up file - replace your entire views.py with this)
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ProductForm
from .models import Product

def product_manage(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('product_manage')
        else:
            messages.error(request, 'Error creating product. Please check the form.')
    else:
        form = ProductForm()

    # Always fetch products here (for both GET and invalid POST)
    products = Product.objects.all().order_by('-created_at')
    print(f"DEBUG: Rendering with {products.count()} products")  # Remove after testing

    context = {
        'form': form,
        'products': products,
    }
    return render(request, 'create_product.html', context)

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_update.html'
    success_url = reverse_lazy('product_manage')

    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating product. Please check the form.')
        return super().form_invalid(form)

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('product_manage')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Product deleted successfully!')
        return super().delete(request, *args, **kwargs)