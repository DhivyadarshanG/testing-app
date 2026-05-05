class TokenValidator:
    def validate(self, user):
        if user is None:
            return None
        return user.id
