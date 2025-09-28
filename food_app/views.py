
from django.db import transaction
from .razorpay_tester  import _generate_order_ref
from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils.timezone import now, timedelta
from .models import Order, Food, Stock
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Food, Menu, MealPlan, Order
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from .models import Order, Stock, Menu, MealPlan
from .forms import FoodForm
from .models import Food, Ingredient, Order, Restaurant, Chef, MealPlan, Discount, Stock, Allergy, Tag
from .forms import FoodForm, IngredientForm, TagForm, DiscountForm, StockForm, AllergyForm
from django.core.paginator import Paginator
from .models import Order
from .forms import OrderStatusForm
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from .models import Food, Order
from decimal import Decimal
from django.utils import timezone

# ---------- List All Foods ----------

def food_list(request):
    foods_qs = Food.objects.filter(available=True)
    paginator = Paginator(foods_qs, 8)  # 6 foods per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "foods": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
    }
    return render(request, "food_app/food_list.html", context)

# ---------- Food Detail ----------
def food_detail(request, food_id):
    food = get_object_or_404(Food, id=food_id)
    context = {'food': food}
    return render(request, 'food_app/food_detail.html', context)

# ---------- Menu ----------
def menu_list(request):
    menus = Menu.objects.all().order_by('-date')
    context = {'menus': menus}
    return render(request, 'food_app/menu_list.html', context)

# ---------- Place Order ----------
@login_required
def place_order(request, food_id):
    """
    Display food and create a local Order then create Razorpay order id and send to template.
    """
    food = get_object_or_404(Food, pk=food_id)

    if request.method == "POST":
        qty = int(request.POST.get('quantity', 1))
        # calculate total
        total_price = (food.price * Decimal(qty)).quantize(Decimal('0.01'))

        # create local order (PENDING)
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            food=food,
            quantity=qty,
            total_price=total_price,
            status='PENDING'
        )

        # create razorpay order (amount in paise)
        print("Razorpay Key ID in view:", settings.RAZORPAY_KEY_ID)  # Debug print
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create(dict(amount=int(total_price * 100),  # paise
                                                   currency='INR',
                                                   receipt=f'order_rcptid_{order.id}',
                                                   payment_capture=1))
        # save razorpay order id on our Order
        order.razorpay_order_id = razorpay_order.get('id')
        order.save()

        # send required details to template to open checkout
        context = {
            'food': food,
            'order': order,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order.get('id'),
            'amount': int(total_price * 100),  # paise
            'currency': 'INR',
        }
        return render(request, 'food_app/checkout.html', context)

    # GET: show product / order form
    return render(request, 'food_app/place_order.html', {'food': food})


# ---------- User Meal Plan ----------
@login_required
def meal_plan(request):
    plans = MealPlan.objects.filter(user=request.user)
    return render(request, 'food_app/meal_plan.html', {'plans': plans})


# Dashboard
@staff_member_required
def admin_food(request):
    foods = Food.objects.all().order_by('food_name')
    return render(request, 'food_app/admin_food.html', {'foods': foods})




@staff_member_required
def admin_orders(request,pk):
    orders = Order.objects.all().order_by('-ordered_at')
    return render(request, 'food_app/admin_orders.html', {'orders': orders})



@staff_member_required
def edit_order(request, pk):
    """
    View to edit/update an order (status, quantity, delivered_at, etc.)
    """
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            updated = form.save(commit=False)
            # if status changed to DELIVERED and delivered_at not set, set it
            if updated.status == 'DELIVERED' and not updated.delivered_at:
                updated.delivered_at = timezone.now()
            updated.save()
            form.save_m2m()  # not necessary here but safe
            messages.success(request, f'Order #{order.id} updated successfully.')
            return redirect('admin_order')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        # If order.delivered_at exists, convert to local input format (handled by widget usually)
        form = OrderStatusForm(instance=order)

    return render(request, 'admin/edit_order.html', {
        'form': form,
        'order': order,
    })


@staff_member_required
def delete_order(request, pk):
    """
    Confirm and delete an order. GET shows confirmation; POST performs deletion.
    """
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        order_id = order.id
        order.delete()
        messages.success(request, f'Order #{order_id} deleted.')
        return redirect('admin_order')

    # GET: show confirmation page
    return render(request, 'admin/delete_order.html', {
        'order': order,
    })
@staff_member_required
def admin_stock(request):
    stocks = Stock.objects.all()
    return render(request, 'food_app/admin_stock.html', {'stocks': stocks})

