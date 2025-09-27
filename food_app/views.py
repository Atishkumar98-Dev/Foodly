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