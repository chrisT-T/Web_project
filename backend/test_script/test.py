from test_script import echo

def testFunc():
    res = 0
    for i in range(100):
        res += i

    print(res)

    print(res ** 2)

testFunc()