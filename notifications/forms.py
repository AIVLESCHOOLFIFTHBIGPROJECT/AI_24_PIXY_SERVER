from django import forms

class NotificationForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, label='Notification Message')
