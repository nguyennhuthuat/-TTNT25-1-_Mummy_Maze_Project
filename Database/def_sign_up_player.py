# Import the initialized client from your dedicated file
from supabase_client import supabase

def sign_up_player(username, password):
    """
    Signs up a new player using a username and password.
    A dummy email is created for Supabase's auth requirement.
    """
    try:
        # Create a dummy email using the username.
        # This email is only for Supabase's internal use.
        dummy_email = f"{username}@yourgame.com"

        res = supabase.auth.sign_up({
            "email": dummy_email,
            "password": password,
            "options": {
                "data": {
                    "username": username
                }
            }
        })

        # Since email confirmation is off, a session should be returned.
        if res.session:
            print(f"Sign up and login successful for user: {res.user.id}")
            return res.session
        else:
            # Handle cases where sign up might fail or return an unexpected result
            print(f"Sign up failed or requires an action. Response: {res}")
            return None

    except Exception as e:
        print(f"Error during sign up: {e}")
        return None