import sys
import os
import re
import subprocess

def myParser(arg):

    global skip
    skip = False
    specState = False
    specChars = ["'", '"']
    stepChar = ''

    tempStr = ''
    endList = []

    for i, char in enumerate(arg):

        if skip:
            skip = False
            continue

        if char in specChars and not specState:
            specState = True
            stepChar = char
            continue

        if specState and char == stepChar:
            specState = False
            continue

        if char == " " and not specState and char != '\\':
            if tempStr:
                endList.append(tempStr)
                tempStr = ''
            continue

        if ord(char) == 92 and stepChar != '"':
            nextChar = arg[i+1]
            skip = True
            tempStr += nextChar

        if ord(char) != 92 or specState:
            tempStr += char

    if tempStr:
        endList.append(tempStr)

    return endList

def echoFunc(parsed):

    #command = re.sub("  *", " ", command) if not "'" in command else re.sub("'", "", command)
    tempStr = ''
    finParsed = []

    for i, string in enumerate(parsed):

        if i == 0:
            finParsed.append(string)
            continue

        if string == ' ':
            tempStr += string
            continue

        if tempStr and not tempStr.endswith(' '):
            tempStr += ' '

        tempStr += string

        if i == len(parsed)-1:
            finParsed.append(tempStr.lstrip())

    sys.stdout.write(f'{finParsed[1]}\n')

def typeFunc(builtIns, command, paths):
    if command in builtIns:
        sys.stdout.write(f'{command} is a shell builtin\n')
    elif command not in builtIns:
        found = False
        for path in paths:
            fileName = os.path.join(path, command)

            if os.path.isfile(fileName) and os.access(fileName, os.X_OK):
                sys.stdout.write(f'{command} is {fileName}\n')
                found = True
            elif os.path.isfile(fileName) and not os.access(fileName, os.X_OK):
                continue
        if not found:
            sys.stdout.write(f'{command}: not found\n')

def cdFunc(path):
    try:
        if path == '~':
            os.chdir(os.getenv('HOME'))
        else:
            os.chdir(path)
    except FileNotFoundError:
        sys.stdout.write(f'cd: {path}: No such file or directory\n')

def catFunc(statements):
    subprocess.run(statements)

def runProg(paths, name, command):
    found = False
    for path in paths:
            fileName = os.path.join(path, name)

            if os.path.isfile(fileName) and os.access(fileName, os.X_OK):
                os.system(command)
                found = True
                break
    if not found:
        sys.stdout.write(f'{command}: command not found\n')

def main():

    builtIns = ['type', 'exit', 'echo', 'pwd']

    while True:
        sys.stdout.write("$ ")

        command = input("")
        paths = os.environ['PATH'].split(':')
        parsed = myParser(command)
        cmdName = parsed[0]

        match cmdName:
            case 'exit':
                break
            case 'echo':
                echo = echoFunc(parsed)
            case 'type':
                typeFunc(builtIns, parsed[1], paths)
            case 'pwd':
                sys.stdout.write(f'{os.getcwd()}\n')
            case 'cd':
                cdFunc(parsed[1])
            case 'cat':
                catFunc(parsed)
            case _:
                runProg(paths, cmdName, command)

    pass


if __name__ == "__main__":
    main()
