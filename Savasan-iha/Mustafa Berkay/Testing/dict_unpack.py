
def return_test():
    
    dict3 = {
            "dict3_a": 31,
            "dict3_b": 31
            }


    dict2 = {
            "dict2_a": dict3,
            "dict2_b": 5743
            }

    dict1 = {
            "dict1_a": dict3,
            "dict1_b": 8234
            }
    return dict1,dict2

a , b = return_test()

print(a)
print(b)