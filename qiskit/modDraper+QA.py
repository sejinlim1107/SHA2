from qiskit.circuit import *
from math import floor, log2


def w(n):
    return n - sum(int(floor(n / (pow(2, i)))) for i in range(1, int(log2(n)) + 1))

def l(n, t):
    return int(floor(n / (pow(2, t))))

def quantum_and(qc, a, b, c, ancilla):
    qc.h(c)
    qc.cx(b, ancilla)
    qc.cx(c, a)
    qc.cx(c, b)
    qc.cx(a, ancilla)
    qc.tdg(a)
    qc.tdg(b)
    qc.t(c)
    qc.t(ancilla)
    qc.cx(a, ancilla)
    qc.cx(c, b)
    qc.cx(c, a)
    qc.cx(b, ancilla)
    qc.h(c)
    qc.s(c)

def quantum_and_dag(qc, a, b, c, classic):
    qc.h(b)
    qc.h(c)
    qc.measure(c,classic)
    if(classic):
        qc.cx(a,b)
        qc.x(c)
    qc.h(b)

n = 32
a = QuantumRegister(n)
b = QuantumRegister(n)

length = n-1-w(n-1)-floor(log2(n-1))
ancilla1 = QuantumRegister(n-1)
ancilla2 = QuantumRegister(length)

and_len = n-1
and_ancilla = QuantumRegister(and_len)
and_idx = 0
tmp_len = (n-1)-w(n-1)
tmp_ancilla = QuantumRegister(tmp_len)
tmp_idx = 0
classic = ClassicalRegister(length+tmp_len)
qc = QuantumCircuit(a,b,ancilla1,ancilla2,and_ancilla,tmp_ancilla,classic)

# Init round
for i in range(n-1):
    quantum_and(qc,a[i], b[i], ancilla1[i], and_ancilla[and_idx]) # ancilla1[0] == Z[1]
    and_idx += 1
