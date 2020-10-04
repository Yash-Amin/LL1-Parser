from collections import defaultdict

START = 'S'

def isNonTerminal(x):
    return x.isupper()

def isTerminal(x):
    return not isNonTerminal(x)

def parse(s):
    s = s.replace(' ', '')
    s = s.split('->')
    if len(s) != 2:
        print(s)
        raise Exception()

    lhs, rhs = s

    lhs = lhs.strip()
    rhs = rhs.strip()

    if len(lhs) == 0 or len(rhs) == 0:
        raise Exception()

    rhsParts = [part.strip() for part in rhs.split('|')]
    if '' in rhsParts:
        rhsParts.remove('')
        
    return lhs, rhsParts


def readRules():

    rules = []
    print('[!] Enter Rules:')

    while True:
        try:
            s = input(' >  ').strip()
        except EOFError:
            break

        if s == '':
            break

        rules += [s]

    return rules


def getFirst(rules):

    
    # nullables -----------------------
    tmp = []
    nullables = []

    for rule in reversed(rules):
        lhs, rhsParts = parse(rule)
 
        for part in rhsParts:
            if part == '#':
                nullables += [lhs]
                break
        
    for rule in reversed(rules):
        lhs, rhsParts = parse(rule)

        for part in rhsParts:
            for c in part:
                if isNonTerminal(c) and c in nullables:
                    part = part.replace(c, '#')
            part = part.replace('#', '')
            if part == '':
                nullables += [lhs]
                break

    nullables = list(set(nullables))
    # ---------------------------------



    allNonTerminals = []

    for rule in rules:
        lhs, _ = parse(rule)
        allNonTerminals += lhs

    allNonTerminals = list(set(allNonTerminals))

    queue = rules.copy()
    found = defaultdict(bool)
    firstSet = defaultdict(set)

    while len(queue) != 0:
        rule = queue[0]
        lhs, rhsParts = parse(rule)
        if found[lhs]:
            queue.remove(rule)
            continue

        isFirstNonTerminal = False

        for part in rhsParts:
            if isTerminal(part[0]):
                continue

            if found[part[0]]:
                continue

            isFirstNonTerminal = True

        if isFirstNonTerminal:
            queue.remove(rule)
            queue.append(rule)
            continue

        # Current rule only contains terminals
        currentFirst = set()
        for rhsPart in rhsParts:
            if isTerminal(rhsPart[0]):
                currentFirst.add(rhsPart[0])
            else:
                for c in rhsPart:
                    currentFirst = currentFirst | firstSet[c]
                    if c not in nullables:
                        break

        firstSet[lhs] = currentFirst
        found[lhs] = True

    return firstSet




def getFollow(rules, first):
    allNonTerminals = set()

    # nullables -----------------------
    tmp = []
    nullables = []

    for rule in reversed(rules):
        lhs, rhsParts = parse(rule)
 
        for part in rhsParts:
            if part == '#':
                nullables += [lhs]
                break
        
    for rule in reversed(rules):
        lhs, rhsParts = parse(rule)

        for part in rhsParts:
            for c in part:
                if isNonTerminal(c) and c in nullables:
                    part = part.replace(c, '#')
            part = part.replace('#', '')
            if part == '':
                nullables += [lhs]
                break

    nullables = list(set(nullables))
    # ---------------------------------


    followSet = defaultdict(set)

    for rule in rules:
        lhs, rhsParts = parse(rule)
        allNonTerminals.add(lhs)

    merge = []
    for tmprule in rules:
        nonTerminal = parse(tmprule)[0]
        # print('NT', nonTerminal)
        if nonTerminal == START:
            followSet[nonTerminal] = set('$')
            continue
        
        for rule in rules:
            if nonTerminal not in rule.split('->')[1]:
                continue
            
            lhs, rhsParts = parse(rule)

            # print('\t',rule)

            for part in rhsParts:
                if nonTerminal not in part:
                    continue
                index = part.index(nonTerminal) 
                nextStr = part[index+1:]
                # print('\tNext:', nextStr)
                '''
                    Example: nextTerminal = B, part = aBDh
                        it will check for each char after B
                            here D is nullable so h will 
                            be included too.. 
                        if anything is not nullable it will break
                '''
                if nextStr == '':
                    if lhs != nonTerminal:
                        # print('\t Merged ', nonTerminal, lhs)
                        newSet = followSet[lhs] | followSet[nonTerminal]
                        followSet[lhs] = newSet
                        followSet[nonTerminal] = newSet
                counter = 0

                for c in nextStr:
                    if isTerminal(c):
                        followSet[nonTerminal].add(c)
                        counter += 1
                        break
                    # print('\t',c, first[c])
                    
                    for x in first[c]:
                        if x != '#':
                            followSet[nonTerminal].add(x)


                    if c not in nullables:
                        counter += 1
                        break
                
                if counter == 0:
                    for c in followSet[lhs]:
                        followSet[nonTerminal].add(c)
                    # print(f'\t {lhs}------')

    return followSet


