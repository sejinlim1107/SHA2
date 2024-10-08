import cirq
import cirqOnqiskit
import math
import CSA.inDraper as inDraper

from base_tree_adder import BaseTreeAdder



class DaddaTreeAdder(BaseTreeAdder):

    def apply_adders_and_handle_carry(self, w, circuit):
        t = len(self.inputs)
        num = 0
        stack = []
        j = 1
        d = 2
        while t > d:
            if int(1.5 * d) == t:
                break
            else:
                j += 1
                d = int(1.5 * d)

        while j > 0:
            j -= 1
            i = 0
            while i < self.n:
                w_tmp2 = []
                if len(w[i]) > d:
                    t = len(w[i]) - d
                    while t > 0:
                        if t == 1:
                            a = w[i].pop(0)
                            b = w[i].pop(0)
                            carry = cirq.NamedQubit("csa_carry" + str(num))
                            num += 1
                            stack.append([a, b, carry])
                            circuit.append(self.QHA(a, b, carry))
                            w[i].insert(0, b)
                            w_tmp2.append(carry)
                            t -= 1
                        else:
                            a = w[i].pop(0)
                            b = w[i].pop(0)
                            c = w[i].pop(0)
                            carry = cirq.NamedQubit("csa_carry" + str(num))
                            num += 1
                            stack.append([a, b, c, carry])
                            circuit.append(self.QFA(a, b, c, carry))
                            w[i].insert(0, c)
                            w_tmp2.append(carry)
                            t -= 2

                    if i == self.n - 1:
                        w.append(w_tmp2)
                        self.n += 1
                    else:
                        w[i + 1].extend(w_tmp2)

                i += 1
            d = math.ceil(d / 1.5)

        return circuit, w, stack, num


    def transfer_to_rca_components(self, w, num):
        rca_A = []
        rca_B = []
        R = []
        while len(w):
            if len(w[0]) == 1:
                if len(w) == 1:
                    rca_A.append(w.pop(0).pop())
                    rca_B.append(cirq.NamedQubit("csa_carry" + str(num)))
                    num += 1
                else:
                    R.append(w.pop(0).pop())
            elif len(w[0]) == 2:
                tmp = w.pop(0)
                rca_A.append(tmp.pop(0))
                rca_B.append(tmp.pop())

        return w, num, rca_A, rca_B, R

    def apply_adder(self, circuit, rca_A, rca_B):
        add_circuit, result = self.Adder.create(rca_A, rca_B, self.is_metric_mode)
        circuit.append(add_circuit.all_operations())

        return circuit, result

    def apply_final_cnot(self, circuit, w, num):
        circuit.append(cirq.CNOT(w[0].pop(), cirq.NamedQubit("csa_carry" + str(num))))
        w[0].append(cirq.NamedQubit("csa_carry" + str(num)))
        num += 1
        return circuit, w, num

    def reverse_adders(self, circuit, stack, rca_B):
        while len(stack):
            tmp = stack.pop()
            if self.adder_type == 'InplaceAdder':
                tmp2 = [tmp[-2], tmp[-1]]
                if len(list(set(rca_B) & set(tmp2))) == 0:
                    if len(tmp) == 3:
                        circuit.append(self.QHA_R(tmp[0], tmp[1], tmp[2]))
                    if len(tmp) == 4:
                        circuit.append(self.QFA_R(tmp[0], tmp[1], tmp[2], tmp[3]))

                elif len(list(set(rca_B) & set(tmp2))) == 1:
                    if len(list(set(rca_B) & set([tmp[-1]]))) == 1:
                        if len(tmp) == 3:
                            circuit.append(cirq.CNOT(tmp[0], tmp[1]))
                        if len(tmp) == 4:
                            circuit.append(cirq.CNOT(tmp[0], tmp[2]))
                            circuit.append(cirq.CNOT(tmp[1], tmp[2]))
            else:
                if (len(tmp) == 3):
                    circuit.append(self.QHA_R(tmp[0], tmp[1], tmp[2]))
                if (len(tmp) == 4):
                    circuit.append(self.QFA_R(tmp[0], tmp[1], tmp[2], tmp[3]))

        return circuit

    def construct_circuit(self):
        circuit, w = self.initialize_circuit_and_qubits()

        circuit, w, stack, num = self.apply_adders_and_handle_carry(w, circuit)
        if self.adder_type == 'InplaceAdder':
            circuit, w, num = self.apply_final_cnot(circuit, w, num)
        w, num, rca_A, rca_B, R= self.transfer_to_rca_components(w, num)

        circuit, result = self.apply_adder(circuit, rca_A, rca_B)
        circuit = self.reverse_adders(circuit, stack, rca_B+R)

        return circuit, result


