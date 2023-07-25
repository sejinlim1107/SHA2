from math import floor, ceil, log10, log2

def w(n):
    return n - sum(int(floor(n / (pow(2, i)))) for i in range(1, int(log2(n)) + 1))

def l(n, t):
    return int(floor(n / (pow(2, t))))

n = 10

print(n-w(n)-floor(log2(n)))

out_cnt = floor(log2(n))+floor(log2(n/3))+7
print(out_cnt)

in_cnt = floor(log2(n))+floor(log2(n-1))+floor(log2(n/3))+floor(log2((n-1)/3))+14
print(in_cnt)