for i in range(n):
    qc.cx(a[i], b[i])

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
            quantum_and(qc,b[2 * m], b[2 * m + 1], ancilla2[idx], and_ancilla[and_idx])
            #print(2*m,2*m+1,idx)
        else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
            quantum_and(qc,ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx], and_ancilla[and_idx])
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
            quantum_and(qc,ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], b[2 * m + 1], tmp_ancilla[tmp_idx], and_ancilla[and_idx])
            qc.cx(tmp_ancilla[tmp_idx],ancilla1[int(pow(2, t) * (m + 1)) - 1])
            quantum_and_dag(qc,ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], b[2 * m + 1], tmp_ancilla[tmp_idx], classic[tmp_idx])
            #print(int(pow(2, t) * m + pow(2, t - 1)) - 1,2 * m + 1,int(pow(2, t) * (m + 1)) - 1)
        else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
            #print(int(pow(2, t) * m + pow(2, t - 1)) - 1,idx+2*m,int(pow(2, t) * (m + 1)) - 1)
            #toffoli_gate(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[idx+2*m],ancilla1[int(pow(2, t) * (m + 1)) - 1])
            quantum_and(qc,ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[idx+2*m],tmp_ancilla[tmp_idx], and_ancilla[and_idx])
            qc.cx(tmp_ancilla[tmp_idx], ancilla1[int(pow(2, t) * (m + 1)) - 1])
            quantum_and_dag(qc,ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[idx+2*m],tmp_ancilla[tmp_idx], classic[tmp_idx])
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
            quantum_and(qc,ancilla1[int(pow(2, t) * m) - 1], b[2 * m],tmp_ancilla[tmp_idx], and_ancilla[and_idx])
            qc.cx(tmp_ancilla[tmp_idx],ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
            quantum_and_dag(qc,ancilla1[int(pow(2, t) * m) - 1], b[2 * m], tmp_ancilla[tmp_idx], classic[tmp_idx])
            #print(int(pow(2, t) * m) - 1,2 * m,int(pow(2, t) * m + pow(2, t - 1)) - 1)
        else:
            if m==1:
                iter += l(n-1, t - 1) - 1
                pre = length - 1 - iter
            quantum_and(qc,ancilla1[int(pow(2, t) * m) - 1],ancilla2[pre + 2 * m],tmp_ancilla[tmp_idx], and_ancilla[and_idx])
            qc.cx(tmp_ancilla[tmp_idx], ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
            quantum_and_dag(qc,ancilla1[int(pow(2, t) * m) - 1],ancilla2[pre + 2 * m],tmp_ancilla[tmp_idx], classic[tmp_idx])
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
            quantum_and_dag(qc,b[2 * m], b[2 * m + 1], ancilla2[m - t], classic[tmp_idx])
            #print(2*m, 2*m+1, m-t)
        else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
            if m == 1:
                iter += l(n-1, t - 1) - 1  # p(t-1) last idx
                pre = length - iter
                iter2 += (l(n-1, t) - 1)
                idx = length - iter2
            quantum_and_dag(qc,ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx-1+m], classic[tmp_idx])
            #print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx-1+m)
        and_idx += 1

# mid round
for i in range(1, n):
    qc.cx(ancilla1[i - 1], b[i])
for i in range(n-1):
    qc.x(b[i])
for i in range(1, n-1):
    qc.cx(a[i], b[i])

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
            quantum_and(qc, b[2 * m], b[2 * m + 1], ancilla2[idx], and_ancilla[and_idx])
        else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
            #print(pre - 1 + 2 * m, pre - 1 + 2 * m + 1, idx)
            quantum_and(qc, ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx], and_ancilla[and_idx])
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
            quantum_and(qc,ancilla1[int(pow(2, t) * m) - 1], b[2 * m],tmp_ancilla[tmp_idx], and_ancilla[and_idx])
            qc.cx(tmp_ancilla[tmp_idx], ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
            quantum_and_dag(qc,ancilla1[int(pow(2, t) * m) - 1], b[2 * m],tmp_ancilla[tmp_idx], classic[tmp_idx])
        else:
            #print(int(pow(2, t) * m) - 1, idx - 1 + 2 * m, int(pow(2, t) * m + pow(2, t - 1)) - 1)
            #toffoli_gate(ancilla1[int(pow(2, t) * m) - 1],ancilla2[idx-1+ 2 * m], ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
            quantum_and(qc,ancilla1[int(pow(2, t) * m) - 1],ancilla2[idx-1+ 2 * m],tmp_ancilla[tmp_idx], and_ancilla[and_idx])
            qc.cx(tmp_ancilla[tmp_idx],ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1])
            quantum_and_dag(qc,ancilla1[int(pow(2, t) * m) - 1],ancilla2[idx-1+ 2 * m], tmp_ancilla[tmp_idx], classic[tmp_idx])
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
            quantum_and(qc,ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], b[2 * m + 1],tmp_ancilla[tmp_idx], and_ancilla[and_idx])
            qc.cx(tmp_ancilla[tmp_idx],ancilla1[int(pow(2, t) * (m + 1)) - 1])
            quantum_and_dag(qc,ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], b[2 * m + 1], tmp_ancilla[tmp_idx], classic[tmp_idx])

        else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
            if m==0:
                iter += l(n-1, idx_t-1) - 1  # p(t-1) last idx
                pre = length - iter
                idx_t -= 1

            #print(int(pow(2, t) * m + pow(2, t - 1)) - 1, pre - 1 + 2 * m + 1, int(pow(2, t) * (m + 1)) - 1)
            #toffoli_gate(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[pre - 1 + 2 * m + 1],ancilla1[int(pow(2, t) * (m + 1)) - 1])
            quantum_and(qc,ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[pre - 1 + 2 * m + 1],tmp_ancilla[tmp_idx],and_ancilla[and_idx])
            qc.cx(tmp_ancilla[tmp_idx], ancilla1[int(pow(2, t) * (m + 1)) - 1])
            quantum_and_dag(qc,ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[pre - 1 + 2 * m + 1],tmp_ancilla[tmp_idx],classic[tmp_idx])
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
            quantum_and_dag(qc,b[2 * m], b[2 * m + 1], ancilla2[m - t], classic[tmp_idx])
            #print(2*m,2*m+1,m-t)
        else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
            if m == 1:
                iter += l(n-1, idx_t-1) - 1  # p(t-1) last idx
                pre = length - iter
                iter2 += l(n-1, idx_t) - 1
                idx = length - iter2
                idx_t -= 1
            quantum_and_dag(qc,ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx-1+m],classic[tmp_idx])
            #print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx-1+m)
        and_idx += 1

# real last
for i in range(1,n-1):
    qc.cx(a[i], b[i])
and_idx = 0
for i in range(n-1):
    quantum_and_dag(qc,a[i], b[i], ancilla1[i], classic[tmp_idx])
for i in range(n-1):
    qc.x(b[i])

t_depth = qc.depth(lambda gate: gate[0].name in ['t', 'tdg'])
print("t depth:", t_depth)
print("full depth : ", qc.depth())