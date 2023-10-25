from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, Swap, Z, T, Tdag, S, Tdagger, Sdag
from projectq.backends import CircuitDrawer, ResourceCounter, CommandPrinter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control, Dagger
from math import floor, ceil, log2

def quantum_and(a, b, c, ancilla):
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

def quantum_and_dag(a, b, c):
    H | b
    H | c
    Measure | c
    if(int(c) or resource_check == 1):
        CNOT | (a,b)
        X | c
    H | b

def toffoli_gate(a, b, c, ancilla = 0, mode=True):

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
    elif (TD == 2):
        if mode:
            quantum_and(a,b,c,ancilla)
        else:
            quantum_and_dag(a,b,c)
    else: # TD == 0, 분해 안된 버전 사용 (클래식 시뮬레이터 사용 시)
        Toffoli | (a, b, c)

def takahashi(a,b,n): # modular adder

    for i in range(1,n):
        CNOT | (a[i], b[i])

    for i in range(n-2,0,-1):
        CNOT | (a[i], a[i+1])

    for i in range(n-1):
        toffoli_gate(a[i], b[i], a[i+1])

    for i in range(n-1,0,-1):
        CNOT | (a[i], b[i])
        toffoli_gate(b[i-1], a[i-1], a[i])

    for i in range(1,n-1):
        CNOT | (a[i], a[i+1])

    for i in range(n):
        CNOT | (a[i], b[i])

def w(n): # for draper
    return n - sum(int(floor(n / (pow(2, i)))) for i in range(1, int(log2(n)) + 1))

def l(n, t): # for draper
    return int(floor(n / (pow(2, t))))

