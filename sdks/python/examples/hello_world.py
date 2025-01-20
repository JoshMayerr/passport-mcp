from passportmcp import BrowserPassport


def main():
    # Initialize the BrowserPassport client
    # It will automatically use credentials from the default storage path
    client = BrowserPassport()

    try:
        response = client.get(
            "https://www.linkedin.com/voyager/api/graphql/api/voyager/api/graphql?includeWebMetadata=true&variables=()&queryId=voyagerDashMySettings.7ea6de345b41dfb57b660a9a4bebe1b8"
        )

        if response.status_code == 200:
            data = response.json()
            print(data)
        else:
            print(f"Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    # You can also list all domains that have stored credentials
    print("\nAvailable domains with stored credentials:")
    for domain in client.list_domains():
        print(f"- {domain}")


if __name__ == "__main__":
    main()
