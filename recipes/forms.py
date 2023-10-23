from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recipe, Ingredient

class RecipeForm(forms.ModelForm):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={"class": "form-item"}),)
    description = forms.CharField(max_length=100, label="Description", widget=forms.Textarea(attrs={"class": "form-item"}),)
    cooking_time = forms.IntegerField(label="Cooking Time(min)", widget=forms.NumberInput(attrs={"class": "form-item"}),)
    recipe_ingredients = forms.CharField( max_length=600, required=False, widget=forms.TextInput(attrs={"class": "form-item", "placeholder": "e.g. ingredient1, ingredient2"}),)
    instructions = forms.CharField(label="Instructions", widget=forms.Textarea(attrs={"class": "form-item"}),)
    pic = forms.ImageField( label="Picture", widget=forms.FileInput(attrs={"class": "form-item"}), )

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'cooking_time', 'instructions', 'pic']
        
class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
    first_name = forms.CharField(label="", max_length=90, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
    last_name = forms.CharField(label="", max_length=90, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = ''

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = ''

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = ''

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="E-mail", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
    first_name = forms.CharField(label="First name", max_length=50, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
    last_name = forms.CharField(label="Last name", max_length=50, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))
    username = forms.CharField(label="Username", max_length=50,  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}), required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', )
    
    def clean(self):
        cleaned_data = super(UserUpdateForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("The new password and confirm password do not match.")
        
        return cleaned_data


CHART_CHOICES = (
    ("#1", "Bar Chart"),
    ("#2", "Pie Chart"),
    ("#3", "Line Chart"),
)

class RecipeSearchForm(forms.Form):
    Recipe_Name = forms.CharField(required=False, max_length=50, label="Recipe Name", widget=forms.TextInput(attrs={"class": "form-item", "placeholder": "Search by Recipe Name"}))
    Ingredients = forms.CharField(required=False, label="Ingredient", widget=forms.TextInput(attrs={"class": "form-item", "placeholder": "Search by ingredient"}))
    chart_type = forms.ChoiceField(choices=CHART_CHOICES, required=False, widget=forms.Select(attrs={"class": "form-item"}))

    def clean(self):
        cleaned_data = super().clean()
        recipe_name = cleaned_data.get("Recipe_Name")
        ingredients = cleaned_data.get("Ingredients")

        if not recipe_name and not ingredients:
            raise forms.ValidationError(
                "Please enter a recipe name or ingredient."
            )
        return cleaned_data