def outDraper(a,b,z,ancillas,n):
    length = n-1-w(n-1)-floor(log2(n-1))
    #ancilla = eng.allocate_qureg(length)  # 논문에서 X라고 지칭되는 ancilla
    ancilla = ancillas[:length]
    and_len = n-1
    #and_ancilla = eng.allocate_qureg(and_len)
    and_ancilla = ancillas[length:length+n-1]
    and_idx = 0
    tmp_len = (n-1)-w(n-1)
    #tmp_ancilla = eng.allocate_qureg(tmp_len)
    tmp_ancilla = ancillas[length+n-1:]
    tmp_idx = 0

    # Init round
    for i in range(n-1):
        toffoli_gate(a[i], b[i], z[i + 1], and_ancilla[and_idx]) # and
        and_idx += 1
    for i in range(1,n-1):
        CNOT | (a[i], b[i])
    CNOT | (a[n-1], z[n-1])
    CNOT | (b[n-1], z[n-1])

    # P-round
    #print("P-rounds")
    idx = 0 # ancilla idx
    tmp = 0 # m=1일 때 idx 저장해두기
    and_idx = 0
    for t in range(1, int(log2(n-1))):
        pre = tmp  # (t-1)일 때의 첫번째 자리 저장
        for m in range(1, l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(2*m,2*m+1,idx)
                toffoli_gate(b[2 * m], b[2 * m + 1], ancilla[idx], and_ancilla[and_idx]) # and
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                #print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx)
                toffoli_gate(ancilla[pre - 1 + 2 * m], ancilla[pre - 1 + 2 * m + 1], ancilla[idx], and_ancilla[and_idx]) # and
            if m == 1:
                tmp = idx
            idx += 1
            and_idx += 1

    # G-round
    #print("G-rounds")
    pre = 0  # The number of cumulative p(t-1)
    idx = 0  # ancilla idx
    for t in range(1, int(log2(n-1)) + 1):
        for m in range(l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(int(pow(2, t) * m + pow(2, t - 1)), 2*m+1, int(pow(2, t) * (m + 1)))
                toffoli_gate(z[int(pow(2, t) * m + pow(2, t - 1))], b[2 * m + 1], tmp_ancilla[tmp_idx], and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx], z[int(pow(2, t) * (m + 1))])
                toffoli_gate(z[int(pow(2, t) * m + pow(2, t - 1))], b[2 * m + 1], tmp_ancilla[tmp_idx], and_ancilla[and_idx], False)

            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                #print(int(pow(2, t) * m + pow(2, t - 1)), idx+2*m, int(pow(2, t) * (m + 1)))
                #toffoli_gate(z[int(pow(2, t) * m + pow(2, t - 1))], ancilla[idx+2*m], z[int(pow(2, t) * (m + 1))])
                toffoli_gate(z[int(pow(2, t) * m + pow(2, t - 1))], ancilla[idx+2*m], tmp_ancilla[tmp_idx], and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx], z[int(pow(2, t) * (m + 1))])
                toffoli_gate(z[int(pow(2, t) * m + pow(2, t - 1))], ancilla[idx+2*m], tmp_ancilla[tmp_idx], and_ancilla[and_idx], False)
            and_idx = (and_idx+1) % and_len
            tmp_idx += 1
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
    tmp_idx = 0
    for t in range(int(log2(2 * (n-1) / 3)), 0, -1):
        for m in range(1, l((n-1 - pow(2, t-1)),t)+1):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(int(pow(2, t) * m), 2*m, int(pow(2, t) * m + pow(2, t - 1)))
                #toffoli_gate(z[int(pow(2, t) * m)], b[2 * m], z[int(pow(2, t) * m + pow(2, t - 1))])
                toffoli_gate(z[int(pow(2, t) * m)], b[2 * m], tmp_ancilla[tmp_idx], and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx], z[int(pow(2, t) * m + pow(2, t - 1))])
                toffoli_gate(z[int(pow(2, t) * m)], b[2 * m], tmp_ancilla[tmp_idx], and_ancilla[and_idx], False)
            else:
                if m==1:
                    iter += l(n-1, t - 1) - 1
                    pre = length - 1 - iter
                #print(int(pow(2, t) * m),pre + 2 * m,int(pow(2, t) * m + pow(2, t-1)))
                #toffoli_gate(z[int(pow(2, t) * m)], ancilla[pre + 2 * m], z[int(pow(2, t) * m + pow(2, t-1))])
                toffoli_gate(z[int(pow(2, t) * m)], ancilla[pre + 2 * m],tmp_ancilla[tmp_idx], and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx],z[int(pow(2, t) * m + pow(2, t - 1))])
                toffoli_gate(z[int(pow(2, t) * m)], ancilla[pre + 2 * m],tmp_ancilla[tmp_idx], and_ancilla[and_idx], False)

            and_idx = (and_idx + 1) % and_len
            tmp_idx += 1

    # P-inverse round
    #print("P-inv-rounds")
    pre = 0  # (t-1)일 때의 첫번째 idx
    iter = l(n-1, int(log2(n-1)) - 1) - 1  # 마지막 pt의 개수
    iter2 = 0 # for idx
    idx = 0
    and_idx = 0
    for t in reversed(range(1, int(log2(n-1)))):
        for m in range(1, l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(2*m,2*m+1,m-t)
                toffoli_gate(b[2 * m], b[2 * m + 1], ancilla[m - t], and_ancilla[and_idx], False)
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                if m == 1:
                    iter += l(n-1, t - 1) - 1  # p(t-1) last idx
                    pre = length - iter
                    iter2 += (l(n-1, t) - 1)
                    idx = length - iter2
                #print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx-1+m)
                toffoli_gate(ancilla[pre - 1 + 2 * m], ancilla[pre - 1 + 2 * m + 1], ancilla[idx-1+m], and_ancilla[and_idx], False)
            and_idx += 1

    # Last round
    for i in range(n-1):
        CNOT | (b[i], z[i])
    CNOT | (a[0], z[0])
    for i in range(1, n-1):
        CNOT | (a[i], b[i])
    return z

def outDraper_dag(a,b,z,ancillas,n):
    length = n-1-w(n-1)-floor(log2(n-1))
    #ancilla = eng.allocate_qureg(length)  # 논문에서 X라고 지칭되는 ancilla
    ancilla = ancillas[:length]
    and_len = n - 1
    # and_ancilla = eng.allocate_qureg(and_len)
    and_ancilla = ancillas[length:length + n - 1]
    and_idx = 0
    tmp_len = (n - 1) - w(n - 1)
    # tmp_ancilla = eng.allocate_qureg(tmp_len)
    tmp_ancilla = ancillas[length + n - 1:]
    tmp_idx = 0

    # Last round - 뒤집음
    for i in range(1, n - 1):
        CNOT | (a[i], b[i])
    CNOT | (a[0], z[0])
    for i in range(n - 1):
        CNOT | (b[i], z[i])

    # P-round
    idx = 0  # ancilla idx
    tmp = 0  # m=1일 때 idx 저장해두기
    for t in range(1, int(log2(n - 1))):
        pre = tmp  # (t-1)일 때의 첫번째 자리 저장
        for m in range(1, l(n - 1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                # print(2*m,2*m+1,idx)
                toffoli_gate(b[2 * m], b[2 * m + 1], ancilla[idx], and_ancilla[and_idx])  # and
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                # print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx)
                toffoli_gate(ancilla[pre - 1 + 2 * m], ancilla[pre - 1 + 2 * m + 1], ancilla[idx],
                             and_ancilla[and_idx])  # and
            if m == 1:
                tmp = idx
            idx += 1
            and_idx += 1

    # C-round - reverse 했음
    pre = 0  # 이전 p(t) 개수
    tmp_idx = 0
    for t in reversed(range(int(log2(2 * (n - 1) / 3)), 0, -1)):
        idx = pre
        for m in range(1, l((n - 1 - pow(2, t - 1)), t) + 1):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(z[int(pow(2, t) * m)], b[2 * m], tmp_ancilla[tmp_idx], and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx], z[int(pow(2, t) * m + pow(2, t - 1))])
                toffoli_gate(z[int(pow(2, t) * m)], b[2 * m], tmp_ancilla[tmp_idx], and_ancilla[and_idx], False)
            else:
                toffoli_gate(z[int(pow(2, t) * m)], ancilla[idx-1+ 2 * m], tmp_ancilla[tmp_idx],
                             and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx], z[int(pow(2, t) * m + pow(2, t - 1))])
                toffoli_gate(z[int(pow(2, t) * m)], ancilla[idx - 1 + 2 * m], tmp_ancilla[tmp_idx],
                             and_ancilla[and_idx], False)
                if m == 1:
                    pre += l(n-1, t-1) -1
            and_idx = (and_idx + 1) % and_len
            tmp_idx += 1

    # G-round - reverse 했음
    pre = 0  # The number of cumulative p(t-1)
    idx_t = int(log2(n-1)) # n-1이 아니라 n일 때의 t의 범위
    iter = 0
    tmp_idx = 0
    for t in reversed(range(1, int(log2(n-1)) + 1)):
        for m in range(l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(z[int(pow(2, t) * m + pow(2, t - 1))], b[2 * m + 1], tmp_ancilla[tmp_idx],
                             and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx], z[int(pow(2, t) * (m + 1))])
                toffoli_gate(z[int(pow(2, t) * m + pow(2, t - 1))], b[2 * m + 1], tmp_ancilla[tmp_idx],
                             and_ancilla[and_idx], False)

            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                if m == 0:
                    iter += l(n-1, idx_t-1) -1  # p(t-1) last idx
                    pre = length - iter
                    idx_t -= 1

                toffoli_gate(z[int(pow(2, t) * m + pow(2, t - 1))], ancilla[pre-1+2*m+1], tmp_ancilla[tmp_idx],
                             and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx], z[int(pow(2, t) * (m + 1))])
                toffoli_gate(z[int(pow(2, t) * m + pow(2, t - 1))], ancilla[pre-1+2*m+1], tmp_ancilla[tmp_idx],
                             and_ancilla[and_idx], False)
            and_idx = (and_idx + 1) % and_len
            tmp_idx += 1

    # P-inverse round
    pre = 0  # (t-1)일 때의 첫번째 idx
    iter = l(n-1, int(log2(n-1)) - 1) - 1  # 마지막 pt의 개수
    iter2 = 0 # for idx
    idx = 0
    and_idx = 0
    for t in reversed(range(1, int(log2(n-1)))):
        for m in range(1, l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(2*m,2*m+1,m-t)
                toffoli_gate(b[2 * m], b[2 * m + 1], ancilla[m - t], and_ancilla[and_idx], False) # 여긴 ancilla 0으로 해도 됨
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                if m == 1:
                    iter += l(n-1, t - 1) - 1  # p(t-1) last idx
                    pre = length - iter
                    iter2 += (l(n-1, t) - 1)
                    idx = length - iter2
                #print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx-1+m)
                toffoli_gate(ancilla[pre - 1 + 2 * m], ancilla[pre - 1 + 2 * m + 1], ancilla[idx-1+m], and_ancilla[and_idx], False)
            and_idx += 1

    recycle_ancilla = ancilla+tmp_ancilla
    # Init round
    CNOT | (b[n - 1], z[n - 1])
    CNOT | (a[n - 1], z[n - 1])
    for i in range(1, n - 1):
        CNOT | (a[i], b[i])
    for i in range(n - 1):
        toffoli_gate(a[i], b[i], recycle_ancilla[i], and_ancilla[i])
        CNOT | (recycle_ancilla[i], z[i+1])
        toffoli_gate(a[i], b[i], recycle_ancilla[i], and_ancilla[i], False)

    return z

def inDraper(a,b,ancillas,n):

    length = n-1-w(n-1)-floor(log2(n-1))
    #ancilla1 = eng.allocate_qureg(n-1) # z[1] ~ z[n] 저장
    ancilla1 = ancillas[:n-1]
    #ancilla2 = eng.allocate_qureg(length) # 논문에서 X라고 지칭되는 ancilla
    ancilla2 = ancillas[n-1:n-1+length]
    and_len = n - 1
    #and_ancilla = eng.allocate_qureg(and_len)
    and_ancilla = ancillas[n-1+length:2*n-2+length]
    and_idx = 0
    tmp_len = (n - 1) - w(n - 1)
    #tmp_ancilla = eng.allocate_qureg(tmp_len)
    tmp_ancilla = ancillas[2*n-2+length:]
    tmp_idx = 0

    # Init round
    for i in range(n-1):
        toffoli_gate(a[i], b[i], ancilla1[i], and_ancilla[and_idx]) # ancilla1[0] == Z[1]
        and_idx += 1
    for i in range(n):
        CNOT | (a[i], b[i])

    # P-round
    #print("P-rounds")
    idx = 0  # ancilla idx
    tmp = 0  # m=1일 때 idx 저장해두기
    and_idx = 0
    for t in range(1, int(log2(n-1))):
        pre = tmp  # (t-1)일 때의 첫번째 자리 저장
        #print("t ========== ",t)
        for m in range(1, l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(b[2 * m], b[2 * m + 1], ancilla2[idx], and_ancilla[and_idx])
                #print(2*m,2*m+1,idx)
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                toffoli_gate(ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx], and_ancilla[and_idx])
                #print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx)
            if m == 1:
                tmp = idx
            idx += 1
            and_idx += 1

    # G-round
    #print("G-rounds")
    pre = 0  # The number of cumulative p(t-1)
    idx = 0  # ancilla idx
    for t in range(1, int(log2(n-1)) + 1):
        #print("t = ",t)
        for m in range(l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #toffoli_gate(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], b[2 * m + 1], ancilla1[int(pow(2, t) * (m + 1)) - 1])
                toffoli_gate(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], b[2 * m + 1], tmp_ancilla[tmp_idx], and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx],ancilla1[int(pow(2, t) * (m + 1)) - 1])
                toffoli_gate(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], b[2 * m + 1], tmp_ancilla[tmp_idx], and_ancilla[and_idx], False)
                #print(int(pow(2, t) * m + pow(2, t - 1)) - 1,2 * m + 1,int(pow(2, t) * (m + 1)) - 1)
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                #print(int(pow(2, t) * m + pow(2, t - 1)) - 1,idx+2*m,int(pow(2, t) * (m + 1)) - 1)
                #toffoli_gate(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[idx+2*m],ancilla1[int(pow(2, t) * (m + 1)) - 1])
                toffoli_gate(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[idx+2*m],tmp_ancilla[tmp_idx], and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx], ancilla1[int(pow(2, t) * (m + 1)) - 1])
                toffoli_gate(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[idx+2*m],tmp_ancilla[tmp_idx], and_ancilla[and_idx], False)
            and_idx = (and_idx + 1) % and_len
            tmp_idx += 1
        if t != 1:
            pre = pre + l(n-1, t - 1) - 1
            idx = pre

    # C-round
    #print("C-rounds")
    if int(log2(n-1)) - 1 == int(log2(2 * (n-1)/ 3)): # p(t-1)까지 접근함
        iter = l(n-1, int(log2(n-1)) - 1) - 1 # 마지막 pt의 개수
    else: # p(t)까지 접근함
        iter = 0
    pre = 0  # (t-1)일 때의 첫번째 idx
    tmp_idx = 0
    for t in range(int(log2(2 * (n-1) / 3)), 0, -1):
        for m in range(1, l(((n-1) - pow(2, t - 1)), t) + 1):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #toffoli_gate(ancilla1[int(pow(2, t) * m) - 1], b[2 * m],ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
                toffoli_gate(ancilla1[int(pow(2, t) * m) - 1], b[2 * m],tmp_ancilla[tmp_idx], and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx],ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
                toffoli_gate(ancilla1[int(pow(2, t) * m) - 1], b[2 * m], tmp_ancilla[tmp_idx], and_ancilla[and_idx], False)
                #print(int(pow(2, t) * m) - 1,2 * m,int(pow(2, t) * m + pow(2, t - 1)) - 1)
            else:
                if m==1:
                    iter += l(n-1, t - 1) - 1
                    pre = length - 1 - iter
                toffoli_gate(ancilla1[int(pow(2, t) * m) - 1],ancilla2[pre + 2 * m],tmp_ancilla[tmp_idx], and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx], ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
                toffoli_gate(ancilla1[int(pow(2, t) * m) - 1],ancilla2[pre + 2 * m],tmp_ancilla[tmp_idx], and_ancilla[and_idx],False)
                #print(int(pow(2, t) * m) - 1,pre + 2 * m,int(pow(2, t) * m + pow(2, t - 1)) - 1)

            and_idx = (and_idx + 1) % and_len
            tmp_idx += 1

    # P-inverse round
    #print("P-inverse round")
    pre = 0  # (t-1)일 때의 첫번째 idx
    iter = l(n-1, int(log2(n-1)) - 1) - 1  # 마지막 pt의 개수
    iter2 = 0  # for idx
    idx = 0
    and_idx = 0
    for t in reversed(range(1, int(log2(n-1)))):
        for m in range(1, l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(b[2 * m], b[2 * m + 1], ancilla2[m - t], and_ancilla[and_idx], False)
                #print(2*m, 2*m+1, m-t)
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                if m == 1:
                    iter += l(n-1, t - 1) - 1  # p(t-1) last idx
                    pre = length - iter
                    iter2 += (l(n-1, t) - 1)
                    idx = length - iter2
                toffoli_gate(ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx-1+m], and_ancilla[and_idx], False)
                #print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx-1+m)
            and_idx += 1

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
    and_idx = 0

    for t in range(1, int(log2(n-1))):
        if t > 1:
            pre = iter
            iter += l(n-1, t - 1) - 1 # ancilla idx. n is right.
            idx = iter
        #print("t ========== ", t)
        for m in range(1, l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(2 * m, 2 * m + 1, idx)
                toffoli_gate(b[2 * m], b[2 * m + 1], ancilla2[idx], and_ancilla[and_idx])
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                #print(pre - 1 + 2 * m, pre - 1 + 2 * m + 1, idx)
                toffoli_gate(ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx], and_ancilla[and_idx])
            idx += 1
            and_idx += 1

    # C-round reverse
    #print("C-inv-rounds")
    pre = 0  # 이전 p(t) 개수
    tmp_idx = 0
    for t in reversed(range(int(log2(2 * (n-1) / 3)), 0, -1)):
        idx = pre # ancilla2 idx
        for m in range(1, l(((n-1) - pow(2, t - 1)), t) + 1):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(int(pow(2, t) * m) - 1, 2 * m, int(pow(2, t) * m + pow(2, t - 1)) - 1)
                #toffoli_gate(ancilla1[int(pow(2, t) * m) - 1], b[2 * m],ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
                toffoli_gate(ancilla1[int(pow(2, t) * m) - 1], b[2 * m],tmp_ancilla[tmp_idx], and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx], ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
                toffoli_gate(ancilla1[int(pow(2, t) * m) - 1], b[2 * m],tmp_ancilla[tmp_idx], and_ancilla[and_idx],False)
            else:
                #print(int(pow(2, t) * m) - 1, idx - 1 + 2 * m, int(pow(2, t) * m + pow(2, t - 1)) - 1)
                #toffoli_gate(ancilla1[int(pow(2, t) * m) - 1],ancilla2[idx-1+ 2 * m], ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
                toffoli_gate(ancilla1[int(pow(2, t) * m) - 1],ancilla2[idx-1+ 2 * m],tmp_ancilla[tmp_idx], and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx],ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
                toffoli_gate(ancilla1[int(pow(2, t) * m) - 1],ancilla2[idx-1+ 2 * m], tmp_ancilla[tmp_idx], and_ancilla[and_idx],False)
                if m == 1:
                    pre += l(n-1, t-1) -1

            and_idx = (and_idx + 1) % and_len
            tmp_idx += 1

    # G-round reverse
    #print("G-inv-rounds")
    pre = 0  # (t-1)일 때의 첫번째 idx
    idx_t = int(log2(n-1)) # n-1이 아니라 n일 때의 t의 범위
    iter = 0
    tmp_idx = 0
    for t in reversed(range(1, int(log2(n-1)) + 1)):
        #print("t=",t)
        for m in range(l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                #print(int(pow(2, t) * m + pow(2, t - 1)) - 1,2 * m + 1,int(pow(2, t) * (m + 1)) - 1)
                #toffoli_gate(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], b[2 * m + 1],ancilla1[int(pow(2, t) * (m + 1)) - 1])
                toffoli_gate(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], b[2 * m + 1],tmp_ancilla[tmp_idx], and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx],ancilla1[int(pow(2, t) * (m + 1)) - 1])
                toffoli_gate(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], b[2 * m + 1], tmp_ancilla[tmp_idx],and_ancilla[and_idx],False)

            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                if m==0:
                    iter += l(n-1, idx_t-1) - 1  # p(t-1) last idx
                    pre = length - iter
                    idx_t -= 1

                #print(int(pow(2, t) * m + pow(2, t - 1)) - 1, pre - 1 + 2 * m + 1, int(pow(2, t) * (m + 1)) - 1)
                #toffoli_gate(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[pre - 1 + 2 * m + 1],ancilla1[int(pow(2, t) * (m + 1)) - 1])
                toffoli_gate(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[pre - 1 + 2 * m + 1],tmp_ancilla[tmp_idx],and_ancilla[and_idx])
                CNOT | (tmp_ancilla[tmp_idx], ancilla1[int(pow(2, t) * (m + 1)) - 1])
                toffoli_gate(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[pre - 1 + 2 * m + 1],tmp_ancilla[tmp_idx],and_ancilla[and_idx], False)
            and_idx = (and_idx + 1) % and_len
            tmp_idx += 1

    # P-inverse round reverse
    #print("P-inverse round reverse")
    pre = 0  # (t-1)일 때의 첫번째 idx
    idx_t = int(log2(n-1))-1 # n-1이 아니라 n일 때의 t의 범위
    iter = l(n-1, idx_t) - 1
    iter2 = 0  # for idx
    and_idx = 0
    for t in reversed(range(1, int(log2(n-1)))):
        for m in range(1, l(n-1, t)):
            if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                toffoli_gate(b[2 * m], b[2 * m + 1], ancilla2[m - t],and_ancilla[and_idx], False)
                #print(2*m,2*m+1,m-t)
            else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                if m == 1:
                    iter += l(n-1, idx_t-1) - 1  # p(t-1) last idx
                    pre = length - iter
                    iter2 += l(n-1, idx_t) - 1
                    idx = length - iter2
                    idx_t -= 1
                toffoli_gate(ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx-1+m],and_ancilla[and_idx], False)
                #print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx-1+m)
            and_idx += 1

    # real last
    for i in range(1,n-1):
        CNOT | (a[i], b[i])
    and_idx = 0
    for i in range(n-1):
        toffoli_gate(a[i], b[i], ancilla1[i], and_ancilla[and_idx],False)
    for i in range(n-1):
        X | b[i]

    result = []
    for k in b:
        result.append(k)

    return result

