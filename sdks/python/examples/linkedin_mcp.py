from passportmcp import PassportMCP

# Create a PassportMCP instance for LinkedIn
mcp = PassportMCP("linkedin", "linkedin.com")

# Define MCP tools using the decorator


@mcp.tool()
async def search_linkedin(query: str):
    """Search LinkedIn for a given query."""
    # The browser instance is automatically authenticated
    response = mcp.browser.get(
        "https://www.linkedin.com/voyager/api/search/blended",
        params={"keywords": query, "origin": "GLOBAL_SEARCH_HEADER"},
    )
    return response.json()


@mcp.tool()
async def get_profile(profile_id: str):
    """Get a LinkedIn profile by ID."""
    response = mcp.browser.get(
        f"https://www.linkedin.com/voyager/api/identity/profiles/{profile_id}"
    )
    return response.json()


async def main():
    # Search for a company
    results = await search_linkedin("Microsoft")
    print("Search results:", results)

    # Get a specific profile
    profile = await get_profile("bill-gates")
    print("Profile data:", profile)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
