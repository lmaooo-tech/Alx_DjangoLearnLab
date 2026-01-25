from django import forms


class BookSearchForm(forms.Form):
    """Simple form to validate book title searches safely."""
    query = forms.CharField(max_length=200, required=False, strip=True)
