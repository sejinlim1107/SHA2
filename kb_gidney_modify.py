# 230226 수정
# n=1일 때 문제 생겨서 수정함
from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, Swap, Z, T, Tdag, S, Tdagger
from projectq.backends import CircuitDrawer, ResourceCounter, CommandPrinter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control, Dagger


def logical_and(eng, i, t, c):
    CNOT | (i, c)
    CNOT | (t, c)
    CNOT | (c, i)
    CNOT | (c, t)
    Tdag | i
    Tdag | t
    T | c
    CNOT | (c, i)
    CNOT | (c, t)
    H | c
    S | c

def logical_and_reverse(eng, i, t, c):
    H | c
    Measure | c
    if(int(c)):
        with Control(eng, i):
            Z | t
def Gidney_no_modular_adder(eng, a, b, c, n): # Generic Adder
    for k in range(n):
        H | c[k]
        T | c[k]

    for k in range(n):
        if (k == 0):
            logical_and(eng, a[k], b[k], c[k])

        else:
            CNOT | (c[k - 1], a[k])
            CNOT | (c[k - 1], b[k])
            logical_and(eng, a[k], b[k], c[k])
            CNOT | (c[k - 1], c[k])
            if (k == n - 1):
                CNOT | (c[k - 1], a[k])

    for k in reversed(range(n - 1)):
        if (k == 0):
            logical_and_reverse(eng, a[k], b[k], c[k])

        else:
            CNOT | (c[k - 1], c[k])
            logical_and_reverse(eng, a[k], b[k], c[k])
            CNOT | (c[k - 1], a[k])

    for k in range(n):
        CNOT | (a[k], b[k])


def print_vecotr(eng, element, length):
    if(length==1):
        Measure | element
        print(int(element),end='')

    else:
        All(Measure) | element
        for k in range(length):
            print(int(element[length - 1 - k]), end='')
        print()

def Round_constant_XOR(rc, qubits, n):
    for i in range(n):
        if ((rc >> i) & 1):
            X | qubits[i]

def Gidney_adder(eng, a, b, c, n): # <= 6-bit only (Do not use now)

    for k in range(n-1):
        if(k == 0):
            H | c[k]
            T | c[k]
            logical_and(eng, a[k], b[k], c[k])
            CNOT | (c[k], a[k+1])
            CNOT | (c[k], b[k+1])
        if(k == n-2):
            H | c[k]
            T | c[k]
            logical_and(eng, a[k], b[k], c[k])
            CNOT | (c[k-1], c[k])
            CNOT | (c[k], b[k+1])
        if(k !=0 and k != n-2):
            H | c[k]
            T | c[k]
            logical_and(eng, a[k], b[k], c[k])
            CNOT | (c[k-1], c[k])
            CNOT | (c[k], b[k + 1])
            CNOT | (c[k], a[k + 1])

    for k in reversed(range(n-1)):
        if(k==0):
            logical_and_reverse(eng, a[k], b[k], c[k])
        else:
            CNOT | (c[k-1], c[k])
            logical_and_reverse(eng, a[k], b[k], c[k])
            CNOT | (c[k-1], a[k])
    for k in range(n):
        CNOT | (a[k], b[k])

def Test(eng):
    n = 4  # bit length
    s = eng.allocate_qureg(n)
    k = eng.allocate_qureg(n)
    ancilla = eng.allocate_qureg(n)
    if (resource_check != 1):
        Round_constant_XOR(0b11111, s, n)  # s - k
        Round_constant_XOR(0b10000, k, n)
    Gidney_no_modular_adder(eng,s,k,ancilla,n)

resource_check = 1
Resource = ResourceCounter()
eng = MainEngine(Resource)
Test(eng)
#Gidney_no_modular_adder(eng, k, s, ancilla, n)
print(Resource)
#print_vecotr(eng,ancilla[-1],1)
#print_vecotr(eng,s,n)
#Adder_Test(eng)
eng.flush()