@staff_member_required
def admin_menu(request):
    menus = Menu.objects.all().order_by('-date')
    return render(request, 'food_app/admin_menu.html', {'menus': menus})

@staff_member_required
def admin_meal_plan(request):
    plans = MealPlan.objects.all()
    return render(request, 'food_app/admin_meal_plan.html', {'plans': plans})


# Add / Edit food (same as before)
@staff_member_required
def add_food(request):
    if request.method == "POST":
        form = FoodForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_food')
    else:
        form = FoodForm()
    return render(request, 'food_app/admin_add_food.html', {'form': form})

@staff_member_required
def edit_food(request, food_id):
    food = get_object_or_404(Food, id=food_id)
    if request.method == "POST":
        form = FoodForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            form.save()
            return redirect('admin_food')
    else:
        form = FoodForm(instance=food)
    return render(request, 'food_app/admin_add_food.html', {'form': form, 'edit': True, 'food': food})

# ---------- Delete Food ----------
@staff_member_required
def delete_food(request, food_id):
    food = get_object_or_404(Food, id=food_id)
    if request.method == "POST":
        food.delete()
        return redirect('admin_food')
    return render(request, 'food_app/admin_delete_food.html', {'food': food})



# -------------------- Ingredient --------------------
def ingredient_list(request):
    ingredients = Ingredient.objects.all()
    return render(request, 'food_app/ingredient_list.html', {'ingredients': ingredients})

def add_ingredient(request):
    form = IngredientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('admin_ingredient')
    return render(request, 'food_app/add_ingredient.html', {'form': form})

def edit_ingredient(request, id):
    ingredient = get_object_or_404(Ingredient, id=id)
    form = IngredientForm(request.POST or None, instance=ingredient)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('admin_ingredient')
    return render(request, 'food_app/add_ingredient.html', {'form': form, 'edit': True})

def delete_ingredient(request, id):
    ingredient = get_object_or_404(Ingredient, id=id)
    ingredient.delete()
    return redirect('admin_ingredient')



# -------------------- Restaurants & Chefs --------------------
def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'food_app/restaurant_list.html', {'restaurants': restaurants})

def chef_list(request):
    chefs = Chef.objects.select_related('restaurant').all()
    return render(request, 'food_app/chef_list.html', {'chefs': chefs})

# -------------------- Meal Plans --------------------
def mealplan_list(request):
    plans = MealPlan.objects.select_related('user').all()
    return render(request, 'food_app/mealplan_list.html', {'plans': plans})

# -------------------- Discounts & Stock --------------------
def discount_list(request):
    discounts = Discount.objects.all()
    return render(request, 'food_app/discount_list.html', {'discounts': discounts})

def stock_list(request):
    stock_items = Stock.objects.select_related('food').all()
    return render(request, 'food_app/stock_list.html', {'stock_items': stock_items})

# -------------------- Allergies & Tags --------------------
def allergy_list(request):
    allergies = Allergy.objects.all()
    return render(request, 'food_app/allergy_list.html', {'allergies': allergies})

def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'food_app/tag_list.html', {'tags': tags})


def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'food_app/tag_list.html', {'tags': tags})

def add_tag(request):
    form = TagForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('admin_tag')
    return render(request, 'food_app/add_tag.html', {'form': form})

def edit_tag(request, id):
    tag = get_object_or_404(Tag, id=id)
    form = TagForm(request.POST or None, instance=tag)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('admin_tag')
    return render(request, 'food_app/add_tag.html', {'form': form, 'edit': True})

def delete_tag(request, id):
    tag = get_object_or_404(Tag, id=id)
    tag.delete()
    return redirect('admin_tag')

# -------------------- Discounts --------------------
def discount_list(request):
    discounts = Discount.objects.all()
    return render(request, 'food_app/discount_list.html', {'discounts': discounts})

def add_discount(request):
    form = DiscountForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('admin_discount')
    return render(request, 'food_app/add_discount.html', {'form': form})

def edit_discount(request, pk):
    discount = get_object_or_404(Discount, id=pk)
    form = DiscountForm(request.POST or None, instance=discount)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('admin_discount')
    return render(request, 'food_app/add_discount.html', {'form': form, 'edit': True})

def delete_discount(request, id):
    discount = get_object_or_404(Discount, id=id)
    discount.delete()
    return redirect('admin_discount')

# -------------------- Stock --------------------
def stock_list(request):
    stocks = Stock.objects.select_related('food').all()
    return render(request, 'food_app/stock_list.html', {'stocks': stocks})

