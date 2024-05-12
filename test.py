import copy 


original_list = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

copied_list = copy.deepcopy(original_list)
copied_list[0][0] = 100

print("copied_list: ", copied_list)
print("original_list: ", original_list)