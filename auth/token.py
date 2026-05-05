class TokenValidator:
    def validate(self, user):
        if user is None:
            return None
        return user.id
    def validate(self, user):
        # Additional validation logic here...
        if user is None:
            raise ValueError("User object is None")
        if not hasattr(user, 'id'):
            raise AttributeError("User object has no 'id' attribute")
        return user.id