def make_list(num,length): # 상수 배열 생성

    arr1 = list(format(num, 'b'))
    if length > len(arr1):
        arr2 = ['0' for i in range(length-len(arr1))]
        arr2.extend(arr1)
        arr1 = arr2
    return arr1

def SHA256_init_H(H):
    H0_hex = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]

    for i in range(8):
        chain = make_list(H0_hex[i], 32)
        for j in range(32):
            if chain[j] == '1':
                # X | H[i][j]
                X | H[i][31 - j]

def SHA256_init_K(K, idx):

    K_hex = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
             0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
             0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
             0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
             0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
             0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
             0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
             0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
             0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
             0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
             0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

    chain = make_list(K_hex[idx], 32)
    for j in range(32):
        if chain[j] == '1':
            # X | K[i][j]
            X | K[31-j]

# msg가 1블럭이라고 가정
def SHA256_preprocessing(msg, q_msg): # q_msg는 W의 0~15가 돼야함

    # Padding
    lenght = len(msg)
    msg_bin = []

    for i in range(lenght):
        msg_bin += make_list(ord(msg[i]), 8) # ord는 문자의 아스키코드를 반환해줌
    lenght = len(msg_bin) # 메시지 길이. 맨 뒤에 넣어줘야함!
    msg_bin += ['1'] # 메시지 바로 뒤에 1을 써줘야함

    for i in range(lenght+1, 448): # 여기는 다 0
        msg_bin += ['0']

    len_arr = make_list(lenght, 64)  # 맨 뒤 64비트는 메시지의 길이를 넣어야함
    msg_bin += len_arr # ---- 여기까지 msg 1차원 배열 완성 (512비트) ----
    # Parsing
    if resource_check != 1:
        for i in range(16):
            for j in range(32):
                if msg_bin[i*32+j] == '1':
                    X | q_msg[i][31-j]

