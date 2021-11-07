import random
heads_in_a_row_needed = 10
heads_in_a_row = 0
total_tries = 0
while heads_in_a_row_needed != heads_in_a_row:
    toss = random.randint(0,1)
    if toss == 1:
        heads_in_a_row +=1
    else:
        heads_in_a_row = 0
    total_tries +=1
print("It took %s tries to get %s heads in a row" % (total_tries, heads_in_a_row))
