from typing_extensions import Required
from flatpickr import DatePickerInput
from django_countries.widgets import CountrySelectWidget
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from setuptools import Require
from .models import  Post, Comment, UserProfile
choices=[('Xbox','Xbox'),('PC','PC'),('Playstation','Playstation'),('Mobile','Mobile'),('Nintendo Switch', 'Nintendo Switch')]

class CreatePostForm(forms.ModelForm):
    """
    Form for creating posts (based on Post model)
    fields:
    * content - post's inner text
    """
    
    
    class Meta:
        model = Post
        fields = ["content", "categ"]
        labels = {
            "Description": _("content: "),
            "Category": _("categ: "), }
    
        widgets={ 
                "content": forms.Textarea(attrs={
                            'placeholder': _("What are you thinking about?"),
                             'autofocus': 'autofocus',
                            'rows': '3',
                            'class': 'form-control',
                            'aria-label': _("post content") }),
                "categ": forms.Select(choices=choices , attrs={'class':'form-control'}),
                }                                

class CreatePostForm1(forms.ModelForm):
    """
    Form for creating posts (based on Post model)
    fields:
    * content - post's inner text
    """
    
    
    class Meta:
        model = Post
        fields = ["content"]
        labels = {
            "Description": _("content: "),
             }
    
        widgets={ 
                "content": forms.Textarea(attrs={
                            'placeholder': _("What are you thinking about?"),
                             'autofocus': 'autofocus',
                            'rows': '3',
                            'class': 'form-control',
                            'aria-label': _("post content") }),
                }                                

    

class CreateCommentForm(forms.ModelForm):
    """
    Form for creating comments (based on Comment model)
    fields:
    * content - comment's inner text
    """

    content = forms.CharField(widget=forms.Textarea(attrs={
                                    'placeholder': _("Write a comment..."),
                                    'rows': '1',
                                    'class': 'form-control',
                                    'aria-label': _("comment content")
                             }))

    class Meta:
        model = Comment
        fields = ["content"]

class CreateUserProfileForm(forms.ModelForm):
    """
    Form for editing user profile (based on UserProfile model)
    fields:
    * name - user's name
    * date_of_birth - user's birth date
    * about - additional info about the user
    * country - user's birth place
    * image - user's profile photo
    """
    
    
    def clean_image(self):
        """ Check if image doesn't exceed max file size """
        image = self.cleaned_data.get('image')

        if "default.png" not in image:
            if image.size > settings.MAX_UPLOAD_SIZE * 1024 * 1024:
                raise ValidationError(_(f"Image file exceeds {settings.MAX_UPLOAD_SIZE} MB size limit"))
        return image

    class Meta:
        model = UserProfile
        fields = ["name", "date_of_birth", "about", "country", "image"]
        labels = {
            "name": _("Discord Id: "),
            "about": _("About: "),
            "country": _("Country: "),
            "date_of_birth":_("Date of birth"), 
            "image": _("Image: ")
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": _("Your name..."),
                "aria-label": _("your name"),
                "class": "form-control"
                }),
            "about": forms.Textarea(attrs={
                "placeholder": _("Tell about yourself..."),
                "aria-label": _("tell about yourself"),
                "class": "form-control"
                }),
            'country': CountrySelectWidget(
                 attrs={"class": "form-control"}
            ),
            'date_of_birth': DatePickerInput(),
        }