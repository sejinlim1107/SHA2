# https://arxiv.org/pdf/quant-ph/0406142.pdf
# Draper adder

from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, Swap, Z, T, Tdag, S, Tdagger, Sdag
from projectq.backends import CircuitDrawer, ResourceCounter, CommandPrinter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control, Dagger
from math import floor, ceil, log2

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
    elif TD == 2: # Quantum AND (일반 시뮬레이터 사용 시 / ResourceCounter 사용 시)
        if mode:
            quantum_and(eng, a, b, c)
        else:
            quantum_and_dag(eng, a, b, c)
    else: # TD == 0, 분해 안된 버전 사용 (클래식 시뮬레이터 사용 시)
        Toffoli | (a, b, c)

def w(n): # for draper
    return n - sum(int(floor(n / (pow(2, i)))) for i in range(1, int(log2(n)) + 1))

def l(n, t): # for draper
    return int(floor(n / (pow(2, t))))

def outDraper_adder(eng,a,b,n):
    length = n-w(n)-floor(log2(n))
    z = eng.allocate_qureg(n+1) # n+1 크기의 결과 저장소 Z 생성
    ancilla = eng.allocate_qureg(length)  # 논문에서 X라고 지칭되는 ancilla

    # Init round
    for i in range(n):
        toffoli_gate(eng, a[i], b[i], z[i + 1])
    for i in range(1,n):
        CNOT | (a[i], b[i])

    # P-round
    #print("P-rounds")
    idx = 0 # ancilla idx
    tmp = 0 # m=1일 때 idx 저장해두기
    for t in range(1, int(log2(n))):
        pre = tmp  # (t-1)일 때의 첫번째 자리 저장
        for m in range(1, l(n, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(2*m,2*m+1,idx)
                toffoli_gate(eng, b[2 * m], b[2 * m + 1], ancilla[idx])
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                #print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx)
                toffoli_gate(eng, ancilla[pre - 1 + 2 * m], ancilla[pre - 1 + 2 * m + 1], ancilla[idx])
            if m == 1:
                tmp = idx
            idx += 1

    # G-round
    #print("G-rounds")
    pre = 0  # The number of cumulative p(t-1)
    idx = 0  # ancilla idx
    for t in range(1, int(log2(n)) + 1):
        for m in range(l(n, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(int(pow(2, t) * m + pow(2, t - 1)), 2*m+1, int(pow(2, t) * (m + 1)))
                toffoli_gate(eng, z[int(pow(2, t) * m + pow(2, t - 1))], b[2 * m + 1], z[int(pow(2, t) * (m + 1))])
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                #print(int(pow(2, t) * m + pow(2, t - 1)), idx+2*m, int(pow(2, t) * (m + 1)))
                toffoli_gate(eng, z[int(pow(2, t) * m + pow(2, t - 1))], ancilla[idx+2*m], z[int(pow(2, t) * (m + 1))])
        if t != 1:
            pre = pre + l(n, t-1) -1
            idx = pre

    # C-round
    #print("C-rounds")
    if int(log2(n)) - 1 == int(log2(2 * n / 3)): # p(t-1)까지 접근함
        iter = l(n, int(log2(n)) - 1) - 1 # 마지막 pt의 개수
    else: # p(t)까지 접근함
        iter = 0
    pre = 0  # (t-1)일 때의 첫번째 idx
    for t in range(int(log2(2 * n / 3)), 0, -1):
        for m in range(1, l((n - pow(2, t-1)),t)+1):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(int(pow(2, t) * m), 2*m, int(pow(2, t) * m + pow(2, t - 1)))
                toffoli_gate(eng, z[int(pow(2, t) * m)], b[2 * m], z[int(pow(2, t) * m + pow(2, t - 1))])
            else:
                if m==1:
                    iter += l(n, t - 1) - 1
                    pre = length - 1 - iter
                #print(int(pow(2, t) * m),pre + 2 * m,int(pow(2, t) * m + pow(2, t-1)))
                toffoli_gate(eng, z[int(pow(2, t) * m)],
                             ancilla[pre + 2 * m], z[int(pow(2, t) * m + pow(2, t-1))])

    # P-inverse round
    #print("P-inv-rounds")
    pre = 0  # (t-1)일 때의 첫번째 idx
    iter = l(n, int(log2(n)) - 1) - 1  # 마지막 pt의 개수
    iter2 = 0 # for idx
    idx = 0
    for t in reversed(range(1, int(log2(n)))):
        for m in range(1, l(n, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(2*m,2*m+1,m-t)
                toffoli_gate(eng, b[2 * m], b[2 * m + 1], ancilla[m - t])
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                if m == 1:
                    iter += l(n, t - 1) - 1  # p(t-1) last idx
                    pre = length - iter
                    iter2 += (l(n, t) - 1)
                    idx = length - iter2
                #print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx-1+m)
                toffoli_gate(eng, ancilla[pre - 1 + 2 * m], ancilla[pre - 1 + 2 * m + 1], ancilla[idx-1+m])

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
    ancilla2 = eng.allocate_qureg(length) # 논문에서 X라고 지칭되는 ancilla

    if n==1:
        toffoli_gate(eng,a[0],b[0],ancilla1[0])
        CNOT | (a[0],b[0])

        result = []
        result.append(b[0])
        result.append(ancilla1[0])

        return result

    # Init round
    for i in range(n):
        toffoli_gate(eng, a[i], b[i], ancilla1[i]) # ancilla1[0] == Z[1]
    for i in range(n):
        CNOT | (a[i], b[i])

    # P-round
    #print("P-rounds")
    idx = 0  # ancilla idx
    tmp = 0  # m=1일 때 idx 저장해두기
    for t in range(1, int(log2(n))):
        pre = tmp  # (t-1)일 때의 첫번째 자리 저장
        #print("t ========== ",t)
        for m in range(1, l(n, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(eng, b[2 * m], b[2 * m + 1], ancilla2[idx])
                #print(2*m,2*m+1,idx)
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                toffoli_gate(eng, ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx])
                #print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx)
            if m == 1:
                tmp = idx
            idx += 1

    # G-round
    #print("G-rounds")
    pre = 0  # The number of cumulative p(t-1)
    idx = 0  # ancilla idx
    for t in range(1, int(log2(n)) + 1):
        #print("t = ",t)
        for m in range(l(n, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(eng,ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], b[2 * m + 1],
                             ancilla1[int(pow(2, t) * (m + 1)) - 1])
                #print(int(pow(2, t) * m + pow(2, t - 1)) - 1,2 * m + 1,int(pow(2, t) * (m + 1)) - 1)
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                #print(int(pow(2, t) * m + pow(2, t - 1)) - 1,idx+2*m,int(pow(2, t) * (m + 1)) - 1)
                toffoli_gate(eng,ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[idx+2*m],
                             ancilla1[int(pow(2, t) * (m + 1)) - 1])
        if t != 1:
            pre = pre + l(n, t - 1) - 1
            idx = pre

    # C-round
    #print("C-rounds")
    if int(log2(n)) - 1 == int(log2(2 * n / 3)): # p(t-1)까지 접근함
        iter = l(n, int(log2(n)) - 1) - 1 # 마지막 pt의 개수
    else: # p(t)까지 접근함
        iter = 0
    pre = 0  # (t-1)일 때의 첫번째 idx
    for t in range(int(log2(2 * n / 3)), 0, -1):
        #print("t=",t)
        for m in range(1, l((n - pow(2, t - 1)), t) + 1):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(eng,ancilla1[int(pow(2, t) * m) - 1], b[2 * m],
                             ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
                #print(int(pow(2, t) * m) - 1,2 * m,int(pow(2, t) * m + pow(2, t - 1)) - 1)
            else:
                if m==1:
                    iter += l(n, t - 1) - 1
                    pre = length - 1 - iter
                toffoli_gate(eng,ancilla1[int(pow(2, t) * m) - 1],
                             ancilla2[pre + 2 * m],ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
                #print(int(pow(2, t) * m) - 1,pre + 2 * m,int(pow(2, t) * m + pow(2, t - 1)) - 1)

    # P-inverse round
    #print("P-inverse round")
    pre = 0  # (t-1)일 때의 첫번째 idx
    iter = l(n, int(log2(n)) - 1) - 1  # 마지막 pt의 개수
    iter2 = 0  # for idx
    idx = 0
    for t in reversed(range(1, int(log2(n)))):
        for m in range(1, l(n, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(eng, b[2 * m], b[2 * m + 1], ancilla2[m - t])
                #print(2*m, 2*m+1, m-t)
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                if m == 1:
                    iter += l(n, t - 1) - 1  # p(t-1) last idx
                    pre = length - iter
                    iter2 += (l(n, t) - 1)
                    idx = length - iter2
                toffoli_gate(eng, ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx-1+m])
                #print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx-1+m)


    # mid round
    for i in range(1, n):
        CNOT | (ancilla1[i - 1], b[i])
    for i in range(n-1):
        X | b[i]
    for i in range(1, n-1):
        CNOT | (a[i], b[i])

    ### Step 7. Section3 in reverse. (n-1)bit adder ###

    # P-round reverse
    #print("P-round reverse")
    iter = 0
    pre = 0 # (t-1)일 때의 첫번째 자리 저장
    idx = 0  # ancilla idx

    for t in range(1, int(log2(n-1))):
        if t > 1:
            pre = iter
            iter += l(n, t - 1) - 1 # ancilla idx. n is right.
            idx = iter
        #print("t ========== ", t)
        for m in range(1, l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(2 * m, 2 * m + 1, idx)
                toffoli_gate(eng, b[2 * m], b[2 * m + 1], ancilla2[idx])
                idx += 1
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                #print(pre - 1 + 2 * m, pre - 1 + 2 * m + 1, idx)
                toffoli_gate(eng, ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx])
                idx += 1

    # C-round reverse
    #print("C-inv-rounds")
    pre = 0  # 이전 p(t) 개수
    for t in reversed(range(int(log2(2 * (n - 1) / 3)), 0, -1)):
        idx = pre # ancilla2 idx
        #print("t = ", t)
        for m in range(1, l(((n - 1) - pow(2, t - 1)), t) + 1):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(int(pow(2, t) * m) - 1, 2 * m, int(pow(2, t) * m + pow(2, t - 1)) - 1)
                toffoli_gate(eng, ancilla1[int(pow(2, t) * m) - 1], b[2 * m],
                             ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
            else:
                #print(int(pow(2, t) * m) - 1, idx - 1 + 2 * m, int(pow(2, t) * m + pow(2, t - 1)) - 1)
                toffoli_gate(eng, ancilla1[int(pow(2, t) * m) - 1],
                             ancilla2[idx-1+ 2 * m], ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
                if m == 1:
                    pre += l(n, t-1) -1

    # G-round reverse
    #print("G-inv-rounds")
    pre = 0  # (t-1)일 때의 첫번째 idx
    idx_t = int(log2(n)) # n-1이 아니라 n일 때의 t의 범위
    if int(log2(n)) != int(log2(n - 1)):  # n-1일 때와 n일 때의 t가 차이가 있을 때
        iter = l(n, idx_t-1) - 1 # 마지막 pt의 개수
        idx_t -= 1
    else:
        iter = 0
    for t in reversed(range(1, int(log2(n-1)) + 1)):
        #print("t=",t)
        for m in range(l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(int(pow(2, t) * m + pow(2, t - 1)) - 1,2 * m + 1,int(pow(2, t) * (m + 1)) - 1)
                toffoli_gate(eng, ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], b[2 * m + 1],
                             ancilla1[int(pow(2, t) * (m + 1)) - 1])
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                if m==0:
                    iter += l(n, idx_t-1) - 1  # p(t-1) last idx
                    pre = length - iter
                    idx_t -= 1

                #print(int(pow(2, t) * m + pow(2, t - 1)) - 1, pre - 1 + 2 * m + 1, int(pow(2, t) * (m + 1)) - 1)
                toffoli_gate(eng, ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[pre - 1 + 2 * m + 1],
                             ancilla1[int(pow(2, t) * (m + 1)) - 1])

    # P-inverse round reverse
    #print("P-inverse round reverse")
    pre = 0  # (t-1)일 때의 첫번째 idx
    idx_t = int(log2(n))-1 # n-1이 아니라 n일 때의 t의 범위
    if int(log2(n)) != int(log2(n-1)): # n-1일 때와 n일 때의 t가 차이가 있을 때
        iter = l(n, idx_t) - 1 + l(n, idx_t-1) - 1 # 마지막 pt의 개수
        iter2 = l(n, idx_t) - 1
        idx_t -= 1
    else:
        iter = l(n, idx_t) - 1
        iter2 = 0  # for idx
    for t in reversed(range(1, int(log2(n-1)))):
        #print("t=",t)
        for m in range(1, l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(eng, b[2 * m], b[2 * m + 1], ancilla2[m - t])
                #print(2*m,2*m+1,m-t)
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                if m == 1:
                    iter += l(n, idx_t-1) - 1  # p(t-1) last idx
                    pre = length - iter
                    iter2 += l(n, idx_t) - 1
                    idx = length - iter2
                    idx_t -= 1
                toffoli_gate(eng, ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx-1+m])
                #print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx-1+m)


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
    sum = outDraper_adder(eng,a,b,n)

    if (resource_check == 0):
        length = n - w(n) - floor(log2(n))
        print('Add result : ', end='')
        print_vector(eng, sum, n+1)


n = 10
a = 0b111111111
b = 0b111111111

'''
TD = 0
resource_check = 0
Resource = ClassicalSimulator()
eng = MainEngine(Resource)

# for AND gate Test Engine
# eng = MainEngine()

adder_test(eng,a,b,n)
eng.flush()
print()
'''

TD = 0
resource_check = 1

Resource = ResourceCounter()
eng = MainEngine(Resource)
#eng = MainEngine()
adder_test(eng,a,b,n)
print(Resource)
eng.flush()

'''
drawing_engine = CircuitDrawer()
eng = MainEngine(drawing_engine)
eng.flush()
print(drawing_engine.get_latex())
'''


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