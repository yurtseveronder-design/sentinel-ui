import random

class UserDataFactory:
    @staticmethod
    def generate_random_user(name_prefix="Önder QA"):
        random_id = random.randint(1000, 9999)
        return {
            "name": f"{name_prefix} {random_id}",
            "username": f"user_{random_id}",
            "email": f"user_{random_id}@qa-test-domain.com",
            "address": {
                "street": "Automation Lane",
                "city": "Tech City"
            }
        }