from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, Swap, Z, T, Tdag, S, Tdagger, Sdag
from projectq.backends import CircuitDrawer, ResourceCounter, CommandPrinter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control, Dagger
from math import floor, ceil, log2

def toffoli_gate(a, b, c):
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

def w(n): # for draper
    return n - sum(int(floor(n / (pow(2, i)))) for i in range(1, int(log2(n)) + 1))

def l(n, t): # for draper
    return int(floor(n / (pow(2, t))))

def outDraper(eng,a,b,z,n):
    length = n-1-w(n-1)-floor(log2(n-1))
    ancilla = eng.allocate_qureg(length)  # 논문에서 X라고 지칭되는 ancilla

    # Init round
    for i in range(n-1):
        toffoli_gate(a[i], b[i], z[i + 1])
    for i in range(1,n-1):
        CNOT | (a[i], b[i])
    CNOT | (a[n-1], z[n-1])
    CNOT | (b[n-1], z[n-1])

    # P-round
    #print("P-rounds")
    idx = 0 # ancilla idx
    tmp = 0 # m=1일 때 idx 저장해두기
    for t in range(1, int(log2(n-1))):
        pre = tmp  # (t-1)일 때의 첫번째 자리 저장
        for m in range(1, l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(2*m,2*m+1,idx)
                toffoli_gate(b[2 * m], b[2 * m + 1], ancilla[idx])
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                #print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx)
                toffoli_gate(ancilla[pre - 1 + 2 * m], ancilla[pre - 1 + 2 * m + 1], ancilla[idx])
            if m == 1:
                tmp = idx
            idx += 1

    # G-round
    #print("G-rounds")
    pre = 0  # The number of cumulative p(t-1)
    idx = 0  # ancilla idx
    for t in range(1, int(log2(n-1)) + 1):
        for m in range(l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(int(pow(2, t) * m + pow(2, t - 1)), 2*m+1, int(pow(2, t) * (m + 1)))
                toffoli_gate(z[int(pow(2, t) * m + pow(2, t - 1))], b[2 * m + 1], z[int(pow(2, t) * (m + 1))])
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                #print(int(pow(2, t) * m + pow(2, t - 1)), idx+2*m, int(pow(2, t) * (m + 1)))
                toffoli_gate(z[int(pow(2, t) * m + pow(2, t - 1))], ancilla[idx+2*m], z[int(pow(2, t) * (m + 1))])
        if t != 1:
            pre = pre + l(n-1, t-1) -1
            idx = pre

    # C-round
    #print("C-rounds")
    if int(log2(n-1)) - 1 == int(log2(2 * (n-1) / 3)): # p(t-1)까지 접근함
        iter = l(n-1, int(log2(n-1)) - 1) - 1 # 마지막 pt의 개수
    else: # p(t)까지 접근함
        iter = 0
    pre = 0  # (t-1)일 때의 첫번째 idx
    for t in range(int(log2(2 * (n-1) / 3)), 0, -1):
        for m in range(1, l((n-1 - pow(2, t-1)),t)+1):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(int(pow(2, t) * m), 2*m, int(pow(2, t) * m + pow(2, t - 1)))
                toffoli_gate(z[int(pow(2, t) * m)], b[2 * m], z[int(pow(2, t) * m + pow(2, t - 1))])
            else:
                if m==1:
                    iter += l(n-1, t - 1) - 1
                    pre = length - 1 - iter
                #print(int(pow(2, t) * m),pre + 2 * m,int(pow(2, t) * m + pow(2, t-1)))
                toffoli_gate(z[int(pow(2, t) * m)],
                             ancilla[pre + 2 * m], z[int(pow(2, t) * m + pow(2, t-1))])

    # P-inverse round
    #print("P-inv-rounds")
    pre = 0  # (t-1)일 때의 첫번째 idx
    iter = l(n-1, int(log2(n-1)) - 1) - 1  # 마지막 pt의 개수
    iter2 = 0 # for idx
    idx = 0
    for t in reversed(range(1, int(log2(n-1)))):
        for m in range(1, l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(2*m,2*m+1,m-t)
                toffoli_gate(b[2 * m], b[2 * m + 1], ancilla[m - t])
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                if m == 1:
                    iter += l(n-1, t - 1) - 1  # p(t-1) last idx
                    pre = length - iter
                    iter2 += (l(n-1, t) - 1)
                    idx = length - iter2
                #print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx-1+m)
                toffoli_gate(ancilla[pre - 1 + 2 * m], ancilla[pre - 1 + 2 * m + 1], ancilla[idx-1+m])

    # Last round
    for i in range(n-1):
        CNOT | (b[i], z[i])
    CNOT | (a[0], z[0])
    for i in range(1, n-1):
        CNOT | (a[i], b[i])

    return z # SHA에서는 안씀

def adder_test(eng, A, B, n):
    a = eng.allocate_qureg(n)
    b = eng.allocate_qureg(n)
    z = eng.allocate_qureg(n)
    if (resource_check == 0):
        round_constant_XOR(A, a, n)
        round_constant_XOR(B, b, n)

    if (resource_check == 0):
        print('a: ', end='')
        print_vector(a, n)
        print('b: ', end='')
        print_vector(b, n)

    sum = outDraper(eng,a,b,z,n)

    if (resource_check == 0):
        print('Add result : ', end='')
        print_vector(sum, n)

def round_constant_XOR(rc, qubits, n):
    for i in range(n):
        if ((rc >> i) & 1):
            X | qubits[i]

def print_vector(element, length):
    All(Measure) | element
    for k in range(length):
        print(int(element[length-1-k]), end='')
    print()

n = 10
a = 0b1111100000
b = 0b0000011111

TD = 0
resource_check = 0

Resource = ClassicalSimulator()
#Resource = ResourceCounter()
eng = MainEngine(Resource)
#eng = MainEngine()
adder_test(eng,a,b,n)
#print(Resource)
eng.flush()