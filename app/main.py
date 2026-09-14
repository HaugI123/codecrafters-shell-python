import sys


def main():
    # TODO: Uncomment the code below to pass the first stage
    while True:
        sys.stdout.write("$ ")

        command = input("")

        if command == 'exit':
            break
        elif command.startswith('echo'):
            sys.stdout.write(f'{command[5:]}\n')
        else:
            sys.stdout.write(f'{command}: command not found\n')



    pass


if __name__ == "__main__":
    main()