def w_sigma0(input): # 2 13 22

    row = 32

    L = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0,
         1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0,
         0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1]

    U = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]

    ######## PLU Decomposition ########
    Apply_U(input, row, U)
    Apply_L(input, row, L)
    Apply_P_W0(input)

def w_sigma0_dag(input):

    row = 32

    L = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0,
         1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0,
         0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1]

    U = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]

    ######## PLU Decomposition ########
    rev_Apply_P_W0(input)
    Apply_L(input, row, L)
    Apply_U(input, row, U)

def w_sigma1(input): # 6 11 25

    row = 32

    L = [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,
        0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,
        0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,1,0,0,0,0,0,0,0,0,
        0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,0,0,1,0,0,0,0,0,0,0,
        0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,1,0,0,0,1,0,0,0,0,0,0,
        0,1,0,0,0,0,1,0,0,0,0,1,0,0,1,0,1,0,0,0,1,0,1,1,0,1,1,0,0,0,0,0,
        1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1,0,1,1,0,0,1,0,0,0,0,
        0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,1,0,0,1,0,0,1,1,0,1,0,1,0,0,0,
        0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,1,0,0,1,1,1,0,1,1,1,0,1,0,0,
        0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,1,0,1,0,0,0,1,0,1,1,0,1,0,0,0,1,0,
        0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,1,0,0,1,0,0,1,1,0,1,1,1,0,0,1,1]

    U = [1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,
        0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,
        0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,
        0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,
        0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,
        0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,
        0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
        0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,1,1,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,1,1,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,1,1,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,1,1,0,0,0,0,1,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,1,1,0,0,0,0,1,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,1,0,0,0,1,1,1,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,0,1,1,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,0,1,1,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,0,1,1,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,0,1,1,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,1,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]

    ######## PLU Decomposition ########
    Apply_U(input, row, U)
    Apply_L(input, row, L)
    Apply_P_W1(input)

