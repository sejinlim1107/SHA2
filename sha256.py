from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, Swap, Z, T, Tdag, S, Tdagger, Sdag
from projectq.backends import CircuitDrawer, ResourceCounter, CommandPrinter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control, Dagger
from takahashi import *
#from modDraper import *

def make_list(num,length): # 상수 배열 생성

    arr1 = list(format(num, 'b'))
    if length > len(arr1):
        arr2 = ['0' for i in range(length-len(arr1))]
        arr2.extend(arr1)
        arr1 = arr2
    return arr1

def SHA256_init_H(H):

    H0_num = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]

    for i in range(8):
        for j in range(32):
            chain = make_list(H0_num[i],32)
            if chain[j] == 1:
                X | H[i][j]
                # X | H[i][31-j]

def SHA256_init_K(K): # K는 32개의 큐비트 배열 64개가 포함된 리스트 (32바이트씩 64개)

    K_hex = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
             0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
             0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
             0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
             0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
             0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
             0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
             0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
             0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
             0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
             0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

    for i in range(64):
        chain = make_list(K_hex[i], 32)
        for j in range(32):
            if chain[i] == 1:
                X | K[i][j]
                #X | K[i][31-j]

# msg가 512비트보다 적게 들어온다고 가정
def SHA256_preprocessing(msg, q_msg): # q_msg는 W의 0~15가 돼야함
    # Padding + Parsing
    length = len(msg)
    msg_bin = []
    for i in range(length):
        msg_bin += make_list(ord(msg[i]), 8) # ord는 문자의 아스키코드를 반환해줌

    length = len(msg_bin)

    if resource_check != 1:
        for i in range(length):
            if msg_bin[i] == 1:
                X | q_msg[i]

    X | q_msg[length] # 메시지 바로 뒤에 1을 써줘야함

    # for i in range(length+1, 448): # 여기는 다 0

    len_bin = make_list(length, 64) # 맨 뒤 64비트는 메시지의 길이를 넣어야함
    for i in range(448, 512):
        if len_bin[i] == 1:
            X | q_msg[i]

def w_sigma(rr0, rr1, ss, input, output):

    rr0 = 32-rr0
    rr1 = 32-rr1

    for i in range(32):
        CNOT | (input[(rr0+i)%32], output[i])
        CNOT | (input[(rr1+i)%32], output[i])
        if i >= ss: # ss ~ 31
            CNOT | (input[i-ss], output[i])

def SHA256_mexp(eng, W, ancilla): # W는 32개의 큐비트 배열 64개가 포함된 리스트 (32바이트씩 64개)

    for i in range(16, 64):
        # carry save adder 쓰면 좋겠다
        # draper 안실라도 재활용!
        # outDraper(eng, W[i-2], W[i-7], W[i], 32) # W[i]에 덧셈 결과 저장
        w_sigma(17, 19, 10, W[i-2], W[i]) # sigma1
        takahashi(W[i-7],W[i],32)
        with Compute(eng):
            w_sigma(7, 18, 3, W[i-15], ancilla)  # sigma0
        takahashi(ancilla, W[i-16], 32)
        Uncompute(eng) # 이거 잘 동작하려나?
        takahashi(W[i-16], W[i], 32)

def r_sigma(rr0, rr1, rr2, input, output):

    rr0 = 32-rr0
    rr1 = 32-rr1
    rr2 = 32-rr2

    for i in range(32):
        CNOT | (input[(rr0+i)%32], output[i])
        CNOT | (input[(rr1+i)%32], output[i])
        CNOT | (input[(rr2+i)%32], output[i])

def maj(x, y, z, output):

    for i in range(32):
        toffoli_gate(x[i],y[i],output[i])
        toffoli_gate(x[i],z[i],output[i])
        toffoli_gate(y[i],z[i],output[i])

def ch(x, y, z, output):

    for i in range(32):
        toffoli_gate(x[i], y[i], output[i])
        X | x[i]
        toffoli_gate(x[i], z[i], output[i])

def SHA256_round(eng, K, W, H, ancilla):

    r_sigma(2, 13, 22, H[0], ancilla[0])
    with Compute(eng):
        maj(H[0],H[1],H[2])
    takahashi(H[2],ancilla[0],32)
    Uncompute(eng) # maj dagger

    r_sigma(6,11,25,H[4],ancilla[1])
    takahashi(ancilla)






def main(eng):

    H = [], K = [], W = []

    for i in range(8):
        H.append(eng.allocate_qureg(32))

    for i in range(64):
        K.append(eng.allocate_qureg(32))
        W.append(eng.allocate_qureg(32))
    ancilla = []
    for i in range(2):
        ancilla.append(eng.allocate_qureg(32)) # for MXF and round

    msg = "abc"

    SHA256_init_H(H)
    SHA256_init_K(K)
    SHA256_preprocessing(msg, W[:16])
    # mexp를 round 16번째일 때 하는건?
    # SHA256_mexp(eng, W, ancilla)



TD = 0
resource_check = 0

Resource = ClassicalSimulator()
#Resource = ResourceCounter()
eng = MainEngine(Resource)
main(eng)
#print(Resource)
eng.flush()








