import sys
import os
import readline
import subprocess
from pathlib import Path

dictKey = dict()
jobsDict = dict()
jobNumDict = dict()
builtIns = ['type', 'exit', 'echo', 'pwd', 'complete', 'jobs', 'history']
historyList = []

def myParser(arg):

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

        if char == " " and not specState:
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
            #adding the word echo
            finParsed.append(string)
            continue

        if string == ' ':
            #Continuing the string I actually dont think this does anything my parser removes spaces IDKY I implemented this
            tempStr += string
            print(tempStr) #Yeah this never prints pretty sure it does nothing atm. Unless I was using it for '' or "" logic.
            continue

        if tempStr and not tempStr.endswith(' '):
            #if valid tempString (a word was added based on what was parsed) then add a space before adding the next word
            tempStr += ' '

        #add word to tempStr
        tempStr += string

        #For index if at the end of the parsed list length append the new string - whitespace from the left to the final parsed list. IDKY I did lstrip() must have thought it necessary when building it though.
        if i == len(parsed)-1:
            finParsed.append(tempStr.lstrip())

    #Output value that makes it to final list in index 1
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

        if parsed[0] in dictKey.keys():
            if 'completer' in dictKey[parsed[0]][0].lower() and dictKey[parsed[0]][1] == False:

                env = os.environ.copy()
                env['COMP_LINE'] = line
                env['COMP_POINT'] = str(readline.get_endidx())

                output = subprocess.run([dictKey[parsed[0]][0], parsed[0], parsed[-1], parsed[-2]], capture_output=True, text=True, env=env)
                result = output.stdout.splitlines()
                result = [f'{x} ' for x in result]
                return result[state]
            else:
                result = dictKey[line.strip()][1][0]
                results = [result + ' '] + [None]
                return results[state]

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
        if not dictKey.get(cmd):
            sys.stderr.write(f'complete: {cmd}: no completion specification\n')
        else:
            sys.stdout.write(f"complete -C '{dictKey.get(cmd)}' {cmd}\n")
    if parsed[1] == '-C':

        response = ''
        try:
            response = subprocess.run(parsed[-2], capture_output=True)
            response = response.stdout.decode('utf-8').split('\n')
        except Exception:
            pass
        try:
            if response[0]:
                dictKey.update({parsed[-1]: [parsed[-2], response]})
            else:
                dictKey.update({parsed[-1]: [parsed[-2], False]})
            return
        except Exception:
            pass

        dictKey.update({parsed[-1]: parsed[-2]})

    if parsed[1] == '-r':
        dictKey.pop(parsed[-1])

def jobFunc(parsed, jobNum, cmd):

    if len(parsed) == 1:
        dynamicMarkerUpdater()
        for key in jobsDict.keys():

            for newKey in jobNumDict.keys():
                if newKey == jobsDict[key][0]:
                    jobsDict[key][1] = jobNumDict[newKey]

            tempList = jobsDict[key]

            if tempList[-1].poll() is not None:
                tempList[2] = 'Done                    '
                tempList[3] = tempList[3].replace('&', '')

            sys.stdout.write(f'[{tempList[0]}]{tempList[1][0]}  {tempList[2]}{tempList[3]}\n')

        removalKeys = [key for key, value in jobsDict.items() if 'Done                    ' in value]
        for key in removalKeys:
            jobNumDict.update({jobsDict[key][0]: ['', 'free']})
            jobsDict.pop(key)

    if '&' in parsed:
        parsed.remove('&')
        backJob = subprocess.Popen(parsed)
        sys.stdout.write(f'[{jobNum}] {backJob.pid}\n')
        jobsDict.update({backJob.pid: [jobNum, '+', 'Running                 ', cmd, backJob]})
        jobNumDict.update({jobNum: ['', 'used']})
        jobNum += 1

    jobNum = jobNumUpdater(jobNum)

    dynamicMarkerUpdater()
    return jobNum

def backgroundJobsTest():
    dynamicMarkerUpdater()
    for key in jobsDict.keys():

        for newKey in jobNumDict.keys():
            if newKey == jobsDict[key][0]:
                jobsDict[key][1] = jobNumDict[newKey]

        tempList = jobsDict[key]

        if tempList[-1].poll() is not None:
            tempList[2] = 'Done                    '
            tempList[3] = tempList[3].replace('&', '')
            sys.stdout.write(f'[{tempList[0]}]{tempList[1][0]}  {tempList[2]}{tempList[3]}\n')

    removalKeys = [key for key, value in jobsDict.items() if 'Done                    ' in value]
    for key in removalKeys:
        jobNumDict.update({jobsDict[key][0]: ['', 'free']})
        jobsDict.pop(key)

def dynamicMarkerUpdater():

    keyList = [key for key,value in jobNumDict.items() if 'free' not in value]
    keyList.sort()
    if keyList:
        maxVal = max(keyList)

    for key in jobNumDict.keys():
        if 'free' in jobNumDict[key]:
            break
        if key == maxVal:
            jobNumDict[key] = ['+', 'used']
        elif len(keyList) == 2:
            if key != maxVal:
                jobNumDict[key] = ['-', 'used']
        elif len(keyList) > 2:
            if key == keyList[-2]:
                jobNumDict[key] = ['-', 'used']
            else:
                jobNumDict[key] = [' ', 'used']

    return

#Did 2 things for recycling job numbers. Added the if 'free' check inside of dynamicMarkerUpdater() so it stopped overwritting every value in th edictionary. Also added a jobNumUpdater() function to update the job number. It iterates over every free key inside the jobNumDict and selects the minimum key as the recycled job num. It does cause some bugs that I can adjust later just trying to see functionally if it works. I did pass, the bug is that jobs prints out of order. I will check normal shell to see if that is how it works or if it prints in order. NVM seems like bash doesnt recycle job numbers yeah it does it was just behaving weirdly pretty sure it prints in order of job number though need to fix that bug

