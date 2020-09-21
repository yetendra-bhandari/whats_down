from django import forms
from django.core.exceptions import ValidationError
import html
import hashlib
import markdown
salt = 'my_salt'
email_field = forms.EmailField()


def saltedHash(password):
    '''
    Generates the 'SHA-256' salted-hash of the given password.
    '''
    return hashlib.sha256((salt + password).encode()).hexdigest()


def toMarkdown(text):
    '''
    Generates html-safe markdown from the given text.
    '''
    return markdown.markdown((html.escape(text, quote=False))).replace('"', '&quot;') .replace("'", '&apos;')


def validName(name):
    for char in name:
        if(not(char.isalpha() or char.isspace())):
            return False
    return True


def validEmail(email):
    '''
    Check whether the given email address is valid or not.
    '''
    try:
        email_field.clean(email)
    except(ValidationError):
        return False
    return True
