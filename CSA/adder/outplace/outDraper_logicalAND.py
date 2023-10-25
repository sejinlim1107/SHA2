# TODO: Document the code !!
"""
  Implementation of the carry lookahead adder
  arxiv preprint 0406142
  A logarithmic-depth quantum carry-lookahead adder
"""
import cirq
from adder.BaseAdder import BaseAdder

from math import floor, log2
import toffoli.toffoli as Toffoli

toffoli = Toffoli.logicalAND(True)
logicalAND = toffoli.logicalAND
uncomputation = toffoli.uncomputation

class OutplaceAdder(BaseAdder):
    def __init__(self, is_metric_mode=False):
        super().__init__(is_metric_mode)
        self.Z = None

    def create(self, a, b, is_metric_mode=False):
        self.A, self.B = a, b
        self.Z = [cirq.NamedQubit("Z" + self.id + '_' + str(i)) for i in range(len(self.A) + 1)]
        self.circuit, self.result = self.construct_circuit()
        return self.circuit, self.result

    def w(self, n):
        return n - sum(int(floor(n / (pow(2, i)))) for i in range(1, int(log2(n)) + 1))

    def l(self, n, t):
        return int(floor(n / (pow(2, t))))

    def construct_circuit(self):
        n = len(self.A)
        init = []
        p_round = []
        g_round = []
        c_round = []
        p_round_uncom = []
        g_rev = []
        c_rev = []

        length = n - self.w(n) - floor(log2(n))
        ancilla = [cirq.NamedQubit("ancilla" + str(i)) for i in range(length)]  # 논문에서 X라 지칭

        and_length = 2*n -self.w(n) -floor(log2(n)) -1
        and_ancilla = [cirq.NamedQubit("logical_ancilla" + str(i)) for i in range(and_length)]
        and_idx = 0



        # Init round
        for i in range(n):
            init.append(logicalAND(self.A[i], self.B[i], self.Z[i+1]))
            if i != 0:
                init.append(cirq.CNOT(self.A[i], self.B[i]))

        # P-round
        #print("P-round")
        idx = 0  # ancilla idx
        tmp = 0
        for t in range(1, int(log2(n))):
            pre = tmp
            for m in range(1, self.l(n, t)):
                if t == 1:
                    # print(2*m,2*m+1,idx)
                    p_round.append(logicalAND(self.B[2*m], self.B[2*m+1], ancilla[idx]))
                else:
                    # print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx)
                    p_round.append(logicalAND(ancilla[pre-1+2*m], ancilla[pre-1+2*m+1], ancilla[idx]))
                if m==1:
                    tmp = idx
                idx += 1

        # G-round
        #print("G-round")
        pre = 0  # The number of cumulative p(t-1)
        idx = 0  # ancilla idx
        for t in range(1, int(log2(n))+1):
            for m in range(self.l(n, t)):
                if t == 1:
                    # print(int(pow(2, t) * m + pow(2, t - 1)), 2*m+1, int(pow(2, t) * (m + 1)))
                    g_round.append(logicalAND(self.Z[int(pow(2, t)*m + pow(2, t-1))], self.B[2 * m + 1], and_ancilla[and_idx]))
                    g_round.append(cirq.CNOT(and_ancilla[and_idx],self.Z[int(pow(2, t)*(m+1))]))
                    #g_round.append(uncomputation(self.Z[int(pow(2, t)*m + pow(2, t-1))], self.B[2 * m + 1], and_ancilla[and_idx]))
                    g_rev.append(uncomputation(self.Z[int(pow(2, t)*m + pow(2, t-1))], self.B[2 * m + 1], and_ancilla[and_idx]))
                else:
                    #print(int(pow(2, t) * m + pow(2, t - 1)), idx+2*m, int(pow(2, t) * (m + 1)))
                    g_round.append(logicalAND(self.Z[int(pow(2, t)*m + pow(2, t-1))], ancilla[idx+2*m], and_ancilla[and_idx]))
                    g_round.append(cirq.CNOT(and_ancilla[and_idx], self.Z[int(pow(2, t)*(m+1))]))
                    #g_round.append(uncomputation(self.Z[int(pow(2, t)*m + pow(2, t-1))], ancilla[idx+2*m], and_ancilla[and_idx]))
                    g_rev.append(uncomputation(self.Z[int(pow(2, t)*m + pow(2, t-1))], ancilla[idx+2*m], and_ancilla[and_idx]))
                and_idx += 1
            if t != 1:
                pre = pre + self.l(n, t - 1) - 1
                idx = pre

        # C-round
        #print("C-round")
        if int(log2(n)) - 1 == int(log2(2 * n / 3)):
            iter = self.l(n, int(log2(n)) - 1) - 1
        else:
            iter = 0
        pre = 0
        for t in range(int(log2(2*n/3)),0,-1):
            for m in range(1,self.l((n-pow(2,t-1)), t)+1):
                if t == 1:
                    # print(int(pow(2, t) * m), 2*m, int(pow(2, t) * m + pow(2, t - 1)))
                    c_round.append(
                        logicalAND(self.Z[int(pow(2, t) * m)], self.B[2 * m], and_ancilla[and_idx]))
                    c_round.append(cirq.CNOT(and_ancilla[and_idx], self.Z[int(pow(2, t) * m + pow(2, t - 1))]))
                    #c_round.append(uncomputation(self.Z[int(pow(2, t) * m)], self.B[2 * m], and_ancilla[and_idx]))
                    c_rev.append(uncomputation(self.Z[int(pow(2, t) * m)], self.B[2 * m], and_ancilla[and_idx]))
                else:
                    if m == 1:
                        iter += self.l(n, t - 1) - 1
                        pre = length - 1 - iter
                    # print(int(pow(2, t) * m),pre + 2 * m,int(pow(2, t) * m + pow(2, t-1)))
                    c_round.append(logicalAND(self.Z[int(pow(2, t) * m)], ancilla[pre + 2 * m],and_ancilla[and_idx]))
                    c_round.append(cirq.CNOT(and_ancilla[and_idx], self.Z[int(pow(2, t) * m + pow(2, t - 1))]))
                    #c_round.append(uncomputation(self.Z[int(pow(2, t) * m)], ancilla[pre + 2 * m], and_ancilla[and_idx]))
                    c_rev.append(uncomputation(self.Z[int(pow(2, t) * m)], ancilla[pre + 2 * m], and_ancilla[and_idx]))
                and_idx += 1

        # P-inverse round
        # print("P-inv-rounds")
        pre = 0
        iter = self.l(n, int(log2(n)) - 1) - 1
        iter2 = 0  # for idx
        idx = 0
        for t in reversed(range(1, int(log2(n)))):
            for m in range(1, self.l(n, t)):
                if t == 1:
                    # print(2*m,2*m+1,m-t)
                    p_round_uncom.append(uncomputation(self.B[2 * m], self.B[2 * m + 1], ancilla[m - t]))
                else:
                    if m == 1:
                        iter += self.l(n, t - 1) - 1  # p(t-1) last idx
                        pre = length - iter
                        iter2 += (self.l(n, t) - 1)
                        idx = length - iter2
                    # print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx-1+m)
                    p_round_uncom.append(uncomputation(ancilla[pre - 1 + 2 * m], ancilla[pre - 1 + 2 * m + 1], ancilla[idx - 1 + m]))


        # Last round
        last_round = [cirq.CNOT(self.B[i], self.Z[i]) for i in range(n)]
        last_round += [cirq.CNOT(self.A[0], self.Z[0])]
        last_round += [cirq.CNOT(self.A[i], self.B[i]) for i in range(1, n)]

        circuit = cirq.Circuit()

        # Init
        circuit += init

        # P-round
        circuit += p_round

        # G-round
        circuit += g_round
        circuit += g_rev # uncomputation

        # C-round
        circuit += c_round
        circuit += c_rev # uncomputation

        # P-inverse
        circuit += p_round_uncom

        # Last round
        circuit += last_round

        result = []

        for k in self.Z:
            result.append(k)

        return circuit, result

