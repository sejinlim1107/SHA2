# https://arxiv.org/pdf/quant-ph/0406142.pdf
# Draper adder

from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, Swap, Z, T, Tdag, S, Tdagger, Sdag
from projectq.backends import CircuitDrawer, ResourceCounter, CommandPrinter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control, Dagger
from math import floor, ceil, log10, log2

def quantum_and(eng, a, b, c):
    ancilla = eng.allocate_qubit()
    H | c
    CNOT | (b, ancilla)
    CNOT | (c, a)
    CNOT | (c, b)
    CNOT | (a, ancilla)
    Tdag | a
    Tdag | b
    T | c
    T | ancilla
    CNOT | (a, ancilla)
    CNOT | (c, b)
    CNOT | (c, a)
    CNOT | (b, ancilla)
    H | c
    S | c

def quantum_and_dag(eng, a, b, c):
    H | c
    Measure | c
    if(int(c)):
        S | a
        S | b
        X | c
        CNOT | (a,b)
        Sdag | b
        CNOT | (a,b)

def toffoli_gate(eng, a, b, c, mode=True):
    if(resource_check ==1):
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
    elif resource_check == "quantum_AND":
        if mode:
            quantum_and(eng, a, b, c)
        else:
            quantum_and_dag(eng, a, b, c)
    else:
        Toffoli | (a, b, c)

def w(n): # for draper
    return n - sum(int(floor(n / (pow(2, i)))) for i in range(1, int(log2(n)) + 1))

def l(n, t): # for draper
    return int(floor(n / (pow(2, t))))

