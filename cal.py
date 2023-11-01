import cirq
import math as mt

def w(n):
    return n - sum(int(mt.floor(n / (mt.pow(2, i)))) for i in range(1, int(mt.log2(n)) + 1))

def l(n, t):
    return int(mt.floor(n / (mt.pow(2, t))))

n = 32


print((n-1)-w(n-1))
cnt = 0

for t in range(1, int(mt.log2(n - 1))):
    for m in range(1, l(n - 1, t)):
        if t != 1:
            cnt+=1


print(cnt)
print
print(n-1-w(n-1)-mt.floor(mt.log2(n-1)))
#print(4*n)


print(int(mt.log2(n))+int(mt.log2(n-1))+int(mt.log2(n/3))+int(mt.log2((n-1)/3))+8)
#print(int(mt.log2(n))+int(mt.log2((n-1)/3))+5)



print(int(mt.log2(n))+int(mt.log2(n/3))+3)


print(int(mt.log2(n))+int(mt.log2(n-1))+int(mt.log2(n/3))+int(mt.log2((n-1)/3))+1)

print(4*n-w(n)-int(mt.log2(n)))
print(77*n-21*w(n)-21*w(n-1)-21*int(mt.log2(n))-21*int(mt.log2(n-1))-49)
print(4*n+1)

print(11*n-3*w(n)-3*w(n-1)-3*int(mt.log2(n))-3*int(mt.log2(n-1))-7)

print(int(mt.log2(n))+int(mt.log2(n/3))+3)

print(int(mt.log2(n))+int(mt.log2(n/3))+4)



print(9*n-2*w(n)-2*w(n-1)-2*int(mt.log2(n))-2*int(mt.log2(n-1))-5)

print(n -w(n) -mt.floor(mt.log2(n)))
print(6*n-2*w(n)-2*int(mt.log2(n))-1)
print(32*n-8*w(n)-8*w(n-1)-8*int(mt.log2(n))-8*int(mt.log2(n-1))-24)
print(int(mt.log2(n))+int(mt.log2(n/3))+int(mt.log2(n-1))+int(mt.log2((n-1)/3))+4)


# print(6*n-2*w(n)-2*int(mt.log2(n)))
# print(16*n-8*w(n)-8*int(mt.log2(n))-4)
# print(int(mt.log2(n))+int(mt.log2(n/3))+4)


print()

print(int(mt.log2(n))+int(mt.log2(n-1))+int(mt.log2(n/3))+int(mt.log2((n-1)/3))+5)


print(9*n-2*int(mt.log2(n))-2*int(mt.log2(n-1))-2*w(n)-2*w(n-1))

print(6*n-2*w(n)-2*int(mt.log2(n)))
print(16*n-8*w(n)-8*int(mt.log2(n))-4)

#print(3*n+3*int(mt.log2(n))+3*int(mt.log2(n/3))+12)

print(2*n-1)
print(int(mt.log2(n))+int(mt.log2(n-1))+int(mt.log2(n/3))+int(mt.log2((n-1)/3))+8)


'''
print(10*n-3*w(n)-3*w(n-1)-3*int(mt.log2(n))-3*int(mt.log2(n-1))-7)
print(4*n-w(n)-int(mt.log2(n)))

for i in range(2,11):
    n = i
    print(10*n-3*w(n)-3*w(n-1)-3*int(mt.log2(n))-3*int(mt.log2(n-1))-7)

print("끝")

n = 8

print(5*n -w(n) -mt.floor(mt.log2(n)) -2*w(n-1) -2*mt.floor(mt.log2(n-1)) -5)
#print(n-1 - w(n-1) - mt.floor(mt.log2(n-1)))
print(2*n -w(n) -mt.floor(mt.log2(n)) -1)

n = 16
print(mt.floor(mt.log2((2*(n-1))/3)))
print(l((n-1)-pow(2,0),1))
#print(l(n-1,2))

for i in range(2,11):
    n = i
    print(10*n-3*w(n)-3*w(n-1)-3*int(mt.log2(n))-3*int(mt.log2(n-1))-7)

print("끝")

n = 10

print(int(mt.log2(n))+int(mt.log2(n-1))+int(mt.log2(n/3))+int(mt.log2((n-1)/3))+14)
print(2*n-w(n)-int(mt.log2(n))-1)
print(int(mt.log2(n))+int(mt.log2(n/3))+7)
print(5*n-3*w(n)-3*mt.floor(mt.log2(n))-1)

print(70*n-21*w(n)-21*w(n-1)-21*int(mt.log2(n))-21*int(mt.log2(n-1))-49)
print(10*n-6*int(mt.log2(n))-13)

print(n-w(n))
print(77*n-21*w(n)-12*int(mt.log2(n))-4)
print(44*n-12*w(n)-12*w(n-1)-12*int(mt.log2(n))-12*int(mt.log2(n-1))-28)

print(24*n-12*w(n)-12*int(mt.log2(n))-4)




n = 16
print('ancilla')
ancilla = n - w(n) - mt.floor(mt.log2(n))
print(ancilla)
print(int(mt.log2(2*n/3)))

print(n-w(n)-int(mt.log2(n)))
print(n-w(n))

print(int(mt.log2(n)))

for i in range(1,5):
    print(l(n, i))
for t in range(3,0,-1):
    print('이걸 봐',ancilla-1-(l((n - pow(2, t - 1)), t)+l((n - pow(2, t - 2)), t-1)))


for t in range(int(mt.log2(2 * n / 3)), 0, -1):
    print('t = ', t)

'''