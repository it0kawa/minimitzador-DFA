import json

"""
Mai se minimitzar DFA's

to do:
    ~ dibuixar el DFA
"""


class DFA:
    def __init__(self, alfabet, Q, taulaTransicions, F, q0=None, show=True):
        self.alfabet = alfabet
        self.Q = Q
        self.taulaTransicions = taulaTransicions
        self.F = F
        self.q0 = q0 if q0 else Q[0]
        DFA.esCorrecteDFA(alfabet, Q, F, taulaTransicions, q0)
        self.show = show
        if show: self.displayDFA()
        
    @staticmethod
    def printError(msg):
        print(f"\n{'!' * 5} ERROR: {msg} {'!' * 5}\n")

    @staticmethod
    def valida(tipus, lst1, allowReps=False, lst2=None):
        if not lst1:
            DFA.printError(f"has d'introduir almenys un element per a '{tipus}'")
            return False
        
        if lst2 is None: return True
        if not(allowReps) and len(lst1) != len(set(lst1)):
            DFA.printError(f"hi ha '{tipus}' repetits: {set([_ for _ in lst1 if lst1.count(_)>1])}")
            return False
        if not set(lst1).issubset(lst2):
            invalids = set(lst1) - set(lst2)
            print(lst1, 'and 2', lst2)
            DFA.printError(f"els '{tipus}': {invalids} no existeixen")
            return False
        return True

    @staticmethod
    def esCorrecteDFA(alfabet, Q, F, TT, q0):
        if q0 not in Q:
            raise ValueError(f"estat inicial incorrecte: {q0}")
        if not DFA.valida("alfabet", alfabet):
            raise ValueError(f"alfabet incorrecte: {alfabet}")
        if not DFA.valida("estats", Q):
            raise ValueError(f"estats incorrectes: {Q}")
        if not DFA.valida("estat", F, Q):
            raise ValueError(f"estats finals incorrectes: {F}")
        if set(TT.keys()) != set(Q):
            raise ValueError(f"falten entrades de la taula de transicions: {set(Q) - set(TT.keys())}")
        for estat, trans in TT.items():
            if set(trans.keys()) != set(alfabet):
                raise ValueError(f"les transicions de l'estat {estat} no es corresponen amb l'alfabet {alfabet}")
            if not set(trans.values()).issubset(Q):
                raise ValueError(f"les transicions de l'estat {estat} van cap a estats que no existeixen")
    
    @staticmethod
    def printTT(TT, alfabet, F, q0):
        print("Taula de transicions:\n")
        print("Estat".ljust(12), end='')
        for simbol in alfabet:
            print(simbol.ljust(10), end='')
        print()
        print('-' * (12 + 10*len(alfabet)))
        for estat in TT:
            esFinal = '+' if estat in F else ' '
            esInicial = '->' if estat == q0 else '  '
            print(f"{esInicial}{estat}{esFinal}".ljust(12), end='')
            for simbol in alfabet:
                print(TT[estat][simbol].ljust(10), end='')
            print()
        print()
        
    def displayDFA(self):
        print('\n' + '=' * 60)
        print(" DFA ".center(60, "-"))
        self.printTT(self.taulaTransicions, self.alfabet, self.F, self.q0)
        
        # Potser afegire un dibuix del DFA en el futur         
        
    @staticmethod
    def read(msg, tipus):
        while True:
            print('\n' + '-' * 60)
            inp = input(f"escriu separant amb espais tots {msg}:\n> ")
            lst = list(dict.fromkeys(inp.strip().split()))
            if not DFA.valida(tipus, lst):
                continue
            print(f"{tipus}({len(lst)}):", ", ".join(lst))
            print('-' * 60)
            break
        return lst
    
    def saveDFA(self, filename):
        if not filename.endswith(".dfa"):
            filename += ".dfa"
            
        dfa = {
            "alfabet": self.alfabet,
            "estats": self.Q,
            "transicions": self.taulaTransicions,
            "finals": self.F,
            "inicial": self.q0
        }
        
        with open(filename, 'w') as f:
            json.dump(dfa, f, indent=2)
        print(f"DFA guardat (json) a {filename}")
        
    @classmethod
    def loadDFA(cls, filename):
        if not filename.endswith(".dfa"):
            filename += ".dfa"
            
        with open(filename, 'r') as f:
            dfa = json.load(f)
            
        alfabet = dfa.get("alfabet", [])
        TT = dfa.get("transicions", {})
        Q = dfa.get("estats", [])
        F = dfa.get("finals", [])
        q0 = dfa.get("inicial", Q[0] if Q else None)
        cls.esCorrecteDFA(alfabet, Q, F, TT, q0)        
        return cls(alfabet, Q, TT, F, q0=q0)
    
    @classmethod
    def makeDFA(cls):
        alfabet = cls.read("els simbols de l'alfabet", "alfabet")
        Q = cls.read("els estats del DFA", "estats")
        taulaTransicions = {}
        for estat in Q:
            print("\n" + "-" * 60)
            while True:
                print("alfabet:", ", ".join(alfabet))
                transicions = input(f"transicions de {estat} separades per espais:\n> ").strip().split()
                if len(transicions) != len(alfabet):
                    cls.printError("et falta alguna transicio!")
                    continue
                if not cls.valida("estat", transicions, allowReps=True, lst2=Q):
                    continue
                break
            taulaTransicions[estat] = dict(zip(alfabet, transicions))

        while True:
            F = cls.read("els estats finals", "estats finals")
            if not cls.valida("estats finals", F, lst2=Q):
                continue
            break
        
        while True:
            q0 = input(f"quin es l'estat inicial? (Q[0] = {Q[0]} per defecte)\n> ").strip()
            if q0 == "":
                q0 = Q[0]
                print(f"Estat inicial per defecte: {Q[0]}")
                break
            elif q0 not in Q:
                cls.printError(f"l'estat inicial {q0} no pertany a Q")
                continue
            break

        return cls(alfabet, Q, taulaTransicions, F, q0=q0)
            
    def minimitza(self):
        # minimitzacio per hopcroft O(nlogn)
        def eliminaInaccessibles():
            accessibles = set()
            queue = [self.q0]
            
            while queue:
                top = queue.pop()
                if top not in accessibles:
                    accessibles.add(top)
                    for simbol in self.alfabet:
                        transicio = self.taulaTransicions[top][simbol]
                        if transicio not in accessibles:
                            queue.append(transicio)
                
            Q = [q for q in self.Q if q in accessibles]
            F = [f for f in self.F if f in accessibles]
            TT = {q: self.taulaTransicions[q] for q in accessibles}
            return Q, F, TT
            
        def getAntiimatge(c, A):
            antiimatge = set()
            for q in Q:
                if TT[q][c] in A:
                    antiimatge.add(q)
            return antiimatge
        
        alfabet = self.alfabet
        Q, F, TT = eliminaInaccessibles()
        P = [set(F), set(q for q in Q if q not in F)]
        W = [set(F), set(q for q in Q if q not in F)]
        
        while W:
            A = W.pop()
            for c in alfabet:
                X = getAntiimatge(c, A)
                newP = []
                for Y in P:
                    interseccio = X & Y
                    diff = Y - X
                    if interseccio and diff:
                        newP.extend([interseccio, diff])
                        if Y in W:
                            W.remove(Y)
                            W.extend([interseccio, diff])
                        else:
                            if len(interseccio) <= len(diff):
                                W.append(interseccio)
                            else:
                                W.append(diff)
                    elif Y:
                        newP.append(Y)
                P = newP
        
        blocEstats = {}
        for bloc in P:
            representant = next(iter(bloc))
            for estat in bloc:
                blocEstats[estat] = representant

        QMin = set(blocEstats.values())
        q0Min = blocEstats[self.q0]
        QMin = [q0Min] + sorted(q for q in QMin if q != q0Min)
        FMin = sorted(set(blocEstats[estat] for estat in F))

        TTMin = {}
        for estat in QMin:
            transicions = {}
            for simbol in alfabet:
                transicio = self.taulaTransicions[estat][simbol]
                transicions[simbol] = blocEstats[transicio]
            TTMin[estat] = transicions

        print("\nConjunt quocient: ")
        print(", ".join("{" + ", ".join(sorted(bloc)) + "}" for bloc in sorted(P, key=min)))

        return DFA(alfabet, QMin, TTMin, FMin, q0=q0Min, show=self.show)
        

