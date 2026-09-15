import sys
import os
import re

def main():

    builtIns = ['type', 'exit', 'echo', 'pwd']

    while True:
        sys.stdout.write("$ ")

        command = input("")
        cmdName = command.split(" ")[0]
        paths = os.environ['PATH'].split(':')

        if cmdName == 'exit':
            break
        elif cmdName == 'echo':
            command = re.sub("  *", " ", command) if not "'" in command else re.sub("'", "", command)
            sys.stdout.write(f'{command[5:]}\n')
        elif cmdName == 'type':
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
        elif cmdName == 'pwd':
            sys.stdout.write(f'{os.getcwd()}\n')
        elif cmdName == 'cd':
            path = command[3:]
            try:
                if path.startswith('~'):
                    os.chdir(os.getenv('HOME'))
                    continue
                os.chdir(path)
            except FileNotFoundError:
                sys.stdout.write(f'cd: {path}: No such file or directory\n')
        elif cmdName not in builtIns:
            found = False
            cmdList = command.split(" ")
            for path in paths:
                    fileName = os.path.join(path, cmdList[0])

                    if os.path.isfile(fileName) and os.access(fileName, os.X_OK):
                        os.system(command)
                        found = True
            if not found:
                sys.stdout.write(f'{command}: command not found\n')


    pass


if __name__ == "__main__":
    main()
