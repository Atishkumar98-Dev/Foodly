from django import forms
from .models import Food, Ingredient, Tag
from .models import Food, Ingredient, Tag, Discount, Stock, Allergy


class FoodForm(forms.ModelForm):
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Food
        fields = [
            'food_name', 'category', 'sub_category', 'types',
            'calories', 'price', 'available', 'image', 'description'
        ]
        widgets = {
            'food_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'sub_category': forms.TextInput(attrs={'class': 'form-control'}),
            'types': forms.TextInput(attrs={'class': 'form-control'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
            'ingredients': forms.CheckboxSelectMultiple(),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['ingredients'].initial = self.instance.ingredients.all()
            self.fields['tags'].initial = self.instance.tags.all()

    def save(self, commit=True):
        food = super().save(commit=commit)
        if commit:
            food.ingredients.set(self.cleaned_data['ingredients'])
            food.tags.set(self.cleaned_data['tags'])
        return food

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = '__all__'

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'

class DiscountForm(forms.ModelForm):
    valid_from = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )
    valid_to = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Discount
        fields = ['code', 'percentage', 'active', 'valid_from', 'valid_to', 'foods', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. SPRING20'}),
            'percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'foods': forms.CheckboxSelectMultiple(),  # you can style via CSS
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = '__all__'

class AllergyForm(forms.ModelForm):
    class Meta:
        model = Allergy
        fields = '__all__'


from django import forms
from .models import Order

# class OrderStatusForm(forms.ModelForm):
#     class Meta:
#         model = Order
#         fields = ['food', 'quantity', 'status', 'delivered_at']
#         widgets = {
#             'food': forms.Select(attrs={'class': 'form-select'}),
#             'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
#             'status': forms.Select(attrs={'class': 'form-select'}),
#             'delivered_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
#         }

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['food', 'quantity', 'status', 'delivered_at']
        widgets = {
            'food': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'delivered_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
from django import forms
from .models import Nutrition

class NutritionForm(forms.ModelForm):
    class Meta:
        model = Nutrition
        fields = ['food', 'protein', 'carbs', 'fats', 'fiber', 'sugar']
        widgets = {
            'food': forms.Select(attrs={'class': 'form-select'}),
            'protein': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'carbs': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'fats': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'fiber': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'sugar': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }


from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'first_name': forms.TextInput(attrs={'class':'form-control'}),
            'last_name': forms.TextInput(attrs={'class':'form-control'}),
        }

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            raise ValidationError("Passwords do not match")
        return password2