def add_stock(request):
    form = StockForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('admin_stock')
    return render(request, 'food_app/add_stock.html', {'form': form})

def edit_stock(request, id):
    stock = get_object_or_404(Stock, id=id)
    form = StockForm(request.POST or None, instance=stock)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('admin_stock')
    return render(request, 'food_app/add_stock.html', {'form': form, 'edit': True})

def delete_stock(request, id):
    stock = get_object_or_404(Stock, id=id)
    stock.delete()
    return redirect('admin_stock')

# -------------------- Allergies --------------------
def allergy_list(request):
    allergies = Allergy.objects.all()
    return render(request, 'food_app/allergy_list.html', {'allergies': allergies})

def add_allergy(request):
    form = AllergyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('admin_allergy')
    return render(request, 'food_app/add_allergy.html', {'form': form})

def edit_allergy(request, id):
    allergy = get_object_or_404(Allergy, id=id)
    form = AllergyForm(request.POST or None, instance=allergy)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('admin_allergy')
    return render(request, 'food_app/add_allergy.html', {'form': form, 'edit': True})

def delete_allergy(request, id):
    allergy = get_object_or_404(Allergy, id=id)
    allergy.delete()
    return redirect('admin_allergy')

# -------------------- Orders --------------------


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'food_app/order_success.html', {'order': order})

def order_list(request):
    orders = Order.objects.select_related('food', 'user').all()
    return render(request, 'food_app/order_list.html', {'orders': orders})

