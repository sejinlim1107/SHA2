# TODO: Document the code !!
"""
  Implementation of the carry lookahead adder
  arxiv preprint 0406142
  A logarithmic-depth quantum carry-lookahead adder
"""
import cirq
from math import floor, log2
from adder.BaseAdder import BaseAdder

import toffoli.toffoli as Toffoli

toffoli = Toffoli.logicalAND(True)
logicalAND = toffoli.logicalAND
uncomputation = toffoli.uncomputation

class InplaceAdder(BaseAdder):
    def __init__(self, is_metric_mode=False):
        super().__init__(is_metric_mode)


    def create(self, a, b, is_metric_mode=False):
        self.A, self.B = a, b
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
        g_round_rev = []
        c_round = []
        c_round_rev = []
        p_round_uncom = []
        mid_round = []
        re_p_round = []
        re_p_round_uncom = []
        g_round_uncom = []
        g_round_uncom_rev = []
        c_round_uncom = []
        c_round_uncom_rev = []
        last_round = []

        length = n - self.w(n) - floor(log2(n))
        ancilla1 = [cirq.NamedQubit("z" + str(i)) for i in range(n)]  # z[1] ~ z[n] 저장
        ancilla2 = [cirq.NamedQubit("ancilla" + str(i)) for i in range(length)] # 논문에서 X라고 지칭되는 ancilla

        and_len = 4*n -self.w(n) -floor(log2(n)) -self.w(n-1) -floor(log2(n-1)) -4
        and_len2 = n -self.w(n-1) -floor(log2(n-1)) -1
        and_ancilla = [cirq.NamedQubit("logical_ancilla" + str(i)) for i in range(and_len)]
        and_ancilla2 = [cirq.NamedQubit("logical_ancilla_2" + str(i)) for i in range(and_len2)]
        and_idx = 0


        # Init round
        for i in range(n):
            init.append(logicalAND(self.A[i], self.B[i], ancilla1[i])) # ancilla1[0] == Z[1]
            init.append(cirq.CNOT(self.A[i], self.B[i]))

        # P-round
        # print("P-rounds")
        idx = 0  # ancilla idx
        tmp = 0
        for t in range(1, int(log2(n))):
            pre = tmp
            for m in range(1, self.l(n, t)):
                if t == 1:
                    p_round.append(logicalAND(self.B[2*m], self.B[2*m+1], ancilla2[idx]))
                    #print(2*m,2*m+1,idx)
                else:
                    p_round.append(logicalAND(ancilla2[pre-1+2*m], ancilla2[pre-1+2*m+1], ancilla2[idx]))
                    # print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx)
                if m == 1:
                    tmp = idx
                idx += 1

        # G-round
        # print("G-rounds")
        pre = 0  # The number of cumulative p(t-1)
        idx = 0  # ancilla idx
        for t in range(1, int(log2(n))+1):
            for m in range(self.l(n, t)):
                if t == 1:
                    g_round.append(logicalAND(ancilla1[int(pow(2, t)*m + pow(2, t-1))-1], self.B[2 * m + 1], and_ancilla[and_idx]))
                    g_round.append(cirq.CNOT(and_ancilla[and_idx], ancilla1[int(pow(2, t) * (m + 1)) - 1]))
                    #g_round.append(uncomputation(ancilla1[int(pow(2, t)*m + pow(2, t-1))-1], self.B[2 * m + 1], and_ancilla[and_idx]))
                    g_round_rev.append(uncomputation(ancilla1[int(pow(2, t)*m + pow(2, t-1))-1], self.B[2 * m + 1], and_ancilla[and_idx]))
                    #print(int(pow(2, t) * m + pow(2, t - 1)) - 1,2 * m + 1,int(pow(2, t) * (m + 1)) - 1)
                else:
                    # print(int(pow(2, t) * m + pow(2, t - 1)) - 1,idx+2*m,int(pow(2, t) * (m + 1)) - 1)
                    g_round.append(logicalAND(ancilla1[int(pow(2, t)*m + pow(2, t-1))-1], ancilla2[idx+2*m], and_ancilla[and_idx]))
                    g_round.append(cirq.CNOT(and_ancilla[and_idx], ancilla1[int(pow(2, t)*(m+1))-1]))
                    #g_round.append(uncomputation(ancilla1[int(pow(2, t)*m + pow(2, t-1))-1], ancilla2[idx+2*m], and_ancilla[and_idx]))
                    g_round_rev.append(uncomputation(ancilla1[int(pow(2, t)*m + pow(2, t-1))-1], ancilla2[idx+2*m], and_ancilla[and_idx]))
                and_idx += 1
            if t != 1:
                pre = pre + self.l(n, t - 1) - 1
                idx = pre

        # C-round
        # print("C-rounds")
        if int(log2(n)) - 1 == int(log2(2 * n / 3)):
            iter = self.l(n, int(log2(n)) - 1) - 1
        else:
            iter = 0
        pre = 0
        for t in range(int(log2(2*n/3)),0,-1):
            for m in range(1,self.l((n-pow(2,t-1)), t)+1):
                if t == 1:
                    # print(int(pow(2, t) * m) - 1,2 * m,int(pow(2, t) * m + pow(2, t - 1)) - 1)
                    c_round.append(logicalAND(ancilla1[int(pow(2, t) * m)-1], self.B[2 * m], and_ancilla[and_idx]))
                    c_round.append(cirq.CNOT(and_ancilla[and_idx], ancilla1[int(pow(2, t) * m + pow(2, t - 1))-1]))
                    #c_round.append(uncomputation(ancilla1[int(pow(2, t) * m)-1], self.B[2 * m], and_ancilla[and_idx]))
                    c_round_rev.append(uncomputation(ancilla1[int(pow(2, t) * m)-1], self.B[2 * m], and_ancilla[and_idx]))
                else:
                    if m == 1:
                        iter += self.l(n, t - 1) - 1
                        pre = length - 1 - iter
                    c_round.append(logicalAND(ancilla1[int(pow(2, t) * m)-1], ancilla2[pre + 2 * m], and_ancilla[and_idx]))
                    c_round.append(cirq.CNOT(and_ancilla[and_idx], ancilla1[int(pow(2, t) * m + pow(2, t - 1))-1]))
                    #c_round.append(uncomputation(ancilla1[int(pow(2, t) * m)-1], ancilla2[pre + 2 * m], and_ancilla[and_idx]))
                    c_round_rev.append(uncomputation(ancilla1[int(pow(2, t) * m)-1], ancilla2[pre + 2 * m], and_ancilla[and_idx]))
                    #print(int(pow(2, t) * m) - 1,pre + 2 * m,int(pow(2, t) * m + pow(2, t - 1)) - 1)
                and_idx += 1

        # P-round uncompute
        # print("P-inverse round")
        pre = 0
        iter = self.l(n, int(log2(n)) - 1) - 1
        iter2 = 0  # for idx
        idx = 0
        for t in reversed(range(1, int(log2(n)))):
            for m in range(1, self.l(n, t)):
                if t == 1:
                    p_round_uncom.append(uncomputation(self.B[2 * m], self.B[2 * m + 1], ancilla2[m - t]))
                    # print(2*m, 2*m+1, m-t)
                else:
                    if m == 1:
                        iter += self.l(n, t - 1) - 1  # p(t-1) last idx
                        pre = length - iter
                        iter2 += (self.l(n, t) - 1)
                        idx = length - iter2
                    p_round_uncom.append(uncomputation(ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1],
                                 ancilla2[idx - 1 + m]))
                    # print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx-1+m)

        # mid round
        mid_round.append(cirq.CNOT(ancilla1[i-1], self.B[i]) for i in range(1, n))
        mid_round.append(cirq.X(self.B[i]) for i in range(n-1))
        mid_round.append(cirq.CNOT(self.A[i], self.B[i]) for i in range(1, n-1))

        ### Step 7. Section3 in reverse. (n-1)bit adder ###

        # re_p_round
        # print("P-round reverse")
        idx = 0  # ancilla idx
        tmp = 0
        for t in range(1, int(log2(n - 1))):
            pre = tmp
            for m in range(1, self.l(n - 1, t)):
                if t == 1:
                    # print(2 * m, 2 * m + 1, idx)
                    re_p_round.append(logicalAND(self.B[2 * m], self.B[2 * m + 1], and_ancilla2[idx]))
                else:
                    # print(pre - 1 + 2 * m, pre - 1 + 2 * m + 1, idx)
                    re_p_round.append(logicalAND(and_ancilla2[pre - 1 + 2 * m], and_ancilla2[pre - 1 + 2 * m + 1], and_ancilla2[idx]))
                if m == 1:
                    tmp = idx
                idx += 1

        # C-round uncom
        # print("C-inv-rounds")
        pre = 0
        for t in reversed(range(int(log2(2 * (n - 1) / 3)), 0, -1)):
            idx = pre  # ancilla2 idx
            # print("t = ", t)
            for m in range(1, self.l(((n - 1) - pow(2, t - 1)), t) + 1):
                if t == 1:
                    # print(int(pow(2, t) * m) - 1, 2 * m, int(pow(2, t) * m + pow(2, t - 1)) - 1)
                    c_round_uncom.append(logicalAND(ancilla1[int(pow(2, t) * m) - 1], self.B[2 * m], and_ancilla[and_idx]))
                    c_round_uncom.append(cirq.CNOT(and_ancilla[and_idx], ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1]))
                    #c_round_uncom.append(uncomputation(ancilla1[int(pow(2, t) * m) - 1], self.B[2 * m], and_ancilla[and_idx]))
                    c_round_uncom_rev.append(uncomputation(ancilla1[int(pow(2, t) * m) - 1], self.B[2 * m], and_ancilla[and_idx]))
                else:
                    # print(int(pow(2, t) * m) - 1, idx - 1 + 2 * m, int(pow(2, t) * m + pow(2, t - 1)) - 1)
                    c_round_uncom.append(logicalAND(ancilla1[int(pow(2, t) * m) - 1],and_ancilla2[idx - 1 + 2 * m], and_ancilla[and_idx]))
                    c_round_uncom.append(cirq.CNOT(and_ancilla[and_idx], ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1]))
                    #c_round_uncom.append(uncomputation(ancilla1[int(pow(2, t) * m) - 1],ancilla2[idx - 1 + 2 * m], and_ancilla[and_idx]))
                    c_round_uncom_rev.append(uncomputation(ancilla1[int(pow(2, t) * m) - 1],and_ancilla2[idx - 1 + 2 * m], and_ancilla[and_idx]))
                    if m == 1:
                        pre += self.l(n-1, t - 1) - 1
                and_idx += 1

        # G-round uncom
        # print("G-inv-rounds")
        pre = 0
        idx = int(log2(n-1))
        iter = 0
        for t in reversed(range(1, int(log2(n - 1)) + 1)):
            for m in range(self.l(n - 1, t)):
                if t == 1:
                    # print(int(pow(2, t) * m + pow(2, t - 1)) - 1,2 * m + 1,int(pow(2, t) * (m + 1)) - 1)
                    g_round_uncom.append(logicalAND(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], self.B[2 * m + 1],and_ancilla[and_idx]))
                    g_round_uncom.append(cirq.CNOT(and_ancilla[and_idx], ancilla1[int(pow(2, t) * (m + 1)) - 1]))
                    #g_round_uncom.append(uncomputation(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], self.B[2 * m + 1],and_ancilla[and_idx]))
                    g_round_uncom_rev.append(uncomputation(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], self.B[2 * m + 1],and_ancilla[and_idx]))
                else:
                    if m == 0:
                        iter += self.l(n-1, idx - 1) - 1  # p(t-1) last idx
                        pre = and_len2 - iter
                        idx -= 1
                    # print(int(pow(2, t) * m + pow(2, t - 1)) - 1, pre - 1 + 2 * m + 1, int(pow(2, t) * (m + 1)) - 1)
                    g_round_uncom.append(logicalAND(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], and_ancilla2[pre - 1 + 2 * m + 1],and_ancilla[and_idx]))
                    g_round_uncom.append(cirq.CNOT(and_ancilla[and_idx],ancilla1[int(pow(2, t) * (m + 1)) - 1]))
                    #g_round_uncom.append(uncomputation(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[pre - 1 + 2 * m + 1],and_ancilla[and_idx]))
                    g_round_uncom_rev.append(uncomputation(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], and_ancilla2[pre - 1 + 2 * m + 1],and_ancilla[and_idx]))
                and_idx += 1

        # re_p_round uncom
        # print("P-inverse round reverse")
        pre = 0
        iter = self.l(n-1, int(log2(n-1))-1) - 1 # 마지막 pt의 개수
        iter2 = 0
        idx = 0
        for t in reversed(range(1, int(log2(n - 1)))):
            # print("t=",t)
            for m in range(1, self.l(n - 1, t)):
                if t == 1:
                    re_p_round_uncom.append(uncomputation(self.B[2 * m], self.B[2 * m + 1], and_ancilla2[m - t]))
                    # print(2*m,2*m+1,m-t)
                else:
                    if m == 1:
                        iter += self.l(n-1, t - 1) - 1  # p(t-1) last idx
                        pre = and_len2 - iter
                        iter2 += self.l(n-1, t) - 1
                        idx = and_len2 - iter2
                    re_p_round_uncom.append(uncomputation(and_ancilla2[pre - 1 + 2 * m], and_ancilla2[pre - 1 + 2 * m + 1], and_ancilla2[idx - 1 + m]))
                    # print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx-1+m)

        # last round
        last_round.append(cirq.CNOT(self.A[i], self.B[i]) for i in range(1, n-1))
        last_round.append(uncomputation(self.A[i], self.B[i], ancilla1[i]) for i in range(n - 1))
        last_round.append(cirq.X(self.B[i]) for i in range(n - 1))

        circuit = cirq.Circuit()
        # Init
        circuit += init

        # P-round
        circuit += p_round

        # G-round
        circuit += g_round
        circuit += g_round_rev

        # C-round
        circuit += c_round
        circuit += c_round_rev

        # P-inverse
        circuit += p_round_uncom

        # mid round
        circuit += mid_round

        circuit += re_p_round
        circuit += c_round_uncom
        circuit += c_round_uncom_rev
        circuit += g_round_uncom
        circuit += g_round_uncom_rev
        circuit += re_p_round_uncom
        circuit += last_round

        result = []

        for k in self.B:
            result.append(k)
        result.append(ancilla1[-1])

        return circuit, result
        #return circuit, result, ancilla1, ancilla2
