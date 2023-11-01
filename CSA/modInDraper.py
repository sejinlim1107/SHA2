# TODO: Document the code !!
"""
  Implementation of the carry lookahead adder
  arxiv preprint 0406142
  A logarithmic-depth quantum carry-lookahead adder
"""
import cirq
from math import floor, log2
from adder.BaseAdder import BaseAdder

import toffoli.toffoli
import cirqOnqiskit


class InplaceAdder(BaseAdder):
    def __init__(self, is_metric_mode=False, tofooli_type='TOFFOLI'):
        super().__init__(is_metric_mode)
        self.Toffoli = toffoli.toffoli.ToffoliDecomp().get_gate(tofooli_type)
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
        print("draper ", n)
        init = []
        p_round = []
        g_round = []
        c_round = []
        p_round_uncom = []
        mid_round = []
        re_p_round = []
        re_p_round_uncom = []
        g_round_uncom = []
        c_round_uncom = []
        last_round = []

        length = n-1 - self.w(n-1) - floor(log2(n-1))
        ancilla1 = [cirq.NamedQubit("z" + str(i)) for i in range(n-1)]
        ancilla2 = [cirq.NamedQubit("ancilla2" + str(i)) for i in range(length)]

        # Init round
        for i in range(n-1):
            init.append(self.Toffoli(self.A[i], self.B[i], ancilla1[i])) # ancilla1[0] == Z[1]
        for i in range(n):
            init.append(cirq.CNOT(self.A[i], self.B[i]))

        # P-round
        # print("P-rounds")
        idx = 0  # ancilla idx
        tmp = 0  # m=1일 때 idx 저장해두기
        for t in range(1, int(log2(n - 1))):
            pre = tmp  # (t-1)일 때의 첫번째 자리 저장
            # print("t ========== ",t)
            for m in range(1, self.l(n - 1, t)):
                if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                    p_round.append(self.Toffoli(self.B[2*m], self.B[2*m+1], ancilla2[idx]))
                    # print(2*m,2*m+1,idx)
                else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                    p_round.append(self.Toffoli(ancilla2[pre-1+2*m], ancilla2[pre-1+2*m+1], ancilla2[idx]))
                    # print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx)
                if m == 1:
                    tmp = idx
                idx += 1

        # G-round
        # print("G-rounds")
        pre = 0  # The number of cumulative p(t-1)
        idx = 0  # ancilla idx
        for t in range(1, int(log2(n - 1)) + 1):
            # print("t = ",t)
            for m in range(self.l(n - 1, t)):
                if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                    g_round.append(self.Toffoli(ancilla1[int(pow(2, t)*m + pow(2, t-1))-1], self.B[2 * m + 1], ancilla1[int(pow(2, t)*(m+1))-1]))
                    # print(int(pow(2, t) * m + pow(2, t - 1)) - 1,2 * m + 1,int(pow(2, t) * (m + 1)) - 1)
                else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                    # print(int(pow(2, t) * m + pow(2, t - 1)) - 1,idx+2*m,int(pow(2, t) * (m + 1)) - 1)
                    g_round.append(self.Toffoli(ancilla1[int(pow(2, t)*m + pow(2, t-1))-1], ancilla2[idx+2*m], ancilla1[int(pow(2, t)*(m+1))-1]))
            if t != 1:
                pre = pre + self.l(n - 1, t - 1) - 1
                idx = pre

        # C-round
        # print("C-rounds")
        if int(log2(n - 1)) - 1 == int(log2(2 * (n - 1) / 3)):  # p(t-1)까지 접근함
            iter = self.l(n - 1, int(log2(n - 1)) - 1) - 1  # 마지막 pt의 개수
        else:  # p(t)까지 접근함
            iter = 0
        pre = 0  # (t-1)일 때의 첫번째 idx
        for t in range(int(log2(2 * (n - 1) / 3)), 0, -1):
            # print("t=",t)
            for m in range(1, self.l(((n - 1) - pow(2, t - 1)), t) + 1):
                if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                    c_round.append(
                        self.Toffoli(ancilla1[int(pow(2, t) * m) - 1], self.B[2 * m],
                                     ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1]))
                else:
                    if m == 1:
                        iter += self.l(n - 1, t - 1) - 1
                        pre = length - 1 - iter
                    c_round.append(self.Toffoli(ancilla1[int(pow(2, t) * m)-1], ancilla2[pre + 2 * m],ancilla1[int(pow(2, t) * m + pow(2, t - 1))-1]))

        # P-round uncompute
        # print("P-inverse round")
        pre = 0  # (t-1)일 때의 첫번째 idx
        iter = self.l(n - 1, int(log2(n - 1)) - 1) - 1  # 마지막 pt의 개수
        iter2 = 0  # for idx
        idx = 0
        for t in reversed(range(1, int(log2(n - 1)))):
            for m in range(1, self.l(n - 1, t)):
                if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                    p_round_uncom.append(self.Toffoli(self.B[2 * m], self.B[2 * m + 1], ancilla2[m - t]))
                    # print(2*m, 2*m+1, m-t)
                else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                    if m == 1:
                        iter += self.l(n - 1, t - 1) - 1  # p(t-1) last idx
                        pre = length - iter
                        iter2 += (self.l(n - 1, t) - 1)
                        idx = length - iter2
                    p_round_uncom.append(self.Toffoli(ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1],
                                                      ancilla2[idx - 1 + m]))

        # mid round
        mid_round.append(cirq.CNOT(ancilla1[i-1], self.B[i]) for i in range(1, n))
        mid_round.append(cirq.X(self.B[i]) for i in range(n-1))
        mid_round.append(cirq.CNOT(self.A[i], self.B[i]) for i in range(1, n-1))

        ### Step 7. Section3 in reverse. (n-1)bit adder ###

        # re_p_round
        # print("P-round reverse")
        iter = 0
        pre = 0
        idx = 0  # ancilla idx

        for t in range(1, int(log2(n - 1))):
            if t > 1:
                pre = iter
                iter += self.l(n-1, t - 1) - 1  # ancilla idx. n is right.
                idx = iter
            for m in range(1, self.l(n - 1, t)):
                if t == 1:
                    # print(2 * m, 2 * m + 1, idx)
                    re_p_round.append(self.Toffoli(self.B[2 * m], self.B[2 * m + 1], ancilla2[idx]))
                    idx += 1
                else:
                    # print(pre - 1 + 2 * m, pre - 1 + 2 * m + 1, idx)
                    re_p_round.append(self.Toffoli(ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx]))
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
                    c_round_uncom.append(self.Toffoli(ancilla1[int(pow(2, t) * m) - 1], self.B[2 * m],
                                 ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1]))
                else:
                    # print(int(pow(2, t) * m) - 1, idx - 1 + 2 * m, int(pow(2, t) * m + pow(2, t - 1)) - 1)
                    c_round_uncom.append(self.Toffoli(ancilla1[int(pow(2, t) * m) - 1],
                                 ancilla2[idx - 1 + 2 * m], ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1]))
                    if m == 1:
                        pre += self.l(n-1, t-1) -1

        # G-round uncom
        # print("G-inv-rounds")
        pre = 0
        idx_t = int(log2(n-1))
        iter = 0
        for t in reversed(range(1, int(log2(n - 1)) + 1)):
            for m in range(self.l(n - 1, t)):
                if t == 1:
                    # print(int(pow(2, t) * m + pow(2, t - 1)) - 1,2 * m + 1,int(pow(2, t) * (m + 1)) - 1)
                    g_round_uncom.append(self.Toffoli(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], self.B[2 * m + 1],
                                 ancilla1[int(pow(2, t) * (m + 1)) - 1]))
                else:
                    if m == 0:
                        iter += self.l(n-1, idx_t - 1) - 1  # p(t-1) last idx
                        pre = length - iter
                        idx_t -= 1

                    # print(int(pow(2, t) * m + pow(2, t - 1)) - 1, pre - 1 + 2 * m + 1, int(pow(2, t) * (m + 1)) - 1)
                    g_round_uncom.append(self.Toffoli(ancilla1[int(pow(2, t) * m + pow(2, t - 1)) - 1], ancilla2[pre - 1 + 2 * m + 1],
                                 ancilla1[int(pow(2, t) * (m + 1)) - 1]))

        # re_p_round uncom
        # print("P-inverse round reverse")
        pre = 0  # (t-1)일 때의 첫번째 idx
        idx_t = int(log2(n - 1)) - 1  # n-1이 아니라 n일 때의 t의 범위
        iter = self.l(n - 1, idx_t) - 1
        iter2 = 0  # for idx
        for t in reversed(range(1, int(log2(n - 1)))):
            # print("t=",t)
            for m in range(1, self.l(n - 1, t)):
                if t == 1:  # B에 저장되어있는 애들로만 연산 가능
                    re_p_round_uncom.append(self.Toffoli(self.B[2 * m], self.B[2 * m + 1], ancilla2[m - t]))
                    # print(2*m,2*m+1,m-t)
                else:  # t가 1보다 클 때는 ancilla에 저장된 애들도 이용해야함
                    if m == 1:
                        iter += self.l(n - 1, idx_t - 1) - 1  # p(t-1) last idx
                        pre = length - iter
                        iter2 += self.l(n - 1, idx_t) - 1
                        idx = length - iter2
                        idx_t -= 1
                    re_p_round_uncom.append(self.Toffoli(ancilla2[pre - 1 + 2 * m], ancilla2[pre - 1 + 2 * m + 1], ancilla2[idx - 1 + m]))

        # last round
        last_round.append(cirq.CNOT(self.A[i], self.B[i]) for i in range(1, n-1))
        last_round.append(self.Toffoli(self.A[i], self.B[i], ancilla1[i]) for i in range(n - 1))
        last_round.append(cirq.X(self.B[i]) for i in range(n - 1))

        circuit = cirq.Circuit()
        # Init
        circuit += init

        # P-round
        circuit += p_round

        # G-round
        circuit += g_round

        # C-round
        circuit += c_round

        # P-inverse
        circuit += p_round_uncom

        # mid round
        circuit += mid_round

        circuit += re_p_round
        circuit += c_round_uncom
        circuit += g_round_uncom
        circuit += re_p_round_uncom
        circuit += last_round


        result = []

        for k in self.B:
            result.append(k)

        return circuit, result

