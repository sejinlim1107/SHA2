"""
    Implementation of control adder from : arXiv:0910.2530, 2009
"""
import cirq
from adder.BaseAdder import BaseAdder

import cirqOnqiskit
import toffoli.toffoli

class InplaceAdder(BaseAdder):
    def __init__(self, is_metric_mode=False, tofooli_type = 'TOFFOLI'):
        super().__init__(is_metric_mode)
        self.Z = None
        self.nr_qubits = None
        self.Toffoli = toffoli.toffoli.ToffoliDecomp().get_gate(tofooli_type)

    def create(self, a, b, is_metric_mode=False):
        self.A, self.B = a, b
        self.Z = cirq.NamedQubit("Z" + self.id)
        self.nr_qubits = len(a)

        if self.nr_qubits > 1:
            self.circuit, self.result = self.construct_circuit()
        else:
            self.circuit, self.result = self.construct_circuit1()
        return self.circuit, self.result

    def construct_circuit1(self):
        op = []

        op.append(self.Toffoli(self.A[0], self.B[0], self.Z))
        op.append(cirq.CNOT(self.A[0], self.B[0]))

        circuit = cirq.Circuit()
        circuit.append(op)

        result = []
        for k in self.B:
            result.append(k)
        result.append(self.Z)

        return circuit, result

    def construct_circuit(self):
        n = len(self.A)
        op = []

        op.append(cirq.CNOT(self.A[i], self.B[i]) for i in range(1, n))
        op.append(cirq.CNOT(self.A[n-1],self.Z))
        op.append(cirq.CNOT(self.A[i], self.A[i+1]) for i in range(n-2,0,-1))
        op.append(self.Toffoli(self.A[i], self.B[i], self.A[i+1]) for i in range(n-1))
        op.append(self.Toffoli(self.A[n-1], self.B[n-1], self.Z))

        for i in range(n - 1, 0, -1):
            op.append(cirq.CNOT(self.A[i], self.B[i]))
            op.append(self.Toffoli(self.B[i-1], self.A[i-1], self.A[i]))
        op.append(cirq.CNOT(self.A[i], self.A[i+1]) for i in range(1,n-1))
        op.append(cirq.CNOT(self.A[i], self.B[i]) for i in range(n))

        # measure
        result = []
        for k in self.B:
            result.append(k)
        result.append(self.Z)

        circuit = cirq.Circuit()
        circuit.append(op)

        return circuit, result

if __name__ == '__main__':
    n = 10

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
