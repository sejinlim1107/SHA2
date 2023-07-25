from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, Swap, Z, T, Tdag, S, Tdagger, Sdag
from projectq.backends import CircuitDrawer, ResourceCounter, CommandPrinter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control, Dagger

def toffoli_gate(a, b, c):
    if(TD == 1): # 분해 버전 (일반 시뮬레이터 사용 시 / ResourceCounter 사용 시)
        Tdag | a
        Tdag | b
        H | c
        CNOT | (c, a)
        T | a
        CNOT | (b, c)
        CNOT | (b, a)
        T | c
        Tdag | a
        CNOT | (b, c)
        CNOT | (c, a)
        T | a
        Tdag | c
        CNOT | (b, a)
        H | c
    else: # TD == 0, 분해 안된 버전 사용 (클래식 시뮬레이터 사용 시)
        Toffoli | (a, b, c)

def takahashi(a,b,n): # modular adder

    for i in range(1,n):
        CNOT | (a[i], b[i])

    for i in range(n-2,0,-1):
        CNOT | (a[i], a[i+1])

    for i in range(n-1):
        toffoli_gate(a[i], b[i], a[i+1])

    for i in range(n-1,0,-1):
        CNOT | (a[i], b[i])
        toffoli_gate(b[i-1], a[i-1], a[i])

    for i in range(1,n-1):
        CNOT | (a[i], a[i+1])

    for i in range(n):
        CNOT | (a[i], b[i])

    result = []
    for i in b:
        result.append(i)

    return result

def adder_test(eng, A, B, n):
    a = eng.allocate_qureg(n)
    b = eng.allocate_qureg(n)
    if (resource_check == 0):
        round_constant_XOR(A, a, n)
        round_constant_XOR(B, b, n)

    if (resource_check == 0):
        print('a: ', end='')
        print_vector(a, n)
        print('b: ', end='')
        print_vector(b, n)

    sum = takahashi(a,b,n)

    if (resource_check == 0):
        print('Add result : ', end='')
        print_vector(sum, n)

def round_constant_XOR(rc, qubits, n):
    for i in range(n):
        if ((rc >> i) & 1):
            X | qubits[i]

def print_vector(element, length):
    All(Measure) | element
    for k in range(length):
        print(int(element[length-1-k]), end='')
    print()

if __name__ == "__main__":
    n = 10
    a = 0b1111111111
    b = 0b1111111111

    TD = 0
    resource_check = 0

    Resource = ClassicalSimulator()
    #Resource = ResourceCounter()
    eng = MainEngine(Resource)
    #eng = MainEngine()
    adder_test(eng,a,b,n)
    #print(Resource)
    eng.flush()
