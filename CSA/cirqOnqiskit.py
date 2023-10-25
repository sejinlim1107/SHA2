import cirq
from qiskit import QuantumCircuit
def run_cirq_circuit_on_qiskit(circuit: 'cirq.Circuit', qubits, backend: str):
    qasm_output = cirq.QasmOutput((circuit.all_operations()), qubits)

    qasm_circuit = QuantumCircuit().from_qasm_str(str(qasm_output))
    return qasm_circuit