def update_order_status(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == "POST":
        order.status = request.POST.get('status')
        order.save()
        return redirect('admin_orders')
    return render(request, 'food_app/update_order.html', {'order': order})

def update_order(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Order updated successfully!")
            return redirect('admin_order')
    else:
        form = OrderStatusForm(instance=order)
    return render(request, 'food_app/update_order.html', {'form': form, 'order': order})


# Nutrition & Calories - (Could be part of Food model and forms)
from .models import Nutrition
from .forms import NutritionForm

def nutrition_list(request):
    nutritions = Nutrition.objects.select_related('food').all()
    return render(request, 'food_app/nutrition_list.html', {'nutritions': nutritions})

def add_nutrition(request):
    if request.method == 'POST':
        form = NutritionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_nutrition')
    else:
        form = NutritionForm()
    return render(request, 'food_app/add_nutrition.html', {'form': form})

def edit_nutrition(request, pk):
    nutrition = get_object_or_404(Nutrition, pk=pk)
    if request.method == 'POST':
        form = NutritionForm(request.POST, instance=nutrition)
        if form.is_valid():
            form.save()
            return redirect('admin_nutrition')
    else:
        form = NutritionForm(instance=nutrition)
    return render(request, 'food_app/edit_nutrition.html', {'form': form, 'nutrition': nutrition})

def delete_nutrition(request, pk):
    nutrition = get_object_or_404(Nutrition, pk=pk)
    if request.method == 'POST':
        nutrition.delete()
        return redirect('admin_nutrition')
    return render(request, 'food_app/delete_nutrition.html', {'nutrition': nutrition})



# views.py (continued)
@csrf_exempt  # payment gateway POSTs or client posts — we will use POST from client, so csrf_exempt is acceptable; secure with server-side verification.
def payment_success(request, order_id):
    """
    Verify Razorpay signature and mark order as CONFIRMED (or DELIVERED depending on flow).
    This view expects POST from client with: razorpay_payment_id, razorpay_order_id, razorpay_signature
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")

    payment_id = request.POST.get('razorpay_payment_id')
    razorpay_order_id = request.POST.get('razorpay_order_id')
    signature = request.POST.get('razorpay_signature')

    order = get_object_or_404(Order, id=order_id)

    # Verify signature
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }
    try:
        client.utility.verify_payment_signature(params_dict)
    except razorpay.errors.SignatureVerificationError:
        # Verification failed
        order.status = 'CANCELLED'
        order.save()
        return JsonResponse({'status': 'error', 'message': 'Signature verification failed'}, status=400)

    # success: save payment ids and update status
    order.razorpay_payment_id = payment_id
    order.razorpay_signature = signature
    order.status = 'CONFIRMED'  # or use 'PAID' if you have that
    order.delivered_at = None
    order.save()

    # You may redirect to a success page or return json
    # Here return a JSON response; client JS can redirect.
    return JsonResponse({'status': 'success', 'message': 'Payment successful', 'order_id': order.id})



def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        "order": order,
        "message": "Your payment was successful 🎉",
    }
    return render(request, "food_app/order_success.html", context)


def order_failure(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        "order": order,
        "message": "Payment failed ❌ Please try again.",
    }
    return render(request, "food_app/order_failure.html", context)


def user_login(request):
    if request.user.is_authenticated:
        return redirect('food_list')  # redirect logged-in users

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('food_list')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'food_app/login.html')


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

from .forms import UserRegistrationForm

def user_register(request):
    if request.user.is_authenticated:
        return redirect('food_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Registration successful! You can now login.")
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'food_app/register.html', {'form': form})


def analytics_dashboard(request):
    # ---------- Top Metrics ----------
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_price'))['total'] or 0
    total_foods = Food.objects.count()
    pending_orders = Order.objects.filter(status='PENDING').count()

    # ---------- Popular Foods ----------
    popular_foods = (
        Food.objects.annotate(
            order_count=Count('order'),
            revenue=Sum('order__total_price')
        )
        .order_by('-order_count')[:10]
    )

    # ---------- Stock Levels ----------
    stocks = Stock.objects.select_related('food').all().order_by('food__food_name')

    # ---------- Orders & Revenue per Day for last 30 days ----------
    today = now().date()
    start_date = today - timedelta(days=29)

    # Orders per day
    orders_per_day_qs = (
        Order.objects.filter(ordered_at__date__gte=start_date)
        .extra({'day': "date(ordered_at)"})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    orders_dates = [o['day'] for o in orders_per_day_qs]  # no strftime
    orders_count = [o['count'] for o in orders_per_day_qs]

    # Revenue per day
    revenue_per_day_qs = (
        Order.objects.filter(ordered_at__date__gte=start_date)
        .extra({'day': "date(ordered_at)"})
        .values('day')
        .annotate(revenue=Sum('total_price'))
        .order_by('day')
    )
    revenue_dates = [r['day'] for r in revenue_per_day_qs]  # keep as string
    revenue_amounts = [float(r['revenue'] or 0) for r in revenue_per_day_qs]


    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_foods': total_foods,
        'pending_orders': pending_orders,
        'popular_foods': popular_foods,
        'stocks': stocks,
        'orders_dates': orders_dates,
        'orders_count': orders_count,
        'revenue_dates': revenue_dates,
        'revenue_amounts': revenue_amounts,
    }

    return render(request, 'food_app/analytics.html', context)



# Cart & Wishlist - (Could be implemented with sessions or models)

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Food, CartItem

@login_required
def add_to_cart(request, food_id):
    food = get_object_or_404(Food, id=food_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, food=food)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_view')

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        item.total_price = item.food.price * item.quantity
    cart_total = sum([item.total_price for item in cart_items])
    razorpay_amount = int(cart_total * 100)  # Razorpay expects amount in paise
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'razorpay_amount': razorpay_amount,
    }
    total = sum(item.total_price for item in cart_items)
    return render(request, 'food_app/cart.html', context)

@login_required
def update_cart_item(request, item_id, action):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if action == 'increase':
        item.quantity += 1
        item.save()
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    elif action == 'remove':
        item.delete()
    return redirect('cart_view')

# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Cart, Order, Food
from django.conf import settings
import razorpay
from django.utils import timezone




@login_required
def checkout_cart(request):
    """
    Show checkout page for current user's cart.
    Creates a Razorpay Order server-side and passes the id + amount to the template.
    """
    user = request.user
    # get cart items for logged-in user (use session_key fallback if you implemented anonymous carts)
    cart_items = CartItem.objects.filter(user=user).select_related('food')

    # If cart is empty, show empty cart template
    if not cart_items.exists():
        return render(request, 'food_app/empty_cart.html')

    # Calculate total (Decimal for currency safety)
    total_amount = sum((item.food.price * item.quantity) for item in cart_items)
    # Ensure Decimal -> float handling if price is DecimalField
    total_amount = Decimal(total_amount)

    # Razorpay wants amount in paise (integer)
    razorpay_amount = int(total_amount * 100)

    # Create a Razorpay order (recommended - you can also skip and allow client to create)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        razorpay_order = client.order.create({
            "amount": razorpay_amount,
            "currency": "INR",
            "payment_capture": 1,  # auto-capture
            "receipt": f"cart_rcpt_{user.id}_{int(timezone.now().timestamp())}"
        })
    except Exception as e:
        # log and show friendly message
        # logger.exception("Razorpay order creation failed")
        messages.error(request, "Payment provider is currently unavailable. Please try again later.")
        return render(request, 'food_app/cart.html', {'cart_items': cart_items, 'total_amount': total_amount})

    # Pass everything the template needs
    context = {
        'cart_items': cart_items,
        'cart_total': total_amount,
        'razorpay_amount': razorpay_amount,
        'razorpay_order_id': razorpay_order.get('id'),
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }

    return render(request, 'food_app/checkout_cart.html', context)



# Add item to cart
@login_required
def add_to_cart(request, food_id):
    food = get_object_or_404(Food, id=food_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, food=food)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_view')


# Remove item from cart
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('cart_view')


# Update cart quantity
@login_required
def update_cart_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if request.method == "POST":
        if 'increase' in request.POST:
            item.quantity += 1
        elif 'decrease' in request.POST and item.quantity > 1:
            item.quantity -= 1
        else:
            item.quantity = int(request.POST.get('quantity', item.quantity))
        item.save()
    return redirect('cart_view')


# Cart view
@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum([item.total_price for item in cart_items])
    return render(request, 'food_app/cart.html', {'cart_items': cart_items, 'cart_total': cart_total})



# Razorpay success
@login_required
def checkout_success(request):
    orders = Order.objects.select_related('food', 'user').all()
    payment_id = request.POST.get('payment_id')
    # Create orders for each cart item
    print(payment_id)
    
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        Order.objects.create(
            user=request.user,
            food=item.food,
            quantity=item.quantity
        )
    # Clear cart
    con = {'orders': orders}
    cart_items.delete()
    return render(request, 'food_app/checkout_success.html', con)


# Razorpay failure
@login_required
def checkout_failure(request):
    return render(request, 'food_app/checkout_failure.html')

@csrf_exempt  # if this will be called directly by client JS fetch; see note below
@login_required
def cart_payment_success(request):
    """
    Verify Razorpay signature sent from client after checkout success.
    Expects POST with: razorpay_payment_id, razorpay_order_id, razorpay_signature
    On success: create Orders (or update existing temporary order records), clear cart, and respond.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid method")

    payment_id = request.POST.get('razorpay_payment_id')
    razorpay_order_id = request.POST.get('razorpay_order_id')
    signature = request.POST.get('razorpay_signature')

    if not (payment_id and razorpay_order_id and signature):
        return HttpResponseBadRequest("Missing payment information")

    # Verify signature using razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    params = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }
    try:
        client.utility.verify_payment_signature(params)
    except razorpay.errors.SignatureVerificationError as e:
        # logger.exception("Razorpay signature verification failed")
        return JsonResponse({'status': 'error', 'message': 'Signature verification failed'}, status=400)

    # Signature verified -> create Orders from cart items
    user = request.user
    cart_items = CartItem.objects.filter(user=user).select_related('food')
    
    orders = []
    with transaction.atomic():
        for item in cart_items:
            order_ref = _generate_order_ref()
            order = Order.objects.create(
                user=user,
                food=item.food,
                quantity=item.quantity,
                total_price=item.food.price * item.quantity,
                status='CONFIRMED',
                razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=payment_id,
                razorpay_signature=signature,
                order_ref=order_ref,
            )
            orders.append(order)
        # clear cart after creating orders
        cart_items.delete()

    # Save payment ids to orders OR a single payment record (optional)
    # If you want to attach Razorpay ids to each order:
    for o in orders:
        o.razorpay_order_id = razorpay_order_id
        o.razorpay_payment_id = payment_id
        o.razorpay_signature = signature
        o.save(update_fields=['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'])

    # Return JSON success; client JS can redirect to a success page
    return JsonResponse({'status': 'success', 'message': 'Payment verified', 'payment_id': payment_id, 'orders': [o.id for o in orders]})



@login_required
def cart_success(request):
    payment_id = request.GET.get('payment_id')
    if not payment_id:
        # fallback: show last few orders for user if payment_id missing
        orders = Order.objects.filter(user=request.user).order_by('-ordered_at')[:10]
        msg = "Here are your recent orders."
    else:
        orders = Order.objects.filter(user=request.user, razorpay_payment_id=payment_id).order_by('-ordered_at')
        msg = f"Payment ID: {payment_id}"

    return render(request, 'food_app/cart_success.html', {
        'payment_id': payment_id,
        'orders': orders,
        'message': msg
    })


def orders_list_user(request):
    if not request.user.is_authenticated:
        return redirect('login')
    # orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    orders = Order.objects.select_related('food', 'user').all()
    return render(request, 'food_app/user_orders.html', {'orders': orders})