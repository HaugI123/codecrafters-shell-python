import sys
import os

def main():

    builtIns = ['type', 'exit', 'echo']

    while True:
        sys.stdout.write("$ ")

        command = input("")
        paths = os.environ['PATH'].split(':')

        if command == 'exit':
            break
        elif command.startswith('echo'):
            sys.stdout.write(f'{command[5:]}\n')
        elif command.startswith('type'):
            command = command[5:]
            if command in builtIns:
                sys.stdout.write(f'{command} is a shell builtin\n')
                break
            elif command not in builtIns:
                for path in paths:
                    if command in path & os.access(f'{path}/{command}', os.X_OK):
                        sys.stdout.write(f'{command} is {path}/{command}')
                    elif command in path & not os.access(f'{path}/{command}', os.X_OK):
                        continue
            else:
                sys.stdout.write(f'{command}: not found\n')
        else:
            sys.stdout.write(f'{command}: command not found\n')

    pass


if __name__ == "__main__":
    main()
