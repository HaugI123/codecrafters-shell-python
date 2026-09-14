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
            for word in builtIns:
                if command[5:] == word:
                    sys.stdout.write(f'{word} is a shell builtin\n')
                else:
                    continue
        else:
            sys.stdout.write(f'{command}: command not found\n')



    pass


if __name__ == "__main__":
    main()
