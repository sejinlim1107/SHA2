import cirq
import cirqOnqiskit
import wallace
import inDraper

if __name__ == '__main__':
    n = 4
    while n < 1024:
        n *= 2

        A = [cirq.NamedQubit("IN0_" + str(i)) for i in range(n)]
        B = [cirq.NamedQubit("IN1_" + str(i)) for i in range(n)]
        C = [cirq.NamedQubit("IN2_" + str(i)) for i in range(n)]
        D = [cirq.NamedQubit("IN3_" + str(i)) for i in range(n)]
        E = [cirq.NamedQubit("IN4_" + str(i)) for i in range(n)]
        F = [cirq.NamedQubit("IN5_" + str(i)) for i in range(n)]
        G = [cirq.NamedQubit("IN6_" + str(i)) for i in range(n)]
        H = [cirq.NamedQubit("IN7_" + str(i)) for i in range(n)]
        I = [cirq.NamedQubit("IN8_" + str(i)) for i in range(n)]

        inputs = [A, B, C, D, E, F, G, H, I]

        circuit = cirq.Circuit()

        is_metric_mode = True

        #adder, toffoli_type = takahashi.InplaceAdder(True,'Toffoli'), 'Toffoli'
        adder, toffoli_type = inDraper.InplaceAdder(True, 'Toffoli'), 'Toffoli'
        #adder, toffoli_type = outDraper.OutplaceAdder(True, 'Toffoli'), 'Toffoli'
        #adder, toffoli_type = ring.OutplaceAdder(True, 'Toffoli'), 'Toffoli'

        #adder, toffoli_type = gidney.InplaceAdder(is_metric_mode=True), 'ZERO_ANCILLA_TDEPTH_3'
        #adder, toffoli_type = inDraper_logicalAND.InplaceAdder(is_metric_mode=True), 'ZERO_ANCILLA_TDEPTH_3'
        #adder, toffoli_type = outDraper_logicalAND.InplaceAdder(is_metric_mode=True), 'ZERO_ANCILLA_TDEPTH_3'


        #adder, toffoli_type = takahashi.InplaceAdder(True, 'ZERO_ANCILLA_TDEPTH_3'), 'logicalAND'
        #adder, toffoli_type = inDraper.InplaceAdder(True,'ZERO_ANCILLA_TDEPTH_3'), 'logicalAND'
        #adder, toffoli_type = outDraper.OutplaceAdder(True,'ZERO_ANCILLA_TDEPTH_3'), 'logicalAND'

        #adder, toffoli_type = gidney.InplaceAdder(is_metric_mode=True), 'logicalAND'
        #adder, toffoli_type = inDraper_logicalAND.InplaceAdder(is_metric_mode=True), 'logicalAND'
        #adder, toffoli_type = outDraper_logicalAND.OutplaceAdder(is_metric_mode=True), 'logicalAND'
        #adder, toffoli_type = ring.OutplaceAdder(True, 'ZERO_ANCILLA_TDEPTH_3'), 'ZERO_ANCILLA_TDEPTH_3'

        #k = dadda.DaddaTreeAdder(n, inputs, adder, is_metric_mode, toffoli_type)
        k = wallace.WallaceTreeAdder(n, inputs, adder, is_metric_mode, toffoli_type)

        circuit.append(k.circuit.all_operations())

        qasm_circuit = cirqOnqiskit.run_cirq_circuit_on_qiskit(circuit, circuit.all_qubits(), 'qasm_simulator')

        ## t-gate

        t_depth = qasm_circuit.depth(lambda gate: gate[0].name in ['t', 'tdg'])
        op_count = qasm_circuit.count_ops()
        t_count = op_count.get('tdg', 0) + op_count.get('t', 0)

        q_count = qasm_circuit.width()
        print(t_depth, t_count, q_count)


        ## toffoli

        #toffoli_depth = qasm_circuit.depth(lambda gate: gate[0].name in ['ccx'])
        #op_count = qasm_circuit.count_ops()
        #toffoli_count =op_count.get('ccx', 0)
        #q_count = qasm_circuit.width()
        #print(toffoli_depth, toffoli_count, q_count)

