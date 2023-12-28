print("Введите регулярное выражение: ")
reg_exp = input()
pointer = 0
flag = False

# Класс для состояния НКА
class State:
    currentNumber = 0
    states = []  # глобальный список всех вершин

    def __init__(self):
        self.name = State.currentNumber  # в качестве имени присваиваем порядковый номер
        State.states.append(self)  # сохраняем новую вершину в глобальном списке вершин (для отладки)
        State.currentNumber += 1
        self.edges = {}  # ребра храним в хеш-таблице:
        # ключ - символ, значение - список вершин, в которые ведут ребра, помеченные этим символом

    def addEdge(self, symbol, state):  # метод добавления ребра с меткой symbol, ведущего в вершину state
        if (not (symbol in self.edges)):
            self.edges[symbol] = []
        self.edges[symbol].append(state)

    def __repr__(self):
        return (str(self.name))

    def __str__(self):
        return (str(self.name))

    def printEdges(self):  # печатаем содержимое вершины
        for symbol in self.edges:
            print("\t'" + symbol + "': " + str(self.edges[symbol]))


# функция печати НКА: выводит все вершины,
# созданные на текущий момент, и их ребра
def printStates():
    for state in State.states:
        print("State " + str(state))
        state.printEdges()
    print()


# мини-класс для хранения НКА - хранит только начальное и конечное состояния НКА
class NSM:
    def __init__(self, start, stop):
        self.startState = start
        self.stopState = stop

    def __repr__(self):
        return ("Start state is " + str(self.startState) + ", end state is " + str(self.stopState))

    def __getitem__(self, key):
        if key < len(State.states):
            return State.states[key]


# БАЗИС: создаем НКА для символа
def makeSymbolNSM(symbol):
    start = State()
    stop = State()
    start.addEdge(symbol, stop)
    return NSM(start, stop)


# ИНДУКЦИЯ: создаем автомат для регулярного выражения И
def makeAndNSM(leftNSM, rightNSM):
    for symbol in rightNSM.startState.edges:
        for state in rightNSM.startState.edges[symbol]:
            leftNSM.stopState.addEdge(symbol, state)
    return NSM(leftNSM.startState, rightNSM.stopState)


# ИНДУКЦИЯ: создаем автомат для регулярного выражения ИЛИ
def makeOrNSM(leftNSM, rightNSM):
    start = State()
    stop = State()
    start.addEdge('epsilon', leftNSM.startState)
    start.addEdge('epsilon', rightNSM.startState)
    leftNSM.stopState.addEdge('epsilon', stop)
    rightNSM.stopState.addEdge('epsilon', stop)
    return NSM(start, stop)


# ИНДУКЦИЯ: создаем автомат для регулярного выражения *
def makeClosureNSM(cNSM):
    start = State()
    stop = State()
    cNSM.stopState.addEdge('epsilon', cNSM.startState)
    start.addEdge('epsilon', cNSM.startState)
    start.addEdge('epsilon', stop);
    cNSM.stopState.addEdge('epsilon', stop)
    return NSM(start, stop)


def S():
    q = T()
    if q is None:
        return None
    p = S_(q)
    if p is None:
        return None
    return p


def S_(r):
    global pointer
    if pointer >= len(reg_exp):
        return r
    if reg_exp[pointer] == "+":
        pointer += 1
        q = T()
        if q is None:
            return None
        return S_(makeOrNSM(r, q))
    return r


def T():
    q = F()
    if q is None:
        return None
    p = T_(q)
    if p is None:
        return None
    return p


def T_(r):
    global pointer
    if pointer >= len(reg_exp):
        return r
    if reg_exp[pointer] not in ['1', '0', '*']:
        return r
    if reg_exp[pointer] == ')':
        return r
    p = F()
    if p is None:
        return None
    return T_(makeAndNSM(p, r))


def F():
    global pointer
    if pointer >= len(reg_exp):
        return None
    if reg_exp[pointer] == "(":
        pointer += 1
        q = S()
        if q is None:
            return None
        if pointer >= len(reg_exp) or reg_exp[pointer] != ")":
            return None
        pointer += 1
        return F_(q)
    q = X()
    if q is not None:
        q = F_(q)
        return q
    return None

def F_(q):
    global pointer
    if pointer >= len(reg_exp):
        return q
    if reg_exp[pointer] == "*":
        pointer += 1
        return makeClosureNSM(q)
    return q


def X():
    global pointer
    if reg_exp[pointer] in ['0', '1']:
        pointer += 1
        return makeSymbolNSM(reg_exp[pointer - 1])
    return None


def epsClosure(T):
    stack = []
    e_closure = T[:]
    for i in T:
        stack.append(i)

    while stack != []:
        t = stack.pop(-1)
        if 'epsilon' in t.edges:
            for u in t.edges['epsilon']:
                if u not in e_closure:
                    e_closure.append(u)
                    stack.append(u)

    return e_closure

def emulate(NSM, word):
    pointerition = 0
    S = epsClosure([NSM.startState])
    while pointerition < len(word):
        next = []
        for s in S:
            if word[pointerition] in s.edges:
                for i in s.edges[word[pointerition]]:
                    next.append(i)
        pointerition +=1

        S = epsClosure(next)

    for i in S:
        if i == NSM.stopState:
            return True

    return False

NSM = S()
if NSM is None or (pointer != len(reg_exp)):
    raise Exception('error')
else:
    print("Введите строку: ")
    exp = input()
    print(emulate(NSM, exp))
