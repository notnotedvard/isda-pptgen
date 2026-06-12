import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="ISDA PPT Generator")
    subparsers = parser.add_subparsers(dest="command")

    # Command 1: Build Worship Service
    ws_parser = subparsers.add_parser("build-ws", help="Build a worship service presentation")
    ws_parser.add_argument("--config", help="Path to the WS config file")

    # Command 2: Generate Lyrics
    lyrics_parser = subparsers.add_parser("generate-lyrics", help="Generate hymn lyrics presentations")
    lyrics_parser.add_argument("--force", action="store_true", help="Force regenerate all")

    # Command 3: Web UI
    webui_parser = subparsers.add_parser("webui", help="Start the Streamlit Web UI")

    # Command 4: Songs Manager
    songs_parser = subparsers.add_parser("songs-manager", help="Start the Streamlit Songs Manager")

    # Command 5: Create config
    create_parser = subparsers.add_parser("create", help="Create an empty .yml file for the upcoming Saturday")
    create_parser.add_argument("-p", "--populate", action="store_true", help="Automatically populate from Google Sheet")

    # Command 6: Populate config
    populate_parser = subparsers.add_parser("populate", help="Populate empty fields in a given config from Google Sheet")
    populate_parser.add_argument("file", help="Path to the .yml config to populate")

    # Command 7: Images to slides
    images_parser = subparsers.add_parser("images-to-slides", help="Generate a presentation from images in the current directory")
    images_parser.add_argument("-o", "--output", default="images_presentation.pptx", help="Output file name (default: images_presentation.pptx)")
    images_parser.add_argument("-c", "--caption", default="", help="Caption to add to each slide")
    images_parser.add_argument("--extensions", default="jpg,jpeg,png,gif,bmp,webp", help="Comma-separated image extensions to include")
    images_parser.add_argument("-d", "--directory", default=None, help="Directory containing images (default: current directory)")

    args = parser.parse_args()

    if args.command == "build-ws":
        print(f"Building WS using config: {args.config}")
        from isda_pptgen.build_ws import load_yaml_config, build_presentation, DEFAULT_CONFIG
        cfg_path = Path(args.config) if args.config else Path(DEFAULT_CONFIG)
        config = load_yaml_config(cfg_path)
        build_presentation(config)
    elif args.command == "generate-lyrics":
        print(f"Generating lyrics. Force: {args.force}")
        from isda_pptgen.hymn_lyrics_generator import generate_all_hymns
        generate_all_hymns(args.force)
    elif args.command == "webui":
        print("Starting Web UI...")
        from streamlit.web import cli as stcli
        import isda_pptgen.webui as webui_module
        webui_path = Path(webui_module.__file__).resolve()
        sys.argv = ["streamlit", "run", str(webui_path)]
        sys.exit(stcli.main())
    elif args.command == "songs-manager":
        print("Starting Songs Manager...")
        from streamlit.web import cli as stcli
        import isda_pptgen.songs_ui as songs_module
        songs_path = Path(songs_module.__file__).resolve()
        sys.argv = ["streamlit", "run", str(songs_path)]
        sys.exit(stcli.main())
    elif args.command == "create":
        from isda_pptgen.config_manager import cmd_create
        # Basic logging config if needed
        import logging
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        cmd_create(args.populate)
    elif args.command == "populate":
        from isda_pptgen.config_manager import cmd_populate
        import logging
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        cmd_populate(Path(args.file))
    elif args.command == "images-to-slides":
        from isda_pptgen.images_to_slides import generate_from_images
        generate_from_images(
            output=args.output,
            caption=args.caption,
            extensions=tuple(ext.strip() for ext in args.extensions.split(",")),
            directory=args.directory
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
