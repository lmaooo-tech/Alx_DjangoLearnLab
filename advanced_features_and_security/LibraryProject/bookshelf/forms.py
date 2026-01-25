from django import forms


class BookSearchForm(forms.Form):
    """Simple form to validate book title searches safely."""
    query = forms.CharField(max_length=200, required=False, strip=True)


class ExampleForm(forms.Form):
    """Example form demonstrating CSRF-protected input handling."""
    sample = forms.CharField(max_length=100, required=True, strip=True)