def w_sigma1_dag(input):

    row = 32

    L = []

    U = []

    ######## PLU Decomposition ########
    rev_Apply_P_W1_dag(input)
    Apply_L(input, row, L)
    Apply_U(input, row, U)

def SHA256_mexp(eng, W, ancilla, i): # ancilla 2 세트

    # for i in range(16, 64):
        # carry save adder 쓰면 좋겠다
        # draper 안실라도 재활용!
        # outDraper(eng, W[i-2], W[i-7], W[i], 32) # W[i]에 덧셈 결과 저장
    inDraper(W[(i-7)%16],W[i%16],ancilla[2:6],32)
    with Compute(eng):
        w_sigma(7, 18, 3, W[(i-15)%16], ancilla[0])  # sigma0
        w_sigma(17, 19, 10, W[(i-2)%16], ancilla[1])  # sigma1
    inDraper(ancilla[0], W[i%16], ancilla[2:6], 32)
    inDraper(ancilla[1], W[i%16], ancilla[2:6], 32)
    # if i < 63: # 재활용하나 뒤에서 ?
    Uncompute(eng)

def r_sigma(rr0, rr1, rr2, input, output):

    for i in range(32):
        CNOT | (input[(rr0+i)%32], output[i])
        CNOT | (input[(rr1+i)%32], output[i])
        CNOT | (input[(rr2+i)%32], output[i])

