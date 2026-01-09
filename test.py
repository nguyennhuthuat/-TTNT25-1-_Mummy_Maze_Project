a = {
    "cc": [1,2,3]
}
print(a)
def cal(a):
    a["cc"].append(4)
    print(a)
    b = a["cc"]
    b.append(5)
    print(a)

cal(a)
print(a)