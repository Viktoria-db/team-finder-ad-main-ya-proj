import re

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

PHONE_PATTERN = re.compile(r"^(?:8\d{10}|\+7\d{10})$")


def normalize_phone(value):
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits.startswith("8"):
        return f"+7{digits[1:]}"
    if len(digits) == 11 and digits.startswith("7"):
        return f"+{digits}"
    if len(digits) == 10:
        return f"+7{digits}"
    return value


def validate_phone(value):
    if not PHONE_PATTERN.match(value.replace(" ", "")):
        raise ValidationError("Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX.")


def validate_github_url(value):
    if not value:
        return
    validator = URLValidator()
    validator(value)
    if "github.com" not in value.lower():
        raise ValidationError("Ссылка должна вести на GitHub.")
