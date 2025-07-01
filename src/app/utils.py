import random
import string

class SessionManager:
    @staticmethod
    def generate_session_id():
        """
        Generates a 24-character alphanumeric session ID
        formatted as 4 sets of 6 characters separated by dashes.
        Example: X4a9Kf-Gm3WQ7-Po29Ls-ZxL8qB
        """
        chars = string.ascii_letters + string.digits
        session_parts = [''.join(random.choices(chars, k=6)) for _ in range(4)]
        return '-'.join(session_parts)
