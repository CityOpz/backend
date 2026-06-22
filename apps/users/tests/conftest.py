from django.utils.crypto import get_random_string


def make_test_password():
    return f"Test-{get_random_string(16)}"
