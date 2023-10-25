import cirq
from adder.BaseAdder import BaseAdder

import cirqOnqiskit

import toffoli.toffoli

import math

import random

def brent_kung_tree(n):
    operations = []

    # 첫 번째 단계: 기본 연산
    layer = [(i, i + 1) for i in range(0, n - 1, 2)]
    operations.append(layer)

    step = 2
    while step < n:
        layer = [(i - 1, min(i + step - 1, n - 1)) for i in range(step, n, step * 2) if i + step - 1 < n]
        if layer:
            operations.append(layer)
        step *= 2

    step //= 4
    while step >= 1:
        layer = [(i + step - 1, i + 2*step - 1) for i in range(step, n, 2 * step) if i + 2*step - 1 < n]
        if layer:
            operations.append(layer)
        step //= 2

    return operations



class OutplaceAdder(BaseAdder):
    def __init__(self, is_metric_mode=False, tofooli_type='TOFFOLI'):
        super().__init__(is_metric_mode)
        self.Toffoli = toffoli.toffoli.ToffoliDecomp().get_gate(tofooli_type)

    def create(self, a, b, is_metric_mode=False):
        self.A, self.B = a, b
        self.circuit, self.result = self.construct_circuit()
        return self.circuit, self.result

    def construct_circuit(self):

        def OR(list, a, b, c):
            list.append(cirq.X(a))
            list.append(cirq.X(b))
            list.append(self.Toffoli(a, b, c))
            list.append(cirq.X(a))
            list.append(cirq.X(b))
            list.append(cirq.X(c))


        n = len(self.A)


        # Step 1
        step1 = []
        for i in range(0, n, 1):
            step1.append(self.Toffoli(self.A[i], self.B[i], cirq.NamedQubit("ring_gl" + str(i))))
            step1.append(cirq.CNOT(self.A[i], self.B[i]))
            step1.append(cirq.CNOT(self.B[i], cirq.NamedQubit("ring_pl" + str(i))))
            step1.append(cirq.CNOT(cirq.NamedQubit("ring_gl" + str(i)), cirq.NamedQubit("ring_pl" + str(i))))


        # Step 2
        step2 = []
        step2_1 = []

        g = []
        g.append(cirq.NamedQubit("ring_gl0"))
        for i in range(1, n):
            g.append(cirq.NamedQubit("ring_g" + str(i)))

        for i in range(1, n, 2):
            OR(step2_1, cirq.NamedQubit("ring_gl" + str(i - 1)), cirq.NamedQubit("ring_gl" + str(i)),
                                      cirq.NamedQubit("ring_g" + str(i)))
        for i in range(2, n, 2):
            OR(step2_1, cirq.NamedQubit("ring_gl" + str(i - 1)), cirq.NamedQubit("ring_gl" + str(i)),
                                      cirq.NamedQubit("ring_g" + str(i)))


        step2_2 = []
        p = []
        p.append(cirq.NamedQubit("ring_pl" + str(0)))
        for i in range(1, n, 1):
            p.append(cirq.NamedQubit("ring_p" + str(i)))
        for i in range(1, n, 2):
            step2_2.append(self.Toffoli(cirq.NamedQubit("ring_pl" + str(i - 1)), cirq.NamedQubit("ring_pl" + str(i)),
                                      cirq.NamedQubit("ring_p" + str(i))))
        for i in range(2, n, 2):
            step2_2.append(self.Toffoli(cirq.NamedQubit("ring_pl" + str(i - 1)), cirq.NamedQubit("ring_pl" + str(i)),
                                        cirq.NamedQubit("ring_p" + str(i))))

        step2 += step2_1
        step2 += step2_2

        # Step 3
        step3 = []
        layer1 = brent_kung_tree(math.ceil(n/2))

        layer2 = brent_kung_tree(int(n / 2))
        #gx, px−1 ◦ gy, py−1 = gx + px−1 · gy, px−1 · py−1
        #G = gx + px−1 · gy
        #P = px−1 · py−1
        #Generate
        def generate1(list, px1, gy, k):
            # px1 · gy
            list.append(self.Toffoli(px1, gy,cirq.NamedQubit("ring_pg_" + k)))
            return cirq.NamedQubit("ring_pg_" + k)

        def generate2(list, gx2, pg, k):
            #gx + (px−1 · gy)
            OR(list, gx2, pg, cirq.NamedQubit("ring_G_" + k))
            return cirq.NamedQubit("ring_G_" + k)

        def propagate(list, px, py, k):
            list.append(self.Toffoli(px, py, cirq.NamedQubit("ring_P" + str(k))))
            return cirq.NamedQubit("ring_P" + str(k))

        numP = 0
        for i in range(0,len(layer1)):
            #gx + px−1 · gy, px−1 · py−1
            for pair in layer1[i]:

                pg = generate1(step3, p[(pair[1])*2-1], g[pair[0]*2], str(i)+"_"+str((pair[1])*2))
                g[(pair[1])*2] = generate2(step3, g[(pair[1])*2], pg, str(i)+"_"+str((pair[1])*2))

                if i==(len(layer1)-1):
                    pass
                else:
                    p[pair[1]*2-1] = propagate(step3, p[pair[1]*2-1], p[pair[0]*2-1],numP)
                    numP +=1

        for i in range(0,len(layer2)):
            #gx + px−1 · gy, px−1 · py−1
            for pair in layer2[i]:

                pg = generate1(step3, p[(pair[1]) * 2], g[pair[0] * 2+1], str(i)+"_"+str((pair[1])*2+1))
                g[(pair[1]) * 2+1] = generate2(step3, g[(pair[1]) * 2+1], pg, str(i)+"_"+str((pair[1])*2+1))

                if i==(len(layer2)-1):
                    pass
                else:
                    p[pair[1] * 2] = propagate(step3, p[pair[1] * 2], p[pair[0] * 2+1-1], numP)
                    numP += 1

        step4 = []
        for i in range(1, n, 1):
            step4.append(self.Toffoli(cirq.NamedQubit("ring_pl" + str(i - 1)), g[i - 1], self.B[i]))

        step4.append(self.Toffoli(cirq.NamedQubit("ring_pl" + str(n - 1)), g[n - 1], cirq.NamedQubit("ring_Sn")))

        # Step 5
        step5 = []
        step5 += reversed(step3)

        # Step 6
        step6 = []
        step6 += reversed(step2)

        # Step 7
        step7 = []
        for i in range(0, n, 1):
            step7.append(cirq.CNOT(cirq.NamedQubit("ring_gl" + str(i)), cirq.NamedQubit("ring_pl" + str(i))))
            step7.append(cirq.CNOT(self.A[i], cirq.NamedQubit("ring_pl" + str(i))))
            step7.append(
                self.Toffoli(self.A[i], cirq.NamedQubit("ring_pl" + str(i)), cirq.NamedQubit("ring_gl" + str(i))))
            step7.append(cirq.SWAP(cirq.NamedQubit("ring_pl" + str(i)), self.B[i]))
        '''
        circuit = cirq.Circuit()
        
        circuit += step3
        qasm_circuit = cirqOnqiskit.run_cirq_circuit_on_qiskit(circuit, circuit.all_qubits(), 'qasm_simulator')

        toffoli_depth = qasm_circuit.depth(lambda gate: gate[0].name in ['ccx'])
        op_count = qasm_circuit.count_ops()
        toffoli_count = op_count.get('ccx', 0)
        q_count = qasm_circuit.width()
        print(toffoli_depth, toffoli_count, q_count)
        '''
        circuit = cirq.Circuit()
        circuit += step1
        circuit += step2
        circuit += step3
        circuit += step4
        circuit += step5
        circuit += step6
        circuit += step7
        result = []

        for i in range(0, n, 1):
            result.append(cirq.NamedQubit("ring_pl" + str(i)))

        result.append(cirq.NamedQubit("ring_Sn"))

        '''
        #Intermediate measurement for testing
        circuit2 = cirq.Circuit()
        a= random.randint(0, 2**n - 1)
        b= random.randint(0, 2**n - 1)
        c= a+b
        bin_str = format(a, 'b')[::-1]  # Get the binary representation and reverse it for easy indexing
        for i, bit in enumerate(bin_str):
            if bit == '1':
                circuit2.append(cirq.X(self.A[i]))
        bin_str = format(b, 'b')[::-1]  # Get the binary representation and reverse it for easy indexing
        for i, bit in enumerate(bin_str):
            if bit == '1':
                circuit2.append(cirq.X(self.B[i]))


        circuit2 += step1
        used_qubits = circuit2.all_qubits()

        for q in used_qubits:
            circuit2.append(cirq.measure(q, key=f'{q}'))

        simul = cirq.Simulator()
        results = simul.simulate(circuit2)

        #print("\nstep2")
        #print("\nstep3")
        ###########################
        def divide(lst, n):
            """Divide the list into n equal parts."""
            k, m = divmod(len(lst), n)
            return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

        def apply_circuit(results, sub_list, qubits):
            circuit2 = cirq.Circuit()
            for q in qubits:
                if results.measurements[str(q)][0] == 1:
                    circuit2.append(cirq.X(q))
            circuit2 += sub_list
            used_qubits = circuit2.all_qubits()
            for q in used_qubits:
                circuit2.append(cirq.measure(q, key=f'{q}'))
            return circuit2, used_qubits
        step = []
        step += step2
        step += step3
        split_lists = divide(step, 64)
        simul = cirq.Simulator()

        for sublist in split_lists:
            circuit2, used_qubits = apply_circuit(results, sublist, used_qubits)
            results = simul.simulate(circuit2)



        #for key, value in results.measurements.items():
        #    print(key, ":", value)

        ######################
        circuit2 = cirq.Circuit()
        for q in used_qubits:
            if results.measurements[str(q)][0] == 1:
                circuit2.append(cirq.X(q))


        circuit2 += step4
        used_qubits = circuit2.all_qubits()
        for q in used_qubits:
            circuit2.append(cirq.measure(q, key=f'{q}'))
        r = []
        for i in range(n):
            r.append(B[i])

        r += [cirq.NamedQubit("ring_Sn")]
        circuit2.append(cirq.measure(r, key="result"))
        simul = cirq.Simulator()
        results = simul.simulate(circuit2)
        for key, value in results.measurements.items():
            #print(key, ":", value)
            if(key =='result'):
                r = int( ''.join(map(str, reversed(value))), 2)

        print("a:",a,"b:",b,"a+b:",a+b,"result:",r)
        if c==r :
            print("good")
        '''
        '''
        print("\nstep5")
        #############################
        circuit2 = cirq.Circuit()
        for q in used_qubits:
            if results.measurements[str(q)][0] == 1:
                circuit2.append(cirq.X(q))

        circuit2 += step5

        print(circuit2)

        used_qubits = circuit2.all_qubits()
        for q in used_qubits:
            circuit2.append(cirq.measure(q, key=f'{q}'))

        simul = cirq.Simulator()
        results = simul.simulate(circuit2)
        for key, value in results.measurements.items():
            print(key, ":", value)

        print("\nstep6")
        #############################
        circuit2 = cirq.Circuit()
        for q in used_qubits:
            if results.measurements[str(q)][0] == 1:
                circuit2.append(cirq.X(q))


        circuit2 += step6
        used_qubits = circuit2.all_qubits()
        for q in used_qubits:
            circuit2.append(cirq.measure(q, key=f'{q}'))

        simul = cirq.Simulator()
        results = simul.simulate(circuit2)
        for key, value in results.measurements.items():
            print(key, ":", value)
        print()
        #############################
        circuit2 = cirq.Circuit()
        for q in used_qubits:
            if results.measurements[str(q)][0] == 1:
                circuit2.append(cirq.X(q))

        circuit2 += step7

        used_qubits = circuit2.all_qubits()
        for q in used_qubits:
            circuit2.append(cirq.measure(q, key=f'{q}'))

        r = []
        for i in range(n):
            r.append(cirq.NamedQubit("ring_pl" + str(i)))

        r += [cirq.NamedQubit("ring_Sn")]
        circuit2.append(cirq.measure(r, key="result"))

        simul = cirq.Simulator()
        results = simul.simulate(circuit2)
        for key, value in results.measurements.items():
            print(key, ":", value)
        '''
        return circuit, result


if __name__ == '__main__':

    n = 16

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
    c, r = adder.create(A, B)
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
    ''''''
    '''
    circuit.append(cirq.measure(r, key="result"))

    simul = cirq.Simulator()
    results = simul.simulate(circuit)
    for key, value in results.measurements.items():
        print(key, ":", value)
    print(results.measurements)
    '''







