import cirq

class logicalAND():
    def __init__(self, is_metric_mode=False):
        super().__init__()
        self.is_metric_mode = is_metric_mode
    def logicalAND(self, x, y, A):
        yield [cirq.H(A)]
        yield [cirq.T(A)]
        yield [cirq.CNOT(x, A)]
        yield [cirq.CNOT(y, A)]
        yield [cirq.CNOT(A, x)]
        yield [cirq.CNOT(A, y)]
        yield [(cirq.T ** -1)(x), (cirq.T ** -1)(y), cirq.T(A)]
        yield [cirq.CNOT(A, x), cirq.CNOT(A, y)]
        yield [cirq.H(A)]
        yield [cirq.S(A)]


    def uncomputation(self, x, y, xy):
        yield [cirq.H(xy)]
        if self.is_metric_mode:
            yield [cirq.CZ(x, y)]
        else:
            yield [cirq.measure(xy, key=xy.name)]
            yield [cirq.CZ(x, y).with_classical_controls(xy.name)]
        #yield [(cirq.T ** -1)(x)]

class ToffoliDecomp():
    def __init__(self):
        self.gate_dict = {
            'ZERO_ANCILLA_TDEPTH_3': self.ZERO_ANCILLA_TDEPTH_3,
            'TOFFOLI': cirq.TOFFOLI,
        }
    #Equation 3 from arxiv:1210.0974v2
    def ZERO_ANCILLA_TDEPTH_3(self, x, y, z):
        yield [cirq.H(z)]
        yield [(cirq.T ** -1)(x), cirq.T(y), cirq.T(z)]
        yield [cirq.CNOT(x, y)]
        yield [cirq.CNOT(z, x)]
        yield [(cirq.T ** -1)(x), cirq.CNOT(y, z)]
        yield [cirq.CNOT(y, x)]
        yield [(cirq.T ** -1)(x), (cirq.T ** -1)(y), cirq.T(z)]
        yield [cirq.CNOT(z, x)]
        yield [cirq.S(x), cirq.CNOT(y, z)]
        yield [cirq.CNOT(x, y), cirq.H(z)]

    def get_gate(self, gate_type):
        return self.gate_dict.get(gate_type, cirq.TOFFOLI)




