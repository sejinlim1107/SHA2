# TODO: Document the code !!
"""
  Implementation of the carry lookahead adder
  arxiv preprint 0406142
  A logarithmic-depth quantum carry-lookahead adder
"""
import cirq
from adder.BaseAdder import BaseAdder

import cirqOnqiskit

from math import floor, log2
import toffoli.toffoli

class OutplaceAdder(BaseAdder):
    def __init__(self, is_metric_mode=False, tofooli_type='TOFFOLI'):
        super().__init__(is_metric_mode)
        self.Z = None
        self.Toffoli = toffoli.toffoli.ToffoliDecomp().get_gate(tofooli_type)

    def create(self, a, b, is_metric_mode=False):
        self.A, self.B = a, b
        self.Z = [cirq.NamedQubit("Z" + str(i)) for i in range(len(self.A) + 1)]
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


        length = n - self.w(n) - floor(log2(n))
        ancilla = [cirq.NamedQubit("a" + str(i)) for i in range(length)]  # 논문에서 X라 지칭

        # Init round
        for i in range(n):
            init.append(self.Toffoli(self.A[i], self.B[i], self.Z[i + 1]))

        for i in range(1,n):
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
                    p_round.append(self.Toffoli(self.B[2*m], self.B[2*m+1], ancilla[idx]))
                else:
                    # print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx)
                    p_round.append(self.Toffoli(ancilla[pre-1+2*m], ancilla[pre-1+2*m+1], ancilla[idx]))
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
                    g_round.append(self.Toffoli(self.Z[int(pow(2, t)*m + pow(2, t-1))], self.B[2 * m + 1], self.Z[int(pow(2, t)*(m+1))]))
                else:
                    #print(int(pow(2, t) * m + pow(2, t - 1)), idx+2*m, int(pow(2, t) * (m + 1)))
                    g_round.append(self.Toffoli(self.Z[int(pow(2, t)*m + pow(2, t-1))], ancilla[idx+2*m], self.Z[int(pow(2, t)*(m+1))]))
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
                        self.Toffoli(self.Z[int(pow(2, t) * m)], self.B[2 * m], self.Z[int(pow(2, t) * m + pow(2, t - 1))]))
                else:
                    if m == 1:
                        iter += self.l(n, t - 1) - 1
                        pre = length - 1 - iter
                    # print(int(pow(2, t) * m),pre + 2 * m,int(pow(2, t) * m + pow(2, t-1)))
                    c_round.append(self.Toffoli(self.Z[int(pow(2, t) * m)], ancilla[pre + 2 * m],self.Z[int(pow(2, t) * m + pow(2, t - 1))]))

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
                    p_round_uncom.append(self.Toffoli(self.B[2 * m], self.B[2 * m + 1], ancilla[m - t]))
                else:
                    if m == 1:
                        iter += self.l(n, t - 1) - 1  # p(t-1) last idx
                        pre = length - iter
                        iter2 += (self.l(n, t) - 1)
                        idx = length - iter2
                    # print(pre - 1 + 2 * m,pre - 1 + 2 * m + 1,idx-1+m)
                    p_round_uncom.append(self.Toffoli(ancilla[pre - 1 + 2 * m], ancilla[pre - 1 + 2 * m + 1], ancilla[idx - 1 + m]))


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

        # C-round
        circuit += c_round

        # P-inverse
        circuit += p_round_uncom

        # Last round
        circuit += last_round

        result = []

        for k in self.Z:
            result.append(k)

        return circuit, result

if __name__ == '__main__':
    n = 512

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
    adder = OutplaceAdder(True, "Toffoli")
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
