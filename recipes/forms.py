from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recipe

class RecipeForm(forms.ModelForm):
    title = forms.CharField(
        label="Title",
        widget=forms.TextInput(attrs={"class": "form-item"}),
    )

    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(attrs={"class": "form-item"}),
    )

    cooking_time = forms.IntegerField(
        label="Cooking Time(min)",
        widget=forms.NumberInput(attrs={"class": "form-item"}),
    )

    recipe_ingredients = forms.CharField(
        max_length=600,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-item", "placeholder": "e.g. ingredient1, ingredient2"}),
    )

    instructions = forms.CharField(
        label="Instructions",
        widget=forms.Textarea(attrs={"class": "form-item"}),
    )

    pic = forms.ImageField(
        label="Picture",
        widget=forms.FileInput(attrs={"class": "form-item"}),
    )

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
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
    first_name = forms.CharField(label="", max_length=50, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
    last_name = forms.CharField(label="", max_length=50, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))
    username = forms.CharField(label="", max_length=50,  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}), help_text='' )
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', )
