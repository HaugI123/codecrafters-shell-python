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
            if command[5:] in builtIns:
                sys.stdout.write(f'{command[5:]} is a shell builtin\n')
                break
            elif command[5:] not in builtIns:
                try:
                    for path in paths:
                        fileName = os.path.join(path, command[5:])

                        if os.path.isfile(fileName) and os.access(fileName, os.X_OK):
                            sys.stdout.write(f'{command[5:]} is {fileName}\n')
                except FileNotFoundError:
                    sys.stdout.write(f'{command[5:]}: not found\n')
                    continue
        else:
            sys.stdout.write(f'{command}: command not found\n')



    pass


if __name__ == "__main__":
    main()
