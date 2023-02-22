init_comp, p_round_comp, g_round_comp, c_round_comp, last_round, p_round_uncomp, g_round_uncomp, c_round_uncomp, ancilla = self.construct_rounds()
# Init
circuit = cirq.Circuit(init_comp)

# P-round
circuit += cirq.Circuit(p_round_comp)

# G-round
circuit += cirq.Circuit(g_round_comp)

# C-round
circuit += cirq.Circuit(c_round_comp)

# P-inverse
circuit += cirq.Circuit(p_round_comp[::-1])

# Last round
circuit += cirq.Circuit(last_round)

### Step7. Section3 in reverse. (n-1)bit adder ###
n = len(self.A)

circuit += cirq.Circuit(p_round_uncomp)
circuit += cirq.Circuit(c_round_uncomp[::-1])
circuit += cirq.Circuit(g_round_uncomp[::-1])
circuit += cirq.Circuit(p_round_uncomp[::-1])

'''
### Step7. Section3 in reverse. (n-1)bit adder ###

p_round_uncomp = 0
# P round에서 어디까지 잘라야하는지 계산. 방식을 개선시킬 수 있을 것 같지만 일단 보류.
start = 0
end = 0
for t in range(1, int(mt.log2(n - 1))):
    for m in range(1, int(mt.floor((n - 1) / (mt.pow(2, t))))):
        end += 1
    p_round_uncomp += p_round_comp[start:end+1] # 기존 P-round 자르기
    start = int(mt.floor((n) / (mt.pow(2, t))))-1

#print(cnt)

p_round_uncomp = p_round_comp[:cnt] # 기존 P-round 자르기
circuit += cirq.Circuit(p_round_uncomp)

# C
cnt = 0
for t in range(int(mt.log2(2*(n-1)/3)),0,-1):
    for m in range(1,self.l(((n-1)-pow(2,t-1)), t)+1):
        cnt += 1


c_round_uncomp = c_round_comp[:cnt][::-1] # 기존 C-round 자르기 -> 뒤집기
circuit += cirq.Circuit(c_round_uncomp)

# G
cnt = 0
for t in range(1, int(mt.log2(n-1)) + 1):
    for m in range(self.l(n-1, t)):
        cnt += 1

g_round_uncomp = g_round_comp[:cnt][::-1]
circuit += cirq.Circuit(g_round_uncomp)

# P^(-1)
circuit += cirq.Circuit(p_round_uncomp[::-1])

'''

fin = [cirq.CNOT(self.A[i], self.B[i]) for i in range(1, n - 1)]
fin += [cirq.TOFFOLI(self.A[i], self.B[i], ancilla[i]) for i in range(n - 1)]
fin += [cirq.X(self.B[i]) for i in range(n - 1)]

circuit.append(fin)

result = []

for k in self.B:
    result.append(k)
result.append(ancilla[-1])

# print(circuit)
return circuit, result