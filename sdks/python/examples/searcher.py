import json
from datetime import datetime
import argparse
from typing import Dict, List, Optional
from passportmcp import BrowserPassport

# An example app of how to use the BrowserPassport SDK to search through Twitter DMs
# This app is a simple command-line tool that allows you to search through your Twitter DMs
# using various filters. It uses the BrowserPassport SDK to make requests to the Twitter API
# and process the data.

# it needs zero configuration, just install the BrowserPassport SDK and run the script


class TwitterDMSearch:
    def __init__(self, data: Dict):
        """Initialize the DM search tool with the Twitter data dictionary."""
        self.inbox_state = data.get('inbox_initial_state', {})
        self.entries = self.inbox_state.get('entries', [])
        self.messages = self._process_messages()

    def _process_messages(self) -> List[Dict]:
        """Convert raw message entries into a searchable format."""
        processed_messages = []

        for entry in self.entries:
            if 'message' not in entry:
                continue

            message = entry['message']
            message_data = message.get('message_data', {})

            processed_msg = {
                'id': message.get('id'),
                'conversation_id': message.get('conversation_id'),
                'time': message.get('time'),
                'request_id': message.get('request_id'),
                'message_data': {
                    'id': message_data.get('id'),
                    'time': message_data.get('time'),
                    'recipient_id': message_data.get('recipient_id'),
                    'sender_id': message_data.get('sender_id'),
                    'text': message_data.get('text', ''),
                    'edit_count': message_data.get('edit_count', 0),
                    'entities': message_data.get('entities', {}),
                    'reply_data': message_data.get('reply_data')
                }
            }
            processed_messages.append(processed_msg)

        return processed_messages

    def search(self,
               query: Optional[str] = None,
               conversation_id: Optional[str] = None,
               sender_id: Optional[str] = None,
               recipient_id: Optional[str] = None,
               limit: int = 10) -> List[Dict]:
        """
        Search through DMs with various filters.

        Args:
            query: Text to search for in messages
            conversation_id: Filter by specific conversation
            sender_id: Filter by sender ID
            recipient_id: Filter by recipient ID
            limit: Maximum number of results to return
        """
        results = self.messages.copy()

        # Apply text search
        if query:
            query = query.lower()
            results = [
                msg for msg in results
                if query in msg['message_data']['text'].lower()
            ]

        # Apply conversation filter
        if conversation_id:
            results = [
                msg for msg in results
                if msg['conversation_id'] == conversation_id
            ]

        # Apply sender filter
        if sender_id:
            results = [
                msg for msg in results
                if msg['message_data']['sender_id'] == sender_id
            ]

        # Apply recipient filter
        if recipient_id:
            results = [
                msg for msg in results
                if msg['message_data']['recipient_id'] == recipient_id
            ]

        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x['time'], reverse=True)

        return results[:limit]

    def get_conversations(self) -> List[str]:
        """Get a list of all unique conversation IDs."""
        return list(set(msg['conversation_id'] for msg in self.messages))

    def print_message(self, message: Dict):
        """Pretty print a message."""
        msg_data = message['message_data']
        time_str = datetime.fromtimestamp(
            int(message['time'])/1000).strftime('%Y-%m-%d %H:%M:%S')

        print(f"\n{'='*80}")
        print(f"ID: {message['id']}")
        print(f"Conversation: {message['conversation_id']}")
        print(f"Time: {time_str}")
        print(f"From: {msg_data['sender_id']}")
        print(f"To: {msg_data['recipient_id']}")
        print(f"Text: {msg_data['text']}")

        if msg_data.get('reply_data'):
            print(f"\nReplying to: {msg_data['reply_data']['text']}")

        if msg_data.get('entities', {}).get('user_mentions'):
            print("\nMentions:")
            for mention in msg_data['entities']['user_mentions']:
                print(f"- @{mention['screen_name']} ({mention['name']})")
        print(f"{'='*80}")


def main():
    parser = argparse.ArgumentParser(description='Search Twitter DMs')
    parser.add_argument('-q', '--query', help='Search text in messages')
    parser.add_argument('-c', '--conversation',
                        help='Filter by conversation ID')
    parser.add_argument('-s', '--sender', help='Filter by sender ID')
    parser.add_argument('-r', '--recipient', help='Filter by recipient ID')
    parser.add_argument('-l', '--limit', type=int, default=10,
                        help='Maximum number of results')
    parser.add_argument('--list-conversations',
                        action='store_true', help='List all conversation IDs')
    parser.add_argument('--save-json', action='store_true',
                        help='Save search results to a JSON file')
    args = parser.parse_args()

    # Load data
    client = BrowserPassport()
    print("\nMaking test request to X.com...")
    url = "https://x.com/i/api/1.1/dm/user_updates.json?nsfw_filtering_enabled=false&dm_secret_conversations_enabled=false&krs_registration_enabled=true&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_ext_limited_action_results=true&include_quote_count=true&include_reply_count=1&tweet_mode=extended&include_ext_views=true&dm_users=false&include_groups=true&include_inbox_timelines=true&include_ext_media_color=true&supports_reactions=true&supports_edit=true&include_ext_edit_control=true&include_ext_business_affiliations_label=true&ext=mediaColor%2CaltText%2CbusinessAffiliationsLabel%2CmediaStats%2ChighlightedLabel%2ChasParodyProfileLabel%2CvoiceInfo%2CbirdwatchPivot%2CsuperFollowMetadata%2CunmentionInfo%2CeditControl%2Carticle"

    response = client.get(url)
    # Initialize the search tool
    dm_search = TwitterDMSearch(response.json())

    # Save raw data if requested
    if args.save_json:
        output_file = f"twitter_dm_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(response.json(), f, indent=2)
        print(f"\nSaved complete DM data to {output_file}")
        return

    if args.list_conversations:
        conversations = dm_search.get_conversations()
        print("\nConversation IDs:")
        for conv_id in conversations:
            print(conv_id)
        return

    # Perform search
    results = dm_search.search(
        query=args.query,
        conversation_id=args.conversation,
        sender_id=args.sender,
        recipient_id=args.recipient,
        limit=args.limit
    )

    # Print results
    print(f"\nFound {len(results)} messages:")
    for msg in results:
        dm_search.print_message(msg)


if __name__ == "__main__":
    main()
