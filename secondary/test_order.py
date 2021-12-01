all_id = [1,2,3,5,7]
all_msg = ['1','2','3','5','7']

# all_id = [1, 5]
# all_msg = ['1', '5']
#
# all_id = [5]
# all_msg = ['5']
#
# all_id = [2, 5]
# all_msg = ['2','5']
#
# all_id = [1]
# all_msg = ['1']

last_ordered_msg = 0

if len(all_id) == 1 and all_id[0] == 1:
   print(all_msg)

elif len(all_id) >= 2:
    for x in all_id:
        if x == all_id[-1] and x - all_id[all_id.index(x) - 1] == 1:
            last_ordered_msg = x + 1
        elif x - all_id[all_id.index(x) + 1] == -1:
            last_ordered_msg = x + 1
        else:
            if x == 1 and x - all_id[all_id.index(x) + 1] != -1:
                last_ordered_msg = 1
                break
            else:
                break
    print(all_msg[:last_ordered_msg])
else:
    print([])