
import re
from rest_framework import serializers

def validate_password(password, username):
    if not password:
        raise serializers.ValidationError("Password cannot be empty.")
    
    if not re.search(r"[A-Z]", password):
        raise serializers.ValidationError("Password must contain at least one uppercase letter.")

    if not re.search(r"[a-z]", password):
        raise serializers.ValidationError("Password must contain at least one lowercase letter.")

    if not re.search(r"[0-9]", password):
        raise serializers.ValidationError("Password must contain at least one digit.")


    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise serializers.ValidationError("Password must contain at least one special character.")

    if re.search(r"\s", password):
        raise serializers.ValidationError("Password must not contain any spaces.")

    if password == username:
        raise serializers.ValidationError("Password must not be the same as the username.")
