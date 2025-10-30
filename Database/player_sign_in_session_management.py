# Import the initialized client from your dedicated file
from supabase_client import supabase

# This is a conceptual helper function. In a real project, this would
# make a call to your Supabase Edge Function to get the email.
def get_email_from_username(username):
    """
    Calls a Supabase Edge Function to securely retrieve a user's email.
    Returns the email string or None if not found.
    """
    try:
        # The name 'get-email-from-username' would be the name of your Edge Function
        res = supabase.functions.invoke('get-email-from-username', invoke_options={'body': {'username': username}})
        if res.data and 'email' in res.data:
            return res.data['email']
        else:
            print(f"Could not find email for username: {username}")
            return None
    except Exception as e:
        print(f"Error invoking Edge Function: {e}")
        return None 


def sign_in_player(username, password):
    """Signs in an existing player with their username and password."""
    try:
        # Step 1: Get the user's email from their username via an Edge Function
        email = get_email_from_username(username)

        if not email:
            print("Login failed: Invalid username.")
            return None

        # Step 2: Use the retrieved email to sign in
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if res.session:
            print(f"Sign in successful. User ID: {res.user.id}")
            return res.session
        
    except Exception as e:
        # This will catch errors from sign_in_with_password, like an incorrect password
        print(f"Error during sign in: {e}")
        return None