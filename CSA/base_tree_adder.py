from abc import ABC, abstractmethod
import math
import cirq

import toffoli.toffoli as Toffloi
is_metric_mode = True


class BaseTreeAdder(ABC):
    def __init__(self, n, inputs, Adder, is_metric_mode=False, toffoli_type = 'TOFFOLI'):
        self.n, self.inputs, self.Adder= n, inputs, Adder
        self.use_logicalAND = False
        self.Toffoli = self.Toffoli = Toffloi.ToffoliDecomp().get_gate('TOFFOLI')
        if toffoli_type == 'logicalAND':
            self.use_logicalAND = True
        else: 
            self.Toffoli = Toffloi.ToffoliDecomp().get_gate(toffoli_type)

        self.adder_type = type(Adder).__name__
        self.is_metric_mode = is_metric_mode
        self.logicalAND = Toffloi.logicalAND(is_metric_mode).logicalAND
        self.uncomputation = Toffloi.logicalAND(is_metric_mode).uncomputation
        self.circuit, self.result = self.construct_circuit()

    def QHA(self, a, b, c):
        if self.use_logicalAND:
            yield self.logicalAND(a, b, c)
        else:
            yield [self.Toffoli(a, b, c)]
        yield [cirq.CNOT(a, b)]

    def QHA_R(self, a, b, c):
        yield [cirq.CNOT(a, b)]
        if self.use_logicalAND:
            yield self.uncomputation(a, b, c)
        else:
            yield [self.Toffoli(a, b, c)]

    def QFA(self, a, b, c, d):
        yield [cirq.CNOT(a, b)]
        yield [cirq.CNOT(a, c)]
        if self.use_logicalAND:
            yield self.logicalAND(b, c, d)
        else:
            yield [self.Toffoli(b, c, d)]
        yield [cirq.CNOT(a, b)]
        yield [cirq.CNOT(a, d)]
        yield [cirq.CNOT(b, c)]

    def QFA_R(self, a, b, c, d):
        yield [cirq.CNOT(a, b)]
        yield [cirq.CNOT(a, c)]
        if self.use_logicalAND:
            yield self.uncomputation(b, c, d)
        else:
            yield [self.Toffoli(b, c, d)]
        yield [cirq.CNOT(a, b)]
        yield [cirq.CNOT(a, d)]
        yield [cirq.CNOT(b, c)]

    '''
    def QHA(self, a, b, c):
        yield [cirq.TOFFOLI(a, b, c)]
        yield [cirq.CNOT(a, b)]

    def QHA_R(self, a, b, c):
        yield [cirq.CNOT(a, b)]
        yield [cirq.TOFFOLI(a, b, c)]

    def QFA(self, a, b, c, d):
        yield [cirq.TOFFOLI(b, c, d)]
        yield [cirq.CNOT(b, c)]
        yield [cirq.TOFFOLI(a, c, d)]
        yield [cirq.CNOT(a, c)]

    def QFA_R(self, a, b, c, d):
        yield [cirq.CNOT(a, c)]
        yield [cirq.TOFFOLI(a, c, d)]
        yield [cirq.CNOT(b, c)]
        yield [cirq.TOFFOLI(b, c, d)]
    '''
    def initialize_circuit_and_qubits(self):
        # Initialize the circuit
        circuit = cirq.Circuit()

        # Initialize qubits by re-structuring inputs for each bit position
        w = []
        for i in range(self.n):
            temp_qubits = []
            for input_list in self.inputs:
                temp_qubits.append(input_list[i])
            w.append(temp_qubits)

        return circuit, w





    @abstractmethod
    def reverse_adders(self):
        pass


    @abstractmethod
    def construct_circuit(self):
        pass