if __name__ == '__main__':
    n = 3

    A = [cirq.NamedQubit("IN0_" + str(i)) for i in range(n)]
    B = [cirq.NamedQubit("IN1_" + str(i)) for i in range(n)]
    C = [cirq.NamedQubit("IN2_" + str(i)) for i in range(n)]
    D = [cirq.NamedQubit("IN3_" + str(i)) for i in range(n)]
    E = [cirq.NamedQubit("IN4_" + str(i)) for i in range(n)]

    circuit = cirq.Circuit()

    circuit.append(cirq.X(A[0]))
    circuit.append(cirq.X(A[1]))
    circuit.append(cirq.X(A[2]))
    circuit.append(cirq.X(B[0]))
    circuit.append(cirq.X(B[1]))
    circuit.append(cirq.X(B[2]))
    circuit.append(cirq.X(C[0]))
    circuit.append(cirq.X(C[1]))
    circuit.append(cirq.X(C[2]))
    '''
    
    circuit.append(cirq.X(D[0]))
    circuit.append(cirq.X(D[1]))
    #circuit.append(cirq.X(D[2]))
    circuit.append(cirq.X(E[0]))
    circuit.append(cirq.X(E[1]))
    #circuit.append(cirq.X(E[2]))
    '''

    inputs = [A, B, C]
    is_metric_mode = True
    #adder, toffoli_type = takahashi.InplaceAdder(True, 'ZERO_ANCILLA_TDEPTH_3'), 'logicalAND'
    adder, toffoli_type = inDraper.InplaceAdder(True, 'ZERO_ANCILLA_TDEPTH_3'), 'logicalAND'
    #adder, toffoli_type = outDraper.InplaceAdder(True, 'ZERO_ANCILLA_TDEPTH_3'), 'logicalAND'

    #adder, toffoli_type = gidney.InplaceAdder(is_metric_mode=True), 'logicalAND'
    #adder, toffoli_type = inDraper_logicalAND.InplaceAdder(is_metric_mode=True), 'logicalAND'
    #adder, toffoli_type = outDraper_logicalAND.InplaceAdder(is_metric_mode=True), 'logicalAND'

    k = DaddaTreeAdder(n, inputs, adder, is_metric_mode, toffoli_type)
    #k=DaddaTreeAdder(n,inputs, inDraper, True)
    circuit.append(k.circuit.all_operations())

    print(circuit)

    circuit.append(cirq.measure(k.result, key="result"))


    simul = cirq.Simulator()
    results = simul.simulate(circuit)
    for key, value in results.measurements.items():
        print(key, ":", value)
    print(results.measurements)



    qasm_circuit = cirqOnqiskit.run_cirq_circuit_on_qiskit(circuit, circuit.all_qubits(), 'qasm_simulator')
    t_depth = qasm_circuit.depth(lambda gate: gate[0].name in ['t', 'tdg'])
    op_count = qasm_circuit.count_ops()
    print(op_count)
    t_count = op_count['tdg']+op_count['t']
    q_count = qasm_circuit.width()
    print("t depth:", t_depth)
    print("t count:", t_count)
    print("q count:", q_count)