from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm
from django import forms
from .models import Profile, Product, Store, ShippingAddress, ProductReviews
from django.core.exceptions import ValidationError

class ChangePassword(SetPasswordForm):
	'''form for changing password'''
	class Meta():
		model = User
		fields = ['new_password1', 'new_password2']

	def __init__(self, *args, **kwargs):
		super(ChangePassword, self).__init__(*args, **kwargs)
		
		self.fields['new_password1'].widget.attrs['class'] = 'form-control'
		self.fields['new_password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['new_password1'].label = ''
		self.fields['new_password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['new_password2'].widget.attrs['class'] = 'form-control'
		self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['new_password2'].label = ''
		self.fields['new_password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


class UpdateUserForm(UserChangeForm):
	'''form for updating user info'''
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}), required=False)
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}), required=False)
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}), required=False)
	password = None

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email')

	def __init__(self, *args, **kwargs):
		super(UpdateUserForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

	def clean_email(self):
		email = self.cleaned_data['email']
		if User.objects.filter(email=email).exists():
			raise ValidationError("This email is already registered.")
			
	

class SignUpForm(UserCreationForm):
	'''form for user registration'''
	role = [
		('vendor', 'vendor'),
		('buyer', 'buyer')
	]
	
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))
	role = forms.ChoiceField(choices=role, required=True, label='Select your role', initial='buyer', widget=forms.Select(attrs={'class': 'form-control'}))

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role')
	

	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'

	def check_email(self):
		email = self.cleaned_data.get('email')
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError("Email already exists")
		return email




class UserInfoForm(forms.ModelForm):
	'''form for user profile information'''
	USER_TYPES = [
		('vendor', 'vendor'),
		('buyer', 'buyer'),
	]

	phone = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'phone'}), required=False)
	full_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'full name'}), required=True)
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'}), required=True)
	address1 = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'address1'}), required=True)
	address2 = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'address2'}), required=False)
	city = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'city'}), required=True)
	country = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'country'}), required=True)
	post_code = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'post code'}), required=True)

	class Meta:
		model = Profile
		fields = ['phone', 'full_name', 'email', 'address1', 'address2', 'city', 'country', 'post_code']


class ProductForm(forms.ModelForm):
	'''form for adding or editing products'''
	name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'name'}), required=False)
	price = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'price'}), required=False)
	stock = forms.IntegerField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'stock'}), required=False)
	image = forms.ImageField(label="", widget=forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'image'}), required=False)
	store = forms.ModelChoiceField(queryset=None, label="", widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'store'}), required=False)


	class Meta:
		model = Product
		fields = ['name', 'price', 'stock', 'image', 'store']

	def __init__(self, *args, **kwargs):
		super(ProductForm, self).__init__(*args, **kwargs)
		self.fields['store'].queryset = Store.objects.all()

class StoreForm(forms.ModelForm):
	'''form for adding stores'''
	name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'name'}), required=True)
	description = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'description'}), required=False)
	image = forms.ImageField(label="", widget=forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'image'}), required=False)

	class Meta:
		model = Store
		fields = ['name', 'description', 'image']

class ShippingForm(forms.ModelForm):
	full_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'full name'}), required=True)
	email = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'}), required=True)
	address1 = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'address1'}), required=True)
	address2 = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'address2'}), required=False)
	city = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'city'}), required=True)
	country = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'country'}), required=True)
	post_code = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'post code'}), required=True)

	class Meta:
		model = ShippingAddress
		fields = ['full_name', 'email', 'address1', 'address2', 'city', 'country', 'post_code']

		exclude = ['user',]

class ReviewForm(forms.ModelForm):
	review = forms.CharField(label="", widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'review'}))

	class Meta:
		model = ProductReviews
		fields = ['review', 'rating']