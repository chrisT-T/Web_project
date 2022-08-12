# from test_script import echo

def testFunc():
    res = 0
    a = [1,2]
    b = { 'a' :2}
    c = [b,a]
    d = 'fk'
    for i in range(100):
        res += i
    x = 1
    print(res)

    print(res ** 2)

testFunc()