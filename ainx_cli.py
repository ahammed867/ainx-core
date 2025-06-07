import argparse
from ainx.protocol import AINXMessage
from ainx.router import AINXRouterAgent

def main():
    parser = argparse.ArgumentParser(description="AINX CLI Interface")
    parser.add_argument("--sender", required=True, help="Name of the sending agent (e.g., 'human')")
    parser.add_argument("--intent", required=True, help="Intent of the message (e.g., 'search', 'plan')")
    parser.add_argument("--message", required=True, help="Content of the message payload")

    args = parser.parse_args()

    # Build AINX message format
    raw_msg = f"{args.sender}::router::QUERY::{args.intent}::{args.message}"

    # Create AINXMessage object
    msg = AINXMessage(raw_msg)

    # Route the message
    router = AINXRouterAgent("router")
    response = router.receive(msg)

    print("\n✅ Response from agent:")
    print(response)

if __name__ == "__main__":
    main()
