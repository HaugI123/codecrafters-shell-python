import sys
import os
import readline
import subprocess
from pathlib import Path

def myParser(arg):

    global skip
    global dictKey
    dictKey = dict()
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

        if ord(char) == 92 and stepChar != "'":
            nextChar = arg[i+1]
            skip = True

            if specState and stepChar == '"':

                match nextChar:
                    case '"':
                        tempStr += nextChar
                        continue
                    case '\\':
                        tempStr += '\\'
                        continue

            tempStr += nextChar


        if ord(char) != 92 or stepChar == "'":
            tempStr += char

    if tempStr:
        endList.append(tempStr)

    return endList

def echoFunc(parsed):

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
            sys.stderr.write(f'{command}: not found\n')

def cdFunc(path):
    try:
        if path == '~':
            os.chdir(os.getenv('HOME'))
        else:
            os.chdir(path)
    except FileNotFoundError:
        sys.stderr.write(f'cd: {path}: No such file or directory\n')

def catFunc(statements):
    subprocess.run(statements)

def runProg(paths, name, command, parsed):
    found = False
    for path in paths:
            fileName = os.path.join(path, name)

            if os.path.isfile(fileName) and os.access(fileName, os.X_OK):
                subprocess.run(parsed)
                found = True
                break
    if not found:
        sys.stderr.write(f'{command}: command not found\n')

def redirectFunc(fileName, cmd):

    if '>' in cmd:
        redirect = '>'
    elif '1>' in cmd:
        redirect = '1>'
    else:
        redirect = '2>'

    stdoutFile = open(fileName,'w') if redirect == '>' or redirect == '1>' else None
    stderrFile = open(fileName, 'w') if redirect == '2>' else None

    index = cmd.index(redirect)

    text = cmd[:index]

    try:
        subprocess.run(text, stdout=stdoutFile, stderr=stderrFile)
    finally:
        if stdoutFile:
            stdoutFile.close()
        if stderrFile:
            stderrFile.close()

def appendFunc(fileName, cmd):

    if '>>' in cmd:
        redirect = '>>'
    elif '1>>' in cmd:
        redirect = '1>>'
    else:
        redirect = '2>>'

    stdoutFile = open(fileName,'a') if redirect == '>>' or redirect == '1>>' else None
    stderrFile = open(fileName, 'a') if redirect == '2>>' else None

    index = cmd.index(redirect)

    text = cmd[:index]

    try:
        subprocess.run(text, stdout=stdoutFile, stderr=stderrFile)
    finally:
        if stdoutFile:
            stdoutFile.close()
        if stderrFile:
            stderrFile.close()

def customCompleter(vocab):
    #Followed a guide on eli.thegreenplace.net to generate this function
    #Understand whats going on wouldnt have thought to generate it like this myself though

    def complete(text, state):


        line = readline.get_line_buffer()
        parsed = myParser(line)
        test = False
        for x in parsed:
            if '/' in x:
                path = x
                test = True
                break

        print(dictKey)

        if text in dictKey.keys():
            return list(dictKey.values()[0][1])

        if ' ' in line and not test:
            tempSet = updateSet(parsed, fullPath=True)
            results = [x for x in tempSet if x.startswith(text)] + [None]
            return results[state]
        elif test:
            tempSet = updateSet(path, testPath=True, fullPath=True)
            results = [x for x in tempSet if x.startswith(text)] + [None]

            result = results[state]

            if result is None:
                return None

            fullPath = Path(path) / result if Path(path).is_dir() else Path(path).parent / result

            return result + '/' if fullPath.is_dir() else result + ' '

        else:
            results = [x for x in vocab if x.startswith(text)] + [None]
            return results[state]

    return complete

def updateSet(paths, testPath=False, set1=set(), fullPath=False):


    if testPath and fullPath:
        set2 = set()
        try:
            if not Path(paths).resolve().exists():
                if Path(paths).parent.exists():
                    for temp in Path(paths).parent.iterdir():
                        set2.add(temp.name)
            else:
                for temp in Path(paths).resolve().iterdir():
                    set2.add(temp.name)

            return set2

        except TypeError:
            pass
    elif fullPath and not testPath:
        set2 = set()
        for path in Path(os.getcwd()).iterdir():

            if not path.exists():
                continue

            if path.is_dir():
                set2.add(f'{path.name}/')
            else:
                set2.add(f'{path.name} ')

        return set2

    else:

        for path in paths:
            newPath = Path(path)

            if not newPath.exists():
                continue

            for temp in newPath.iterdir():
                set1.add(f'{temp.name} ')

        for path in Path(os.getcwd()).iterdir():

            if not path.exists():
                continue

            set1.add(f'{path.name}/')

        return set1

def completeFunc(parsed):
    if parsed[1] == '-p':
        cmd = parsed[-1]
        if not dictKey.get(f'{cmd}'):
            sys.stderr.write(f'complete: {cmd}: no completion specification\n')
        else:
            sys.stdout.write(f"complete -C '{dictKey.get(cmd)}' {cmd}\n")
    if parsed[1] == '-C':
        #cKey.update({f'{parsed[-1]}': f'{parsed[-2]}'})
        response = subprocess.run(parsed[-2], capture_output=True)
        response = response.stdout.decode('utf-8').split('\n')
        dictKey.update({f'{parsed[-1]}': f'{[parsed[-2], response[0]]}'})

def main():

    builtIns = ['type', 'exit', 'echo', 'pwd', 'complete']
    paths = os.environ['PATH'].split(':')

    vocab = set([x+' ' for x in builtIns])
    vocab = updateSet(paths, set1=vocab)

    readline.parse_and_bind('tab: complete')
    readline.set_completer(customCompleter(vocab))

    while True:
        command = input("$ ")
        parsed = myParser(command)
        cmdName = parsed[0]
        if any(st in parsed for st in ('>', '1>', '2>')):
            cmdName = 'redirect'
        elif any(st in parsed for st in ('>>', '1>>', '2>>')):
            cmdName = 'append'

        match cmdName:
            case 'exit':
                break
            case 'echo':
                echoFunc(parsed)
            case 'type':
                typeFunc(builtIns, parsed[1], paths)
            case 'pwd':
                sys.stdout.write(f'{os.getcwd()}\n')
            case 'cd':
                cdFunc(parsed[1])
            case 'cat':
                catFunc(parsed)
            case 'redirect':
                redirectFunc(parsed[-1], parsed)
            case 'append':
                appendFunc(parsed[-1], parsed)
            case 'complete':
                completeFunc(parsed)
            case _:
                runProg(paths, cmdName, command, parsed)

    pass


if __name__ == "__main__":
    main()
