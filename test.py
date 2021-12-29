N, K = list(map(int, input().split()))
A = list(map(int, input().split()))

S = sum(A)
avg = S // N
if avg <= K:
    print(0)
else:
    ans = (S // (K + 1)) - N + 1
    print(ans)
