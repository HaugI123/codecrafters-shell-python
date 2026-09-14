import sys


def main():

    builtIns = ['type', 'exit', 'echo']

    while True:
        sys.stdout.write("$ ")

        command = input("")

        if command == 'exit':
            break
        elif command.startswith('echo'):
            sys.stdout.write(f'{command[5:]}\n')
        elif command.startswith('type'):
            if command[5:] in builtIns:
                sys.stdout.write(f'{command[5:]} is a shell builtin\n')
            else:
                sys.stdout.write(f'{command[5:]}: not found\n')
        else:
            sys.stdout.write(f'{command}: command not found\n')



    pass


if __name__ == "__main__":
    main()