def outDraper_adder(eng, a,b,n):
    length = n-w(n)-floor(log2(n))
    z = eng.allocate_qureg(n+1) # n+1 크기의 결과 저장소 Z 생성
    ancillae = eng.allocate_qureg(length)  # 논문에서 X라고 지칭되는 ancilla

    # Init round
    for i in range(n):
        toffoli_gate(eng, a[i], b[i], z[i + 1])
    for i in range(1,n):
        CNOT | (a[i], b[i])

    # P-round
    idx = 0  # ancilla idx
    pre = 0  # 이전 t-1일 때의 [1]의 상대적 위치.

    for t in range(1, int(log2(n))):
        for m in range(1, l(n, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(eng, b[2 * m], b[2 * m + 1], ancillae[idx])
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                toffoli_gate(eng, ancillae[pre - 1 + 2 * m], ancillae[pre - 1 + 2 * m + 1], ancillae[idx])
                # toffoli_gate(eng, ancillae[idx-l(n,t-1)+2*m], ancillae[idx-l(n,t-1)+2*m+1], ancillae[idx]))
                # 이건 절대적 위치 계산한 식임. 이것도 제대로 동작하긴 함.
            if m == 1:  # 여기 위치가 맞음. t==1일 때 이 if문을 통과하면서 저장할 것임. (t-1) for문의 m=1을 저장하는게 목표.
                pre = idx
            idx += 1

    # G-round
    pre = 0
    for t in range(1, int(log2(n)) + 1):
        for m in range(l(n, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(int(pow(2, t)*m + pow(2, t-1)),2 * m + 1,int(pow(2, t)*(m+1)))
                toffoli_gate(eng, z[int(pow(2, t) * m + pow(2, t - 1))], b[2 * m + 1], z[int(pow(2, t) * (m + 1))])
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                idx = pre - 1 + 2 * m + 1
                #print(int(pow(2, t) * m + pow(2, t - 1)), idx, int(pow(2, t) * (m + 1)))
                toffoli_gate(eng, z[int(pow(2, t) * m + pow(2, t - 1))], ancillae[idx], z[int(pow(2, t) * (m + 1))])
        if t > 1:
            pre = idx + 1

    # C-round
    tmp = 0
    for t in range(int(log2(2 * n / 3)), 0, -1):
        for m in range(1, l((n - pow(2, t-1)),t)+1):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(eng, z[int(pow(2, t) * m)], b[2 * m], z[int(pow(2, t) * m + pow(2, t - 1))])
            else:
                toffoli_gate(eng, z[int(pow(2, t) * m)],
                             ancillae[len(ancillae)-1-l(n,t)-1+2*m], z[int(pow(2, t) * m + pow(2, t-1))])

    # P-inverse round
    idx = 0  # ancilla idx
    pre = 0  # 이전 t-1일 때의 [1]의 상대적 위치.

    for t in reversed(range(1, int(log2(n)))):
        for m in range(1, l(n, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(eng, b[2 * m], b[2 * m + 1], ancillae[idx],False)
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                toffoli_gate(eng, ancillae[pre - 1 + 2 * m], ancillae[pre - 1 + 2 * m + 1], ancillae[idx],False)
                # toffoli_gate(eng, ancillae[idx-l(n,t-1)+2*m], ancillae[idx-l(n,t-1)+2*m+1], ancillae[idx]))
                # 이건 절대적 위치 계산한 식임. 이것도 제대로 동작하긴 함.
            if m == 1:  # 여기 위치가 맞음. t==1일 때 이 if문을 통과하면서 저장할 것임. (t-1) for문의 m=1을 저장하는게 목표.
                pre = idx
            idx += 1

    # Last round
    for i in range(n):
        CNOT | (b[i], z[i])
    CNOT | (a[0], z[0])
    for i in range(1, n):
        CNOT | (a[i], b[i])

    return z

def inDraper_adder(eng, a,b,n):
    length = n-w(n)-floor(log2(n))
    ancilla1 = eng.allocate_qureg(n) # z[1] ~ z[n] 저장
    ancilla2 = eng.allocate_qureg(length)  # 논문에서 X라고 지칭되는 ancilla

    # Init round
    for i in range(n):
        toffoli_gate(eng, a[i], b[i], ancilla1[i]) # ancilla1[0] == Z[1]
    for i in range(n):
        CNOT | (a[i], b[i])

    # P-round
    idx = 0  # ancilla idx
    pre = 0  # 이전 t-1일 때의 [1]의 상대적 위치.
    for t in range(1, int(log2(n))):
        for m in range(1, l(n, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(eng, b[2 * m], b[2 * m + 1], ancilla2[idx])
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                toffoli_gate(eng, ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx])
                # 이건 절대적 위치 계산한 식임. 이것도 제대로 동작하긴 함.
            if m == 1:  # 여기 위치가 맞음. t==1일 때 이 if문을 통과하면서 저장할 것임. (t-1) for문의 m=1을 저장하는게 목표.
                pre = idx
            idx += 1

    # G-round
    pre = 0
    for t in range(1, int(log2(n)) + 1):
        for m in range(l(n, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                # print(int(mt.pow(2, t)*m + mt.pow(2, t-1)-1),2 * m + 1,int(mt.pow(2, t)*(m+1))-1)
                toffoli_gate(eng,ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], b[2 * m + 1],
                             ancilla1[int(pow(2, t) * (m + 1)) - 1])
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                idx = pre - 1 + 2 * m + 1
                # print(int(mt.pow(2, t)*m + mt.pow(2, t-1))-1,idx,int(mt.pow(2, t)*(m+1))-1)
                toffoli_gate(eng,ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[idx],
                             ancilla1[int(pow(2, t) * (m + 1)) - 1])
        if t > 1:
            pre = idx + 1

    # C-round
    for t in range(int(log2(2 * n / 3)), 0, -1):
        for m in range(1, l((n - pow(2, t - 1)), t) + 1):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(eng,ancilla1[int(pow(2, t) * m) - 1], b[2 * m],
                             ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
            else:
                toffoli_gate(eng,ancilla1[int(pow(2, t) * m) - 1],
                             ancilla2[len(ancilla2) - 1 - l(n, t) - 1 + 2 * m],
                             ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])

    # P-inverse round
    idx = 0  # ancilla idx
    pre = 0  # 이전 t-1일 때의 [1]의 상대적 위치.
    for t in reversed(range(1, int(log2(n)))):
        for m in range(1, l(n, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(eng, b[2 * m], b[2 * m + 1], ancilla2[idx], False)
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                toffoli_gate(eng, ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx], False)
                # 이건 절대적 위치 계산한 식임. 이것도 제대로 동작하긴 함.
            if m == 1:  # 여기 위치가 맞음. t==1일 때 이 if문을 통과하면서 저장할 것임. (t-1) for문의 m=1을 저장하는게 목표.
                pre = idx
            idx += 1

    # Last round
    for i in range(1, n):
        CNOT | (ancilla1[i - 1], b[i])
    for i in range(n-1):
        X | b[i]
    for i in range(1, n-1):
        CNOT | (a[i], b[i])

    ### Step 7. Section3 in reverse. (n-1)bit adder ###

    # P-round reverse
    idx = 0  # ancilla idx
    pre = 0  # 이전 t-1일 때의 [1]의 상대적 위치.
    for t in range(1, int(log2(n-1))):
        for m in range(1, l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(eng, b[2 * m], b[2 * m + 1], ancilla2[idx], False)
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                toffoli_gate(eng, ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx], False)
                # 이건 절대적 위치 계산한 식임. 이것도 제대로 동작하긴 함.
            if m == 1:  # 여기 위치가 맞음. t==1일 때 이 if문을 통과하면서 저장할 것임. (t-1) for문의 m=1을 저장하는게 목표.
                pre = idx
            idx += 1

    # C-round reverse
    for t in range(int(log2(2 * (n-1) / 3)), 0, -1):
        for m in range(1, l(((n-1) - pow(2, t - 1)), t) + 1):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(eng, ancilla1[int(pow(2, t) * m) - 1], b[2 * m],
                             ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], False)
            else:
                toffoli_gate(eng, ancilla1[int(pow(2, t) * m) - 1],
                             ancilla2[len(ancilla2) - 1 - l(n, t) - 1 + 2 * m],
                             ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], False)

    # G-round reverse
    pre = 0
    for t in range(1, int(log2(n-1)) + 1):
        for m in range(l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                # print(int(mt.pow(2, t)*m + mt.pow(2, t-1)-1),2 * m + 1,int(mt.pow(2, t)*(m+1))-1)
                toffoli_gate(eng, ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], b[2 * m + 1],
                             ancilla1[int(pow(2, t) * (m + 1)) - 1], False)
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                idx = pre - 1 + 2 * m + 1
                # print(int(mt.pow(2, t)*m + mt.pow(2, t-1))-1,idx,int(mt.pow(2, t)*(m+1))-1)
                toffoli_gate(eng, ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[idx],
                             ancilla1[int(pow(2, t) * (m + 1)) - 1], False)
        if t > 1:
            pre = idx + 1

    # P-inverse round reverse
    idx = 0  # ancilla idx
    pre = 0  # 이전 t-1일 때의 [1]의 상대적 위치.
    for t in reversed(range(1, int(log2(n-1)))):
        for m in range(1, l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(eng, b[2 * m], b[2 * m + 1], ancilla2[idx], False)
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                toffoli_gate(eng, ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx], False)
                # 이건 절대적 위치 계산한 식임. 이것도 제대로 동작하긴 함.
            if m == 1:  # 여기 위치가 맞음. t==1일 때 이 if문을 통과하면서 저장할 것임. (t-1) for문의 m=1을 저장하는게 목표.
                pre = idx
            idx += 1

    # real last
    for i in range(1,n-1):
        CNOT | (a[i], b[i])
    for i in range(n-1):
        toffoli_gate(eng, a[i], b[i], ancilla1[i], False)
    for i in range(n-1):
        X | b[i]

    result = []
    for k in b:
        result.append(k)
    result.append(ancilla1[-1])

    return result

def print_vector(eng, element, length):
    All(Measure) | element
    for k in range(length):
        print(int(element[length-1-k]), end='')
    print()

def round_constant_XOR(rc, qubits, n):
    for i in range(n):
        if ((rc >> i) & 1):
            X | qubits[i]

def adder_test(eng, A, B, n):
    a = eng.allocate_qureg(n)
    b = eng.allocate_qureg(n)

    if (resource_check == 0):
        round_constant_XOR(A, a, n)
        round_constant_XOR(B, b, n)

    if (resource_check == 0):
        print('a: ', end='')
        print_vector(eng, a, n)
        print('b: ', end='')
        print_vector(eng, b, n)

    #sum = outDraper_adder(eng,a,b,n)
    sum = inDraper_adder(eng,a,b,n)

    if (resource_check == 0):
        print('Add result : ', end='')
        print_vector(eng, sum, n+1)


n = 7
a = 0b1010101
b = 0b0101010

resource_check = 0
Resource = ClassicalSimulator()
eng = MainEngine(Resource)

# for AND gate Test Engine
# eng = MainEngine()

adder_test(eng,a,b,n)
eng.flush()
print()

resource_check = "quantum_AND"

Resource = ResourceCounter()
eng = MainEngine(Resource)
adder_test(eng,a,b,n)
print(Resource)
eng.flush()

'''
# AND gate Test
eng = MainEngine()
n = 1 # bit length

a = eng.allocate_qubit()
b = eng.allocate_qubit()
c = eng.allocate_qubit()

round_constant_XOR(1, a, n)
round_constant_XOR(1, b, n)
round_constant_XOR(0, c, n)

print_vector(eng,a,n)
print_vector(eng,b,n)
print_vector(eng,c,n)

quantum_and(eng,a,b,c)

print_vector(eng,a,n)
print_vector(eng,b,n)
print_vector(eng,c,n)

quantum_and_dag(eng,a,b,c)

print_vector(eng,a,n)
print_vector(eng,b,n)
print_vector(eng,c,n)

eng.flush()
'''