from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import Review


# class BookReviewForm(forms.Form):
#     name = forms.CharField(label="Your name", max_length=100)
#     stars = forms.FloatField(label="Rating (out of 5)")
#     review_body = forms.CharField(label="Review body")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'
