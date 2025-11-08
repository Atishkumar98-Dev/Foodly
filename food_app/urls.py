from django.urls import path
from . import views

urlpatterns = [
    path('', views.food_list, name='food_list'),
    path('food/<int:food_id>/', views.food_detail, name='food_detail'),
    path('menu/', views.menu_list, name='menu_list'),
    path('order/<int:food_id>/', views.place_order, name='place_order'),
    path('order/<int:order_id>/payment-success/', views.payment_success, name='payment_success'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('meal-plan/', views.meal_plan, name='meal_plan'),
    path('admin/orders/<int:food_id>/', views.admin_orders, name='admin_order'),
    path('admin/stock/', views.admin_stock, name='admin_stock'),
    path('admin/menu/', views.admin_menu, name='admin_menu'),
    path('admin/meal-plan/', views.admin_meal_plan, name='admin_meal_plan'),
    path('admin/food/', views.admin_food, name='admin_food'),       # List all foods
    path('admin/food/add/', views.add_food, name='add_food'),       # Add new food
    path('admin/food/edit/<int:food_id>/', views.edit_food, name='edit_food'),   # Edit food
    path('admin/food/delete/<int:food_id>/', views.delete_food, name='delete_food'),  # Delete food
    # Ingredient Management
    path('ingredients/', views.ingredient_list, name='admin_ingredient'),
    path('ingredients/add/', views.add_ingredient, name='add_ingredient'),
    path('ingredients/edit/<int:id>/', views.edit_ingredient, name='edit_ingredient'),
    path('ingredients/delete/<int:id>/', views.delete_ingredient, name='delete_ingredient'),
    

    # Orders
    path('orders/', views.order_list, name='admin_orders'),
    path('orders/<int:id>/update/', views.update_order_status, name='update_order_status'),

    # Restaurants & Chefs
    path('restaurants/', views.restaurant_list, name='admin_restaurant'),
    path('chefs/', views.chef_list, name='admin_chef'),

    # Meal Plans
    path('mealplans/', views.mealplan_list, name='admin_mealplan'),

    # Discounts & Stock
    path('discounts/', views.discount_list, name='admin_discount'),
    path('stock/', views.stock_list, name='admin_stock'),

    # Allergies & Tags
    path('allergies/', views.allergy_list, name='admin_allergy'),

    
    # ---------- Tags ----------
    path('admin/tag/', views.tag_list, name='admin_tag'),
    path('admin/tag/add/', views.add_tag, name='add_tag'),
    path('admin/tag/edit/<int:pk>/', views.edit_tag, name='edit_tag'),
    path('admin/tag/delete/<int:pk>/', views.delete_tag, name='delete_tag'),

    # ---------- Discounts ----------
    path('admin/discount/', views.discount_list, name='admin_discount'),
    path('admin/discount/add/', views.add_discount, name='add_discount'),
    path('admin/discount/edit/<int:pk>/', views.edit_discount, name='edit_discount'),
    path('admin/discount/delete/<int:pk>/', views.delete_discount, name='delete_discount'),

    # ---------- Stock ----------
    path('admin/stock/', views.stock_list, name='admin_stock'),
    path('admin/stock/add/', views.add_stock, name='add_stock'),
    path('admin/stock/edit/<int:pk>/', views.edit_stock, name='edit_stock'),
    path('admin/stock/delete/<int:pk>/', views.delete_stock, name='delete_stock'),

    # ---------- Allergies ----------
    path('admin/allergy/', views.allergy_list, name='admin_allergy'),
    path('admin/allergy/add/', views.add_allergy, name='add_allergy'),
    path('admin/allergy/edit/<int:pk>/', views.edit_allergy, name='edit_allergy'),
    path('admin/allergy/delete/<int:pk>/', views.delete_allergy, name='delete_allergy'),

    # ---------- Orders ----------
    path('admin/order/', views.order_list, name='admin_order'),
    path('admin/order/edit/<int:id>/', views.update_order, name='edit_order'),
    path('admin/order/delete/<int:pk>/', views.delete_order, name='delete_order'),
    # ---------- Nutrition Information ----------
    path('admin/nutrition/', views.nutrition_list, name='admin_nutrition'),
    path('admin/nutrition/add/', views.add_nutrition, name='add_nutrition'),
    path('admin/nutrition/<int:pk>/edit/', views.edit_nutrition, name='edit_nutrition'),
    path('admin/nutrition/<int:pk>/delete/', views.delete_nutrition, name='delete_nutrition'),

    # Payment Success & Failure
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('order-failure/<int:order_id>/', views.order_failure, name='order_failure'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('admin/analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/<str:action>/', views.update_cart_item, name='update_cart_item'),
    path('cart/checkout/', views.checkout_cart, name='checkout_cart'),
    path('cart/add/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout-success/', views.checkout_success, name='checkout_success'),
    path('checkout-failure/', views.checkout_failure, name='checkout_failure'),
    path('cart/success/', views.cart_payment_success, name='cart_payment_success'),
    path('cart/failure/', views.checkout_failure, name='cart_payment_failure'),
    path('cart/success/full/', views.cart_success, name='cart_success'),
    path('user/order/lists/', views.cart_success, name='order_list'),
    path('user/order/order_lists_complete/', views.orders_list_user, name='order_lists_complete'),

]
