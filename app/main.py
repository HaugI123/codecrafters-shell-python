import sys
import os

def main():

    builtIns = ['type', 'exit', 'echo', 'pwd']

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
            elif command[5:] not in builtIns:
                found = False
                for path in paths:
                    fileName = os.path.join(path, command[5:])

                    if os.path.isfile(fileName) and os.access(fileName, os.X_OK):
                        sys.stdout.write(f'{command[5:]} is {fileName}\n')
                        found = True
                    elif os.path.isfile(fileName) and not os.access(fileName, os.X_OK):
                        continue
                if not found:
                    sys.stdout.write(f'{command[5:]}: not found\n')
        elif command.startswith('pwd'):
            sys.stdout.write(f'{os.getcwd()}\n')
        elif command.startswith('cd'):
            path = command[3:]
            try:
                os.chdir(path)
                if path.startswith('~'):
                    os.chdir(os.environ['HOME'])
            except FileNotFoundError:
                sys.stdout.write(f'cd: {path}: No such file or directory\n')
        elif command not in builtIns:
            found = False
            for path in paths:
                    cmdList = command.split(" ")

                    fileName = os.path.join(path, cmdList[0])

                    if os.path.isfile(fileName) and os.access(fileName, os.X_OK):
                        os.system(command)
                        found = True
            if not found:
                sys.stdout.write(f'{command}: command not found\n')


    pass


if __name__ == "__main__":
    main()
