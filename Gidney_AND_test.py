# projectQ로 했던 것

from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, Swap, Z, T, Tdag, S, Tdagger
from projectq.backends import CircuitDrawer, ResourceCounter, CommandPrinter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control, Dagger
from math import floor, ceil, log10, log2

def MAJ(eng,a,b,c):
    CNOT | (a, b)
    CNOT | (a, c)
    Toffoli_gate(eng, c, b, a)

def UMA(eng,a,b,c):
    Toffoli_gate(eng, c, b, a)
    CNOT | (c, b)
    CNOT | (a, c)

def logical_and(eng, i, t, c):
    H | c
    T | c
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

def Round_constant_XOR(rc, qubits, n):
    for i in range(n):
        if ((rc >> i) & 1):
            X | qubits[i]

def Toffoli_gate(eng, a, b, c):
    if(TD == 1): # 분해 버전 (일반 시뮬레이터 사용 시 / ResourceCounter 사용 시)
        Tdag | a
        Tdag | b
        H | c
        CNOT | (c, a)
        T | a
        CNOT | (b, c)
        CNOT | (b, a)
        T | c
        Tdag | a
        CNOT | (b, c)
        CNOT | (c, a)
        T | a
        Tdag | c
        CNOT | (b, a)
        H | c

    else: # TD == 0, 분해 안된 버전 사용 (클래식 시뮬레이터 사용 시)
        Toffoli | (a, b, c)

def Gidney_no_modular_adder(eng, a, b, c, carry, n):

    for k in range(n):
        if(k == 0):
            logical_and(eng, a[k], b[k], c[k])

        if(k != 0):
            CNOT | (c[k-1], a[k])
            CNOT | (c[k-1], b[k])
            if(k!= n-1):
                logical_and(eng, a[k], b[k], c[k])
                CNOT | (c[k-1], c[k])
            else:
                logical_and(eng, a[k], b[k], carry)
                CNOT | (c[k - 1], carry)

        if (k == n-1):
            CNOT | (c[k-1], a[k])

    for k in reversed(range(n-1)):
        if(k==0):
            logical_and_reverse(eng, a[k], b[k], c[k])

        else:
            CNOT | (c[k-1], c[k])
            logical_and_reverse(eng, a[k], b[k], c[k])
            CNOT | (c[k-1], a[k])

    for k in range(n):
        CNOT | (a[k], b[k])

def Gidney_adder(eng, a, b, c, n): # <= 6-bit only (Do not use now)
    for k in range(n-1):
        if(k == 0):
            logical_and(eng, a[k], b[k], c[k])
            CNOT | (c[k], a[k+1])
            CNOT | (c[k], b[k+1])
        if(k == n-2):
            logical_and(eng, a[k], b[k], c[k])
            CNOT | (c[k-1], c[k])
            CNOT | (c[k], b[k+1])
        if(k !=0 and k != n-2):
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
def print_vecotr(eng, element, length):
    All(Measure) | element
    for k in range(length):
        print(int(element[length - 1 - k]), end='')
    print()

def AND_Test(eng):
    n = 1 # bit length
    s = eng.allocate_qureg(n)
    k = eng.allocate_qureg(n)
    ancilla = eng.allocate_qureg(n)

    if(resource_check != 1):
        Round_constant_XOR(0b1, s, n) # s - k
        Round_constant_XOR(0b1, k, n)

    print('s: ', end='')
    print_vecotr(eng, s, n)
    print('k: ', end='')
    print_vecotr(eng, k, n)
    print('c: ', end='')
    print_vecotr(eng, ancilla, n)
    logical_and(eng,s,k,ancilla)
    print('after AND')
    print('s: ', end='')
    print_vecotr(eng, s, n)
    print('k: ', end='')
    print_vecotr(eng, k, n)
    print('c: ', end='')
    print_vecotr(eng, ancilla, n)
    logical_and_reverse(eng,s,k,ancilla)
    print('after reverse_AND')
    print('s: ', end='')
    print_vecotr(eng, s, n)
    print('k: ', end='')
    print_vecotr(eng, k, n)
    print('c: ', end='')
    print_vecotr(eng, ancilla, n)

    logical_and(eng,s,k,ancilla)
    print('one more AND')
    print('s: ', end='')
    print_vecotr(eng, s, n)
    print('k: ', end='')
    print_vecotr(eng, k, n)
    print('c: ', end='')
    print_vecotr(eng, ancilla, n)


resource_check = 0
TD = 1

'''
Resource = ClassicalSimulator()
eng = MainEngine(Resource)
Adder_Test(eng)
eng.flush()
'''


#### For Gidney Adder Test####
eng = MainEngine()
AND_Test(eng)
#Adder_Test(eng)
eng.flush()
#
#
# print()
# resource_check = 1
# NCT = 0
# s_minus_k = 1
# parallel = 1
#
# Resource = ResourceCounter()
# eng = MainEngine(Resource)
# Gidney_adder(eng, k, s, ancilla, n)
# #Adder_Test(eng)
#
# print(Resource)
# eng.flush()
