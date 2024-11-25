from django.core.exceptions import ValidationError
from datetime import datetime

def validate_date(date):
    now = datetime.now()
    if now.date() > date:
        raise ValidationError(f'you must enter a date in the present')