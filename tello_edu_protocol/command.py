def command_encoded_from_args(command: str, *args: int | str) -> str:
    if args:
        return f"{command} {' '.join([str(arg) for arg in args])}".encode()
    else:
        return command.encode()

