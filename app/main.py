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
                for path in paths:
                    if command[5:] in path and os.access(f'{path}/{command[5:]}', os.X_OK):
                        sys.stdout.write(f'{command[5:]} is {path}/{command[5:]}')
                    elif command[5:] in path and not os.access(f'{path}/{command{5:}}', os.X_OK):
                        continue
            else:
                sys.stdout.write(f'{command[5:]}: not found\n')
        else:
            sys.stdout.write(f'{command}: command not found\n')



    pass


if __name__ == "__main__":
    main()
