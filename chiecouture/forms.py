from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product, Review, Store


class UserRegisterForm(UserCreationForm):
    """Form for user registration with role selection."""
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = User
        fields = ["username", "email", "role", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "password1": forms.PasswordInput(attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control"}),
        }


class StoreForm(forms.ModelForm):
    """Form for creating or editing a store."""
    class Meta:
        model = Store
        fields = ["name", "description", "logo"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class ProductForm(forms.ModelForm):
    """Form for adding/editing products in a store."""
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "image"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class ReviewForm(forms.ModelForm):
    """Form for submitting product reviews."""
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "max": 5}
            ),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_rating(self):
        """Ensure rating is between 1 and 5."""
        rating = self.cleaned_data.get("rating")
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating
