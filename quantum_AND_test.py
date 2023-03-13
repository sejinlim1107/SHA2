# 얘만 테스트하고 싶으면 Dagger문 안쓴거로 해야됨!
# # AND gate Test
# eng = MainEngine()
# n = 1 # bit length
#
# a = eng.allocate_qubit()
# b = eng.allocate_qubit()
# c = eng.allocate_qubit()
#
# round_constant_XOR(1, a, n)
# round_constant_XOR(1, b, n)
# round_constant_XOR(0, c, n)
#
# print_vector(eng,a,n)
# print_vector(eng,b,n)
# print_vector(eng,c,n)
#
# quantum_and(eng,a,b,c)
#
# print_vector(eng,a,n)
# print_vector(eng,b,n)
# print_vector(eng,c,n)
#
# quantum_and_dag(eng,a,b,c)
#
# print_vector(eng,a,n)
# print_vector(eng,b,n)
# print_vector(eng,c,n)
#
# eng.flush()