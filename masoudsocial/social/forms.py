from django import forms
from .models import User,Post,Comment
from django.contrib.auth.forms import AuthenticationForm 


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=250, required=True, label="نام کاربری یا تلفن",
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=250, required=True, label="رمز عبور",
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))



class UserRegistrationForm(forms.ModelForm):
    password=forms.CharField(max_length=20, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='پسورد')
    password2=forms.CharField(max_length=20, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='تکرار پسورد')

    class Meta:
        model= User
        fields=['username','first_name','last_name','phone','email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
                'phone': forms.TextInput(attrs={
                    'class': 'form-control',
            }),
                'email': forms.TextInput(attrs={
                    'class': 'form-control',
            }),
        }
        labels = {
            'username': 'نام کاربری',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'phone': 'شماره تماس',
            'email': 'ایمیل',

        }
    
    def clean_password2(self):
        cd=self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('پسورد ها با هم مطابقت ندارند')
        return cd['password2']
    
    def clean_phone(self):
        phone=self.cleaned_data['phone']
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('این شماره قبلا ثبت شده است!')
        return phone
    
    def clean_email(self):
        email=self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('این ایمیل قبلا ثبت شده است!')
        return email


class UserEditForm(forms.ModelForm):
    class Meta:
        model= User
        fields=['username','first_name','last_name','phone','email','date_of_birth','bio','job','photo','insta_id','twitter_id','facebook_id']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
            }),
            'bio': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
            }),
            'job': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'facebook_id': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'twitter_id': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'insta_id': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'username': 'نام کاربری',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'ایمیل',
            'date_of_birth': 'تاریخ تولد',
            'phone': 'شماره تماس',
            'bio': 'بایو',
            'job': 'شغل',
            'facebook_id': 'آی دی فیسبوک',
            'twitter_id': 'آی دی توییتر',
            'insta_id': 'آی دی اینستاگرام',

        }
    def clean_phone(self):
        phone=self.cleaned_data['phone']
        if User.objects.exclude(id=self.instance.id).filter(phone=phone).exists():
            raise forms.ValidationError('این شماره قبلا ثبت شده است!')
        return phone

    def clean_username(self):
        username=self.cleaned_data['username']
        if User.objects.exclude(id=self.instance.id).filter(username=username).exists():
            raise forms.ValidationError('این یوزرنیم قبلا ثبت شده است!')
        return username
    
    def clean_email(self):
        email=self.cleaned_data['email']
        if User.objects.exclude(id=self.instance.id).filter(email=email).exists():
            raise forms.ValidationError('این ایمیل قبلا ثبت شده است!')
        return email
    

class TicketForm(forms.Form):
    SUBJECT_CHOICES=(
        ('پیشنهاد','پیشنهاد'),
        ('انتقاد','انتقاد'),
        ('گزارش','گزارش'),
    )
    message=forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': "3"}), required=True) 
    subject=forms.ChoiceField(choices=SUBJECT_CHOICES,label='موضوع')    
    # name=forms.CharField(max_length=250,widget=forms.TextInput(attrs={'class': 'form-control'}), required=True, label='نام')
    # email=forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}),label='ایمیل')
    # phone=forms.CharField(max_length=11,widget=forms.TextInput(attrs={'class': 'form-control'}), required=True, label='شماره تماس')


    # def clean_phone(self):
    #     phone=self.cleaned_data['phone']
    #     if phone:
    #         if not phone.isnumeric():
    #             raise forms.ValidationError('شماره تلفن عددی نیست!')
    #         else:
    #           return phone
            


class CreatePostForm(forms.ModelForm):
    image1=forms.ImageField(label='تصویر اول',required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    image2=forms.ImageField(label='تصویر دوم',required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    class Meta:
        model= Post
        fields=['description','tags']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': "3"
            }),
        }
        labels = {
            'tags': 'تگ ها',
        }



class SearchForm(forms.Form):
    query=forms.CharField()


class CommentForm(forms.ModelForm):
    class Meta:
        model= Comment
        fields=['body']
        widgets={
            'body': forms.TextInput(attrs={
                'placeholder': 'کامنت بزارید...',
                'class':'form-control input-sm'
            }),}