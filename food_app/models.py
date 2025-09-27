from django.db import models
from django.contrib.auth.models import User

# ---------- Food App Models ----------

# Food Model
class Food(models.Model):
    FOOD_CATEGORIES = [
        ('VEG', 'Vegetarian'),
        ('NONVEG', 'Non-Vegetarian'),
        ('VEGAN', 'Vegan'),
        ('BEV', 'Beverage'),
        ('DESSERT', 'Dessert'),
    ]
    
    food_name = models.CharField(max_length=50)
    category = models.CharField(max_length=20, choices=FOOD_CATEGORIES)
    sub_category = models.CharField(max_length=50, blank=True)
    types = models.CharField(max_length=50, blank=True)  # e.g., Organic, Homemade
    calories = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='food_images/', null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.food_name} ({self.category})"


# Ingredients Model
class Ingredient(models.Model):
    name = models.CharField(max_length=50)
    foods = models.ManyToManyField(Food, related_name='ingredients')
    is_allergen = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# Nutrition Facts Model
class Nutrition(models.Model):
    food = models.OneToOneField(Food, on_delete=models.CASCADE, related_name='nutrition')
    protein = models.FloatField(null=True, blank=True)
    carbs = models.FloatField(null=True, blank=True)
    fats = models.FloatField(null=True, blank=True)
    fiber = models.FloatField(null=True, blank=True)
    sugar = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Nutrition - {self.food.food_name}"



# Tags for Food (Vegan, Gluten-Free, Spicy)
class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)
    foods = models.ManyToManyField(Food, related_name='tags', blank=True)

    def __str__(self):
        return self.name


# Recipe Model
class Recipe(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='recipes')
    instructions = models.TextField()
    prep_time = models.PositiveIntegerField(help_text="Preparation time in minutes")
    cook_time = models.PositiveIntegerField(help_text="Cooking time in minutes")
    servings = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Recipe for {self.food.food_name}"


# Reviews / Ratings
class Review(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.food.food_name}"


# ---------- Restaurant & Chef ----------

class Restaurant(models.Model):
    name = models.CharField(max_length=50)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name


class Chef(models.Model):
    name = models.CharField(max_length=50)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='chefs')
    experience_years = models.PositiveIntegerField()
    specialty = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"


# ---------- Menu & Meal Plans ----------

class Menu(models.Model):
    name = models.CharField(max_length=50)
    foods = models.ManyToManyField(Food, related_name='menus')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.date}"


class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    foods = models.ManyToManyField(Food, related_name='meal_plans')
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Meal Plan for {self.user.username} ({self.start_date} to {self.end_date})"


# ---------- Orders & Payments ----------

class Order(models.Model):
    ORDER_STATUS = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PREPARING', 'Preparing'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PENDING')
    ordered_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Automatically calculate total price
        self.total_price = self.food.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order by {self.user.username} - {self.food.food_name}"


# Discount / Coupons
class Discount(models.Model):
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    percentage = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    valid_from = models.DateField()
    valid_to = models.DateField()
    foods = models.ManyToManyField(Food, related_name='discounts', blank=True)

    def __str__(self):
        return f"{self.code} ({self.percentage}% Off)"


# Stock / Inventory Management
class Stock(models.Model):
    food = models.OneToOneField(Food, on_delete=models.CASCADE, related_name='stock')
    quantity = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.food.food_name} - {self.quantity} units"


# Food Allergies
class Allergy(models.Model):
    name = models.CharField(max_length=50)
    ingredients = models.ManyToManyField(Ingredient, related_name='allergies', blank=True)

    def __str__(self):
        return self.name