def jobNumUpdater(curNum):
    """Function to update job number based on available numbers"""

    jobNumList = [key for key,value in jobNumDict.items() if 'free' in value]

    if not jobNumList:
        return curNum

    jobNumList.sort()

    return min(jobNumList)


def pipeFunc(paths, cmdName, command, parsed, job):

    #First thought need to do parsing like I do inside echo. Not sure if I should duplicate the code or create another parser function specific to this use case of building a list with the information split at the pipe delimeter. Actually I think it would be much easier to just loop over the parsed list already, run subproccess.Popen(parsed[previousIndex:indexOf|], stdout=subprocess.PIPE, stderr=subprocess.PIPE) update the previous index to current indexOf|, check for another | in list if not one then indexOf| = -1 use output, error = subprocessetc.etc.communicate() and pass output as input in the next subprocess.Popen() call. Have it recursively do this until there are no more | found in the parsed list.

    #many pipe logic
    numOfPipeDelims = parsed.count('|')
    if numOfPipeDelims>1:
        #thought process is to get the index of first pipe run cmd update parsed to be the rest of the code get the next and cycle etc. for or while loop?? I think while but I tend to use for. Ill implement both see what is easier. During while implementation I realized I didnt know how to "verify" that I was on the last command for loops seem easier since I can do a range based on numOfPipeDelims and if x and numOfPipeDelims == then I know I am at the end. Thought I could get while loops to work dont think I can switching to for loop now
        output = subprocess.PIPE
        '''while '|' in parsed:
            pipe = parsed.index('|')
            cmd = parsed[:pipe]

            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=output)

            output = p.stdout

            parsed = parsed[pipe+1:]
        '''

        for x in range(numOfPipeDelims+1):
            #THERE HAS TO BE A BETTER WAY TO DO THIS I AM JUST MESSING SOMETHING UP AND DONT SEE IT. sadly it worked and I passed the test lol this is definitely shit ass code though. Using an error to test the proper case seems insane to me lmfaooooo
            try:
                pipe = parsed.index('|')
                cmd = parsed[:pipe]
            except ValueError:
                cmd = parsed
                if cmd[0] in builtIns:
                    cmdToRun(paths, cmd[0], command, cmd, job)
                    historyList.append(cmd)
                    return

            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=output)
            output = p.stdout
            parsed = parsed[pipe+1:]

            historyList.append(cmd)

        if '|' not in parsed:
            for line in p.stdout:
                sys.stdout.write(line.decode('utf-8'))
                sys.stdout.flush()

    #Initial logic only assumes a single | operator.
    if numOfPipeDelims == 1:
        locationOfPipe = parsed.index('|')
        cmd1 = parsed[:locationOfPipe]
        cmd2 = parsed[locationOfPipe+1:]

        if cmd2[0] in builtIns:
            cmdToRun(paths, cmd2[0], command, cmd2, job)
            return

        #run both commands
        #use the output of the 1st command as the input of the second
        #close the I/O stream for 1st command
        p = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(cmd2, stdin=p.stdout, stdout=subprocess.PIPE)
        p.stdout.close()

        historyList.append(cmd1)
        historyList.append(cmd2)

        #iterate over stdout for second command, write lines as they become available. Decode with utf-8 because it returns as bytes. Remove from buffer after writing
        for line in p2.stdout:
            sys.stdout.write(line.decode('utf-8'))
            sys.stdout.flush()

        #Waits for process to finish before moving on
        p2.wait()

    return

def cmdToRun(paths, cmdName, command, parsed, job):
    if any(st in parsed for st in ('>', '1>', '2>')):
        cmdName = 'redirect'
    elif any(st in parsed for st in ('>>', '1>>', '2>>')):
        cmdName = 'append'
    elif parsed[-1] == '&':
        cmdName = 'jobs'
    elif '|' in parsed:
        cmdName = 'pipe'

    if cmdName != 'pipe':
        historyList.append(command+'\n')

    match cmdName:
        case 'pipe':
            pipeFunc(paths, cmdName, command, parsed, job)
        case 'echo':
            echoFunc(parsed)
        case 'exit':
            exit
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
        case 'jobs':
            job = jobFunc(parsed, job, command)
        case 'history':
            if len(parsed)>1:
                historyFunc(int(parsed[1]))
            else:
                historyFunc(0)
        case _:
            runProg(paths, cmdName, command, parsed)

    return job

def historyFunc(n):
    if n>0:
        tempHistList = historyList[-n:]
        start = len(historyList) - len(tempHistList)
    else:
        tempHistList = historyList
        start = 0
    for count,cmd in enumerate(tempHistList, start=start+1):
        sys.stdout.write(f'{count} {cmd}')

def main():

    paths = os.environ['PATH'].split(':')

    vocab = set([x+' ' for x in builtIns])
    vocab = updateSet(paths, set1=vocab)

    readline.parse_and_bind('tab: complete')
    readline.set_completer_delims(' \t\n/')
    readline.set_completer(customCompleter(vocab))

    job = 1

    while True:
        backgroundJobsTest()
        job = jobNumUpdater(job)
        command = input("$ ")
        parsed = myParser(command)
        if parsed:
            cmdName = parsed[0]
            if cmdName == 'exit':
                break
            job = cmdToRun(paths, cmdName, command, parsed, job)

    pass


if __name__ == "__main__":
    main()