def maj(x, y, z, ancilla):
    for i in range(32):
        CNOT | (z[i], y[i])
        CNOT | (z[i], x[i])
        toffoli_gate(x[i], y[i], z[i], ancilla[i])

def maj_dag(x, y, z):
    for i in range(32):
        toffoli_gate(x[i], y[i], z[i], 0, False)
        CNOT | (z[i], x[i])
        CNOT | (z[i], y[i])

def ch(x, y, z, ancilla):
    for i in range(32):
        CNOT | (z[i], y[i])
        toffoli_gate(x[i], y[i], z[i], ancilla[i])

def ch_dag(x, y, z):
    for i in range(32):
        toffoli_gate(x[i], y[i], z[i], 0, False)
        CNOT | (z[i], y[i])

def copy(x, y):
    for i in range(32):
        CNOT | (x[i], y[i])

def SHA256_round(K, W, H, ancilla, add_ancilla):

    h = []
    for i in range(8):
        h.append(H[i])

    idx = 16 # W index
    # 라운드 프로세스 시작
    for i in range(64):
        r_sigma(2, 13, 22, h[0], ancilla[0]) # 0
        r_sigma(6, 11, 25, h[4], ancilla[1]) # 1
        maj(h[0], h[1], h[2], ancilla[5]) # h[2], 재활용
        ch(h[4],h[5],h[6], ancilla[7]) # h[6], 재활용
        if i >= 1:
            copy(ancilla[6], ancilla[8])  # copy dag
        # MEXP
        if i >= 2 and idx < 64:
            w_sigma(17, 19, 10, W[(idx-2)%16],ancilla[2]) # sigma1

        # 덧셈기 병렬 1
        outDraper(ancilla[0], h[2], ancilla[3], add_ancilla[2], 32) # rs+maj = an0
        outDraper(ancilla[1], h[6], ancilla[4], add_ancilla[3], 32) # rs+ch = an1
        outDraper(ancilla[3], ancilla[4], ancilla[5], add_ancilla[2], 32) # an0+an1 = an2
        inDraper(h[7],h[3],add_ancilla[0],32) # h+d
        # MEXP
        if i >= 2 and idx < 64:
            r_sigma(6, 11, 25, h[4], ancilla[1])  # 1 dag 처음
            outDraper(W[(idx-7)%16], ancilla[2], ancilla[7], add_ancilla[3], 32)  # w[i-7]+sigma1 = an4
            w_sigma(7, 18, 3, W[(idx-15)%16], ancilla[8]) # sigma0
            inDraper(ancilla[8], W[idx%16], add_ancilla[1], 32)  # w+sigma0
            w_sigma(7, 18, 3, W[(idx-15)%16], ancilla[8]) # sigma0 dag

        # 덧셈기 병렬 2
        inDraper(ancilla[4],h[3],add_ancilla[0], 32) # an1+d
        inDraper(ancilla[5],h[7],add_ancilla[1], 32) # an2+h
        if i >= 1:
            outDraper_dag(K, W[(i-1)%16], ancilla[6], add_ancilla[3], 32)  # an3 dag
            SHA256_init_K(K,i-1) # dag
        SHA256_init_K(K, i)
        outDraper(K, W[i%16], ancilla[6], add_ancilla[3], 32)  # w+k = an3
        copy(ancilla[6], ancilla[8])
        tmp = ancilla[1]+add_ancilla[2]
        # MEXP
        if i >= 2 and idx < 64:
            inDraper(ancilla[7], W[idx % 16], tmp, 32)  # w+an4
            r_sigma(6, 11, 25, h[4], ancilla[1])  # 1 다시

        # 덧셈기 병렬 3
        inDraper(ancilla[6],h[7],add_ancilla[0], 32) # an3+h
        inDraper(ancilla[8],h[3],add_ancilla[1], 32) # copy+d
        outDraper_dag(ancilla[3], ancilla[4], ancilla[5], add_ancilla[2], 32) # an2 dag
        outDraper_dag(ancilla[0], h[2], ancilla[3], add_ancilla[3], 32) # an0 dag
        outDraper_dag(ancilla[1], h[6], ancilla[4], add_ancilla[2], 32) # an1 dag
        # MEXP
        if i >= 2 and idx < 64:
            outDraper_dag(W[(idx-7)%16], ancilla[2], ancilla[7], add_ancilla[3], 32)  # an4 dag
            w_sigma(17, 19, 10, W[(idx-2)%16],ancilla[2]) # sigma1 dag
            idx += 1

        if i == 63:
            copy(ancilla[6], ancilla[8]) # copy dag
            outDraper_dag(K, W[i%16], ancilla[6], add_ancilla[3], 32)  # an3 dag
            SHA256_init_K(K, i) # K dag

        ch_dag(h[4], h[5], h[6])
        maj_dag(h[0], h[1], h[2])
        r_sigma(2, 13, 22, h[0], ancilla[0])  # 0 dag
        r_sigma(6, 11, 25, h[4], ancilla[1])  # 1 dag 최종

        swap = h[0]
        h[0] = h[7]
        h[7] = h[6]
        h[6] = h[5]
        h[5] = h[4]
        h[4] = h[3]
        h[3] = h[2]
        h[2] = h[1]
        h[1] = swap

    # print("ancilla")
    # for i in range(24):
    #     print_vector(ancilla[i], 32)
    # print("체크 완")