carrega = "que vols fer? readDFA(r), carregaDFA(c)\n> "
msg = "que vols fer? readDFA(r), carregaDFA(c), guardaDFA(g), displayDFA(d), minimitza(m), sortir(s)\n> "
dfaMinMsg = "vols seguir operant amb el dfa minimitzat? (perdras l'original)\n(y/n) > "
dfa = None

print('\n' + '=' * 60)
while inp := input(carrega).lower():
    if inp == 'r':
        dfa = DFA.makeDFA()
        break
    elif inp == 'c':
        filename = input("nom del fitxer?\n> ")
        dfa = DFA.loadDFA(filename)
        break
    else:
        print("No es una opcio correcta!")
    print('=' * 60)
    
while inp := input(msg).lower():
    if inp == 'r':
        dfa = DFA.makeDFA()
    elif inp == 'c':
        filename = input("nom del fitxer?\n> ")
        dfa = DFA.loadDFA(filename)
    elif inp == 'g':
        filename = input("nom del nou fitxer?\n> ")
        dfa.saveDFA(filename)
    elif inp == 'd':
        dfa.displayDFA()
    elif inp == 'm':
        dfaMin = dfa.minimitza()
        if input(dfaMinMsg).lower() == 'y':
            dfa = dfaMin
    elif inp == 's':
        print("adeuu")
        break
    else:
        print("No es una opcio correcta!")
    
    print('=' * 60)