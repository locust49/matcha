import os


def generate_verification_url(token):
    HOST = os.getenv("HOST")
    PORT = os.getenv("PORT")

    verification_url = f"http://{HOST}:{PORT}/auth/verify/{token}"
    print(f"Verification URL: {verification_url}")
    return verification_url