def print_vector(element, length):

    All(Measure) | element
    for k in range(length):
        print(int(element[length-1-k]), end='')
    print()

def Apply_U(key, n, U):
    for i in range(n - 1):  # row
        for j in range(n - 1 - i):  # column (Upper라서 역삼각형)
            if (U[(i * n) + 1 + i + j] == 1):  # list는 왼->오, 실제로는 오->왼
                CNOT | (key[1 + i + j], key[i])

def Apply_L(key, n, L):
    for i in range(n - 1):  # row
        for j in range(n - 1, 0 + i, -1):  # column (Lower라서 왼쪽직각삼각형만, 밑에서부터 위로)
            if (L[n * (n - 1 - i) + (n - 1 - j)] == 1):
                CNOT | (key[n - 1 - j], key[n - 1 - i])

def Apply_P_W0(key):
    tmp1 = key[0]
    tmp2 = key[1]
    for i in range(10):
        key[i] = key[i + 2]
    key[10] = tmp1
    key[11] = tmp2
    tmp1 = key[12]
    for i in range(12,19):
        key[i] = key[i+1]
    key[19] = tmp1

def rev_Apply_P_W0(key):
    tmp1 = key[19]
    for i in range(18,11,-1):
        key[i+1] = key[i]
    key[12] = tmp1
    tmp2 = key[11]
    tmp1 = key[10]
    for i in range(9,-1,-1):
        key[i+2] = key[i]
    key[1] = tmp2
    key[0] = tmp1

