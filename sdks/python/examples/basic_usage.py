from passportmcp import BrowserPassport


def main():
    # Initialize the client
    client = BrowserPassport()
    print("Client initialized successfully")

    # Example domain to test with
    domain = "example.com"

    try:
        # Try to get existing credentials
        creds = client.get_credentials(domain)
        print(f"Found existing credentials for {domain}")
        print(f"Headers: {creds.headers}")
        print(f"Cookies: {creds.cookies}")
    except Exception as e:
        print(f"No existing credentials found: {e}")
        print("You might need to authenticate first")


if __name__ == "__main__":
    main()
