import argparse

def main():
    parser = argparse.ArgumentParser(description="ISDA PPT Generator")
    subparsers = parser.add_subparsers(dest="command")

    # Command 1: Build Worship Service
    ws_parser = subparsers.add_parser("build-ws", help="Build a worship service presentation")
    ws_parser.add_argument("--config", help="Path to the WS config file")

    # Command 2: Generate Lyrics
    lyrics_parser = subparsers.add_parser("generate-lyrics", help="Generate hymn lyrics presentations")
    lyrics_parser.add_argument("--force", action="store_true", help="Force regenerate all")

    args = parser.parse_args()

    if args.command == "build-ws":
        print(f"Building WS using config: {args.config}")
        # TODO: Import and call the function from your build_ws module
    elif args.command == "generate-lyrics":
        print(f"Generating lyrics. Force: {args.force}")
        # TODO: Import and call the function from your hymn_lyrics_generator module
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