def main(eng):

    H = []
    K = eng.allocate_qureg(32)
    W = []

    for i in range(8):
        H.append(eng.allocate_qureg(32))

    for i in range(16):
        W.append(eng.allocate_qureg(32))

    ancilla = []
    for i in range(9):
        ancilla.append(eng.allocate_qureg(32)) # for MXF and round

    add_ancilla = []
    add_ancilla.append(eng.allocate_qureg(112))  # for adder (in) # 원래는 111개인데 마지막 때문에!
    add_ancilla.append(eng.allocate_qureg(112))
    add_ancilla.append(eng.allocate_qureg(80))  # for adder (out)
    add_ancilla.append(eng.allocate_qureg(80))

    msg = "abc"

    SHA256_init_H(H)
    SHA256_preprocessing(msg, W)
    SHA256_round(K, W, H, ancilla, add_ancilla)

    # 테스트 벡터 맞춰볼 때만 사용하기
    # SHA256_init_H()


    # H[0] = ancilla[4]
    # H[1] = ancilla[5]
    # H[2] = ancilla[6]
    # H[3] = ancilla[7]
    # H[4] = add_ancilla[0][80:]
    # H[5] = add_ancilla[1][80:]
    # H[6] = K
    # H[7] = ancilla[8]

    if resource_check != 1:
        for i in range(8):
            print_vector(H[i],32)

TD = 2
resource_check = 1
#Resource = ClassicalSimulator()
Resource = ResourceCounter()
eng = MainEngine(Resource)
main(eng)
# test(eng)
print(Resource)
eng.flush()