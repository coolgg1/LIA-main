import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LIA admin CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    register = subparsers.add_parser("register", help="Register a device")
    register.add_argument("--name", required=True)

    status = subparsers.add_parser("status", help="Show daemon status")
    status.add_argument("--endpoint", default="http://localhost:8000")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "register":
        print(f"Registered device: {args.name}")
    elif args.command == "status":
        print(f"Daemon endpoint: {args.endpoint}")


if __name__ == "__main__":
    main()
