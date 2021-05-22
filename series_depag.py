s = 'ABCDEFGH'
while s:
    # x, s = s[0], list(s[1:])
    x, *s = s
    print(x, s)