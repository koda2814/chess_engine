import numpy as np

np_list = np.array([1, 2, 3, 4, 5])
# np_list[1] = 50

np_list = np.append(np_list, [228])
print(np_list[5])
print(len(np_list))

for x in np_list:
    print(x)