def getFirstFollow(rules):
    first = getFirst(rules)    
    follow = getFollow(rules, first)

    print('\n[!] First:')
    printdd(first)

    print('\n[!] Follow:')
    printdd(follow)

    return first, follow


def getNonTerminals(rules):
    x = set()

    for rule in rules:
        lhs, rhsParts = parse(rule)
        x.add(lhs)

    return x


def getTerminals(rules):
    x = set()

    for rule in rules:
        lhs, rhsParts = parse(rule)
        for part in rhsParts:
            for c in part:
                if isTerminal(c):
                    x.add(c)
    return x


def getTable(first, follow, rules):
    nonTerminals = getNonTerminals(rules)
    terminals = getTerminals(rules)
    

    table = defaultdict(lambda: defaultdict(str))

    for rule in rules:
        lhs, rhsParts = parse(rule)

        for part in rhsParts:
            if part == '#':
                fs = follow[lhs]
                for fElement in fs:
                    table[lhs][fElement] = lhs + ' -> ' + part
                continue

            char = part[0]
            if isTerminal(char):
                table[lhs][char] = lhs + ' -> ' + part
            else:
                fs = first[char]
                doFollow = False
                for fElement in fs:
                    if fElement == '#':
                        doFollow = True
                        continue
                    table[lhs][fElement] = lhs + ' -> ' + part
                if doFollow:
                    fs = follow[lhs]
                    for fElement in fs:
                        table[lhs][fElement] = lhs + ' -> ' + part

    return table

def getStart(rules):
    for x in rules:
        lhs, _ = parse(x)
        if lhs == START:
            return x
    raise Exception()

def getRhs(rules, lhs):
    for x in rules:
        l, _ = parse(x)
        if lhs == l:
            return x
    return ''


def test(table, first, follow, rules, s):
    stack = []
    start = getStart(rules)
    lhs, rhs = parse(start)
    stack = list(reversed(rhs[0] + '$'))

    print('Start: ', start)
    print('String: ', s)
    
    while len(stack) > 1:
        print('> Stack : ', stack)
        print('> String: ', s)
        print('\tChar: ', s[0])

        if stack[-1] == '#':
            stack = stack[:-1]
            print('\tAction: POP')
            continue

        if isNonTerminal(stack[-1]):
            last = stack[-1]
            stack = stack[:-1]
            
            newRule = table[last][s[0]]
            if newRule == '':
                print('\n[-] Not matched! ')
                break

            l, r = parse(newRule)
            r = list(reversed(list(r[0])))

            for z in r:
                stack.append(z)

            print('\tAction: POP')
            
            continue

        if stack[-1] != s[0]:
            print('ERROR')
            break

        print('\tMatched')
        stack = stack[:-1]
        s = s[1:]

        # if non terminal
        #  replace it...

    if stack[0] == '$' and len(stack) == 1:
        print('\n[+] Accepted!')
        
def printdd(x):
    for k in x:
        print('\t', k, ':',  x[k])

def printTable(table):
    # Getting max length of any column
    columns = defaultdict(int)
    for key in table:
        for column in table[key]:
            columns[column] = max(columns[column], len(table[key][column]))


    # Print column header
    print('\t  |', end='')
    lineLength = 0

    for column in columns:
        s = column
        
        maxChars = columns[column]
        spaces = maxChars - len(s)
        
        print('', column, ' ' * (spaces), '|', end='')
        lineLength += maxChars + 4

    print()
    print('\t ', '-' * lineLength)

    for terminal in table:
        print('\t', terminal, end='|')
        for column in columns:
            currentValue = table[terminal][column]

            maxChars = columns[column]
            spaces = maxChars - len(currentValue)

            print('', currentValue, ' ' * (spaces), '|', end='')
        print()


def main():
    rules = readRules()

    print()
    # print(rules)

    first, follow = getFirstFollow(rules)
    
    t = getTable(first, follow, rules)

    print('\n[!] Parsing table:')
    # for x in t:
    #     print('\t', x,'::', dict(t[x]))

    printTable(t)


    s = input('\n> Enter string: ')
    s += '$'
    print()
    print()

    test(t, first, follow, rules, s)

print()
main()