if __name__ == '__main__':
    n = 32

    A = [cirq.NamedQubit("IN0_" + str(i)) for i in range(n)]
    B = [cirq.NamedQubit("IN1_" + str(i)) for i in range(n)]


    circuit = cirq.Circuit()
    '''
    circuit.append(cirq.X(A[0]))
    circuit.append(cirq.X(A[1]))
    circuit.append(cirq.X(A[2]))
    circuit.append(cirq.X(A[3]))
    circuit.append(cirq.X(B[0]))
    circuit.append(cirq.X(B[1]))
    circuit.append(cirq.X(B[2]))
    circuit.append(cirq.X(B[3]))
    '''
    adder = InplaceAdder(True, "Toffoli")
    c,r =adder.create(A, B)
    circuit.append(c)

    qasm_circuit = cirqOnqiskit.run_cirq_circuit_on_qiskit(circuit, circuit.all_qubits(), 'qasm_simulator')

    t_depth = qasm_circuit.depth(lambda gate: gate[0].name in ['t', 'tdg'])
    op_count = qasm_circuit.count_ops()
    t_count = op_count.get('tdg', 0) + op_count.get('t', 0)

    q_count = qasm_circuit.width()

    toffoli_depth = qasm_circuit.depth(lambda gate: gate[0].name in ['ccx'])
    op_count = qasm_circuit.count_ops()
    toffoli_count = op_count.get('ccx', 0)
    q_count = qasm_circuit.width()
    print(toffoli_depth, toffoli_count, q_count)

