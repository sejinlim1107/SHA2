import cirq

from BaseAdder import BaseAdder
import toffoli as Toffoli

toffoli = Toffoli.logicalAND(True)
logicalAND = toffoli.logicalAND
uncomputation = toffoli.uncomputation


#Gidney Adder
def Round_constant_XOR(circuit, rc, qubits, n):
    for i in range(n):
        if ((rc >> i) & 1):
            circuit.append(cirq.X(qubits[i]))

class InplaceAdder(BaseAdder):
    def __init__(self, is_metric_mode=False):
        super().__init__(is_metric_mode)

    def create(self, a, b, is_metric_mode=False):
        self.A, self.B = a, b
        self.circuit, self.result = self.construct_circuit()
        return self.circuit, self.result

    def construct_circuit(self):
        n = len(self.A)
        C = [cirq.NamedQubit("C_" + self.id + "_" + str(i)) for i in range(n)]  # append the id to the qubit name
        operations = []

        for k in range(n):
            if(k==0):
                operations.append(logicalAND(self.A[k], self.B[k], C[k]))

            else:
                operations.append([cirq.CNOT(C[k-1], self.A[k]), cirq.CNOT(C[k-1], self.B[k])])
                if(k!=n-1):
                    operations.append(logicalAND(self.A[k], self.B[k], C[k]))
                    operations.append(cirq.CNOT(C[k-1], C[k]))
                else:
                    operations.append(logicalAND(self.A[k], self.B[k], C[-1]))
                    operations.append(cirq.CNOT(C[k-1], C[-1]))
                    operations.append(cirq.CNOT(C[k-1], self.A[k]))

        for k in reversed(range(n-1)):
            if(k==0):
                operations.append(uncomputation(self.A[k], self.B[k], C[k]))
            else:
                operations.append(cirq.CNOT(C[k-1], C[k]))
                operations.append(uncomputation(self.A[k], self.B[k], C[k]))
                operations.append(cirq.CNOT(C[k-1], self.A[k]))

        operations.append(cirq.CNOT(self.A[k], self.B[k]) for k in range(n))

        circuit = cirq.Circuit()
        circuit.append(operations)

        # measure
        #circuit.append(measure(self.carry,key='carry'))
        result = []
        for k in self.B:
            result.append(k)
        result.append(C[-1])
        #circuit.append(measure(result, key='result'))

        return circuit, result


def adder_test(a, b, n):
    A = [cirq.NamedQubit("A" + str(i)) for i in range(n)]
    B = [cirq.NamedQubit("B" + str(i)) for i in range(n)]


    circuit = cirq.Circuit()
    Round_constant_XOR(circuit, a, A, n)  # 숫자, 큐빗, 길이
    Round_constant_XOR(circuit, b, B, n)
    adder = InplaceAdder(A, B)
    circuit.append(adder.circuit)
    circuit.append(cirq.measure(adder.result, key='result'))
    return circuit