import numpy as np
from itertools import combinations
from itertools import product
from itertools import combinations_with_replacement as cwr
import math
import matplotlib.pyplot as plt
import random

"""
IPO Algorithm
This is an implementation of the IPOG algorithm as introduced in IPOG: A General Strategy for T-Way Software Testing (Lei1 et al).

The basic idea of the IPOG algorithm is to use a covering array of size of k-1 parameters to build an array of k parameters.
This growth is achieved in two steps, horizontal growth followed by vertical growth. The horizontal growth adds a new column to the covering array and chooses the value in each row of this new column strategically, maximizing uncovered interactions. If there are interactions that remain uncovered by horizontal growth, we must add new rows to the covering array. Vertical
growth adds these uncovered interactions in the form of new rows.

The function IPO takes three parameters: t, k, and v and returns a covering array

t = the strength of the covering array

k = the number of columns/parameters in the covering array

v = the range of values a parameter can have

In IPOG, we begin by initializing a t-way covering array with t parameters and v values. This is the initial covering array that we will augment.

Next, we loop through the parameters t+1 to k, since we already have a CA that includes parameters 1 to t.

We then create the set of t-way combinations of values involving parameter Pi and the previous i – 1 parameters, called t_comb.
horizontal_growth
We implement horizontal growth using a greedy method that chooses the value of the new parameter such that the chosen value maximizes the number of uncovered interactions.

Horizontal growth begins by iterating through each row in order. v candidate rows are created. These rows are then tested to see which one covers the most uncovered interactions in t_comb. After the best candidate row is chosen, we remove the interactions it covers from t_comb, and augment the existing row in the covering array.

Vertical Growth

If there are any uncovered interactions left in t_comb, vertical growth is required. Vertical growth is accomplished by considering each uncovered interaction in t_comb. If there is no row that covers this interaction nor has a '-' in each place, a new row is created with the parameters having their respective values and '-' or don't cares in all other positions. If there is a row that has a '-' or the respective value for each parameter, modify this row such that each parameter has it's respective value as specified in t_comb.

After Vertical Growth, there may be '-' positions that have not been filled. The '-' are filled randomly.

The algorithm continues untill it creates a new column and however many rows for each parameter k.
"""

"""
Converts a tuple to a list
"""
def tup_to_list(comb):
    new_comb = []
    for item in comb:
        l = []
        for val in item:
            l.append(val)
        new_comb.append(l)
    return new_comb

"""
Determines which candidate row covers the most uncovered interactions and returns that row
"""
def test_candidates(t,candidates,t_comb):
    max_cover = 0
    best_candidate = ""
    for c in candidates:
        num_cover = 0
        for key in t_comb:
            row_vals = []
            for i in range(t):
                pos = key[i]
                row_vals.append(c[pos])
            if row_vals in t_comb[key]:
                num_cover +=1
        if num_cover >= max_cover:
            max_cover = num_cover
            best_candidate = c

    return best_candidate


"""
Removes the interactions from the t_comb that are covered by the new row
"""
def remove_interact(t,new_row,t_comb):
    for key in t_comb:
        row_vals = []
        for i in range(t):
            pos = key[i]
            row_vals.append(new_row[pos])
        if row_vals in t_comb[key]:
            t_comb[key].remove(row_vals)
    return t_comb


"""
Horizontal Growth algorithm
"""
def horizontal_growth(t,v,num_rows,ca,t_comb):
    for r in range(len(ca)):
        #create v candidate rows
        candidates = []
        row = ca[r]
        new_vals = tup_to_list(list(product(range(v),repeat=num_rows)))
        for val in new_vals:
            c = row.copy()
            c.extend(val)
            candidates.append(c)

        #test which candidate row covers the most amount of interactions
        new_row = test_candidates(t,candidates,t_comb)

        #remove from t_comb the combinations of values covered by r'
        t_comb = remove_interact(t,new_row,t_comb)

        #add augmented row to covering array
        ca[r] = new_row


"""
Generate a new row such that each p in parameters has value v, rest have '-'
"""
def generate_row(params,vals,row_len):
    row = []
    for p in range(row_len):
        if p in params:
            i = params.index(p)
            row.append(vals[i])
        else:
            row.append('-')
    return row


"""
Modify the existing row such that each p in parameters has value v in the row
"""
def modify_row(params,vals,row):
    for i in range(len(row)):
        if i in params:
            p = params.index(i)
            row[i] = vals[p]
    return row



"""
Vertical Growth Algorithm
Takes the uncovered interactions as input and adds new rows if necessary to the CA
"""
def vertical_growth(t_comb, ca):
    v_rows = []
    row_len = len(ca[0])
    #print(ca)
    #print(t_comb)
    #for every uncovered interaction in t_comb
    #for each pair (pk*w, pi*u) in t_comb, pk is the col position and w is the value
    for key in t_comb:
        for val in t_comb[key]:
            #if v_rows contains a row that has a '-' as the value of pk and u as the value of pi
            is_modified = False
            for vrow in v_rows:
                #print(vrow)
                is_covered = True
                for k in range(len(key)):
                    v = val[k]
                    pos = key[k]
                    #If this vrow does not have a '-' or the value v in this position, break and try the next vrow
                    if vrow[pos] != '-' and vrow[pos] != v:
                        is_covered = False
                        break
                #this row is good
                if is_covered:
                    #modify this row
                    vrow = modify_row(key,val,vrow)
                    is_modified = True
                    #dont need to consider other rows
                    break
            #else add a new row to v_rows that has w as value for pk, u as value for pi, and '-' for all other parameters
            if not is_modified:
                new_row = generate_row(key,val,row_len)
                v_rows.append(new_row)

    #add new rows to covering array
    for row in v_rows:
        ca.append(row)
   # print(ca)


"""
Function that fills don't care values after vertical growth
Takes the covering array and values v as input and randomly assigns the don't care position a value
"""
def fill_dc(v,ca):
    for row in ca:
        for i in range(len(row)):
            if row[i] == '-':
                row[i] = random.randint(0,v-1)

"""
IPO Baseline
Input strength of covering array t, number of parameters k, and number of values v
IPO function implements the IPOG algorithm, and returns a covering array of size N
"""
def IPO(t,k,v):

    #initial CA, add a row for each combination of values of the first t parameters ie. exhaustive search method
    ca = tup_to_list(list(product(range(v),repeat=t)))
    random.shuffle(ca)

    #loop through parameters t+1 to k
    for i in range(t,k):

        #let t_comb be the set of t-way combinations of values involving parameter Pi and t -1 parameters
        #among the first i – 1 parameters
        comb = (list(combinations(list(np.arange(0,i+1,1)), t)))
        t_comb = {}
        for c in comb:
            if c not in t_comb:
                t_comb[c] = tup_to_list(list(product(range(v),repeat=t)))

        #print(ca)
        #print(len(t_comb))
        #horizontal growth
        horizontal_growth(t,v,1,ca,t_comb)

        keys = []
        for key, val in t_comb.items():
            if len(val) == 0:
                keys.append(key)

        for key in keys:
            del t_comb[key]

        if len(t_comb) > 0:
            #vertical growth
            vertical_growth(t_comb, ca)
            #fill '-' values
            fill_dc(v, ca)

    return ca

"""
IPO 2
"""
def IPO_2(t,k,v):

    #initial CA, add a row for each combination of values of the first t parameters ie. exhaustive search method
    ca = tup_to_list(list(product(range(v),repeat=t)))
    random.shuffle(ca)

    #loop through parameters t+1 to k
    for i in range(t,k,2):

        if i == k-1:
            num_rows = 1

        else:
            num_rows = 2

        #let t_comb be the set of t-way combinations of values involving parameter Pi, Pi+1 and i-1 previous parameters
        comb = (list(combinations(list(np.arange(0,i+num_rows,1)), t)))
        t_comb = {}
        for c in comb:
            if c not in t_comb:
                t_comb[c] = tup_to_list(list(product(range(v),repeat=t)))

        #horizontal growth
        horizontal_growth(t,v,num_rows,ca,t_comb)

        keys = []
        for key, val in t_comb.items():
            if len(val) == 0:
                keys.append(key)

        for key in keys:
            del t_comb[key]

        if len(t_comb) > 0:
            #vertical growth
            vertical_growth(t_comb, ca)
            #fill '-' values
            fill_dc(v, ca)

    return ca


"""
IPO 3
"""
def IPO_3(t,k,v):

    #initial CA, add a row for each combination of values of the first t parameters ie. exhaustive search method
    ca = tup_to_list(list(product(range(v),repeat=t)))
    random.shuffle(ca)

    #loop through parameters t+1 to k
    for i in range(t,k,3):

        if i == k-1:
            num_rows = 1

        elif i == k-2:
            num_rows = 2

        else:
            num_rows = 3

        #let t_comb be the set of t-way combinations of values involving parameter Pi, Pi+1 and i-1 previous parameters
        comb = (list(combinations(list(np.arange(0,i+num_rows,1)), t)))
        t_comb = {}
        for c in comb:
            if c not in t_comb:
                t_comb[c] = tup_to_list(list(product(range(v),repeat=t)))

        #horizontal growth
        horizontal_growth(t,v,num_rows,ca,t_comb)

        keys = []
        for key, val in t_comb.items():
            if len(val) == 0:
                keys.append(key)

        for key in keys:
            del t_comb[key]

        if len(t_comb) > 0:
            #vertical growth
            vertical_growth(t_comb, ca)
            #fill '-' values
            fill_dc(v, ca)
    return ca

"""
IPO 4
"""
def IPO_4(t,k,v):

    #initial CA, add a row for each combination of values of the first t parameters ie. exhaustive search method
    ca = tup_to_list(list(product(range(v),repeat=t)))
    random.shuffle(ca)

    #loop through parameters t+1 to k
    for i in range(t,k,4):

        if i == k-1:
            num_rows = 1

        elif i == k-2:
            num_rows = 2

        elif i == k-3:
            num_rows = 3

        else:
            num_rows = 4

        #let t_comb be the set of t-way combinations of values involving parameter Pi, Pi+1 and i-1 previous parameters
        comb = (list(combinations(list(np.arange(0,i+num_rows,1)), t)))
        t_comb = {}
        for c in comb:
            if c not in t_comb:
                t_comb[c] = tup_to_list(list(product(range(v),repeat=t)))

        #horizontal growth
        horizontal_growth(t,v,num_rows,ca,t_comb)

        keys = []
        for key, val in t_comb.items():
            if len(val) == 0:
                keys.append(key)

        for key in keys:
            del t_comb[key]

        if len(t_comb) > 0:
            #vertical growth
            vertical_growth(t_comb, ca)
            #fill '-' values
            fill_dc(v, ca)

    return ca

"""
IPO 5
"""
def IPO_5(t,k,v):

    #initial CA, add a row for each combination of values of the first t parameters ie. exhaustive search method
    ca = tup_to_list(list(product(range(v),repeat=t)))
    random.shuffle(ca)

    #loop through parameters t+1 to k
    for i in range(t,k,5):

        if i == k-1:
            num_rows = 1

        elif i == k-2:
            num_rows = 2

        elif i == k-3:
            num_rows = 3

        elif i == k-4:
            num_rows = 4

        else:
            num_rows = 5

        #let t_comb be the set of t-way combinations of values involving parameter Pi, Pi+1 and i-1 previous parameters
        comb = (list(combinations(list(np.arange(0,i+num_rows,1)), t)))
        t_comb = {}
        for c in comb:
            if c not in t_comb:
                t_comb[c] = tup_to_list(list(product(range(v),repeat=t)))

        #horizontal growth
        horizontal_growth(t,v,num_rows,ca,t_comb)

        keys = []
        for key, val in t_comb.items():
            if len(val) == 0:
                keys.append(key)

        for key in keys:
            del t_comb[key]

        if len(t_comb) > 0:
            #vertical growth
            vertical_growth(t_comb, ca)
            #fill '-' values
            fill_dc(v, ca)

    return ca

"""
IPO 6
"""
def IPO_6(t,k,v):

    #initial CA, add a row for each combination of values of the first t parameters ie. exhaustive search method
    ca = tup_to_list(list(product(range(v),repeat=t)))
    random.shuffle(ca)

    #loop through parameters t+1 to k
    for i in range(t,k,6):

        if i == k-1:
            num_rows = 1

        elif i == k-2:
            num_rows = 2

        elif i == k-3:
            num_rows = 3

        elif i == k-4:
            num_rows = 4

        elif i == k-5:
            num_rows = 5

        else:
            num_rows = 6

        #let t_comb be the set of t-way combinations of values involving parameter Pi, Pi+1 and i-1 previous parameters
        comb = (list(combinations(list(np.arange(0,i+num_rows,1)), t)))
        t_comb = {}
        for c in comb:
            if c not in t_comb:
                t_comb[c] = tup_to_list(list(product(range(v),repeat=t)))

        #horizontal growth
        horizontal_growth(t,v,num_rows,ca,t_comb)

        keys = []
        for key, val in t_comb.items():
            if len(val) == 0:
                keys.append(key)

        for key in keys:
            del t_comb[key]

        if len(t_comb) > 0:
            #vertical growth
            vertical_growth(t_comb, ca)
            #fill '-' values
            fill_dc(v, ca)

    return ca


"""
IPO 8
"""
def IPO_8(t,k,v):

    #initial CA, add a row for each combination of values of the first t parameters ie. exhaustive search method
    ca = tup_to_list(list(product(range(v),repeat=t)))
    random.shuffle(ca)

    #loop through parameters t+1 to k
    for i in range(t,k,8):

        if i == k-1:
            num_rows = 1

        elif i == k-2:
            num_rows = 2

        elif i == k-3:
            num_rows = 3

        elif i == k-4:
            num_rows = 4

        elif i == k-5:
            num_rows = 5

        elif i == k-6:
            num_rows = 6

        elif i == k-7:
            num_rows = 7

        else:
            num_rows = 8

        #let t_comb be the set of t-way combinations of values involving parameter Pi, Pi+1 and i-1 previous parameters
        comb = (list(combinations(list(np.arange(0,i+num_rows,1)), t)))
        t_comb = {}
        for c in comb:
            if c not in t_comb:
                t_comb[c] = tup_to_list(list(product(range(v),repeat=t)))

        #horizontal growth
        horizontal_growth(t,v,num_rows,ca,t_comb)

        keys = []
        for key, val in t_comb.items():
            if len(val) == 0:
                keys.append(key)

        for key in keys:
            del t_comb[key]

        if len(t_comb) > 0:
            #vertical growth
            vertical_growth(t_comb, ca)
            #fill '-' values
            fill_dc(v, ca)

    return ca

"""
IPO 12
"""
def IPO_12(t,k,v):

    #initial CA, add a row for each combination of values of the first t parameters ie. exhaustive search method
    ca = tup_to_list(list(product(range(v),repeat=t)))
    random.shuffle(ca)

    #loop through parameters t+1 to k
    for i in range(t,k,12):

        if i == k-1:
            num_rows = 1

        elif i == k-2:
            num_rows = 2

        elif i == k-3:
            num_rows = 3

        elif i == k-4:
            num_rows = 4

        elif i == k-5:
            num_rows = 5

        elif i == k-6:
            num_rows = 6

        elif i == k-7:
            num_rows = 7

        elif i == k-8:
            num_rows = 8

        elif i == k-9:
            num_rows = 9

        elif i == k-10:
            num_rows = 10

        elif i == k-11:
            num_rows = 11

        else:
            num_rows = 12

        #let t_comb be the set of t-way combinations of values involving parameter Pi, Pi+1 and i-1 previous parameters
        comb = (list(combinations(list(np.arange(0,i+num_rows,1)), t)))
        t_comb = {}
        for c in comb:
            if c not in t_comb:
                t_comb[c] = tup_to_list(list(product(range(v),repeat=t)))

        #horizontal growth
        horizontal_growth(t,v,num_rows,ca,t_comb)

        keys = []
        for key, val in t_comb.items():
            if len(val) == 0:
                keys.append(key)

        for key in keys:
            del t_comb[key]

        if len(t_comb) > 0:
            #vertical growth
            vertical_growth(t_comb, ca)
            #fill '-' values
            fill_dc(v, ca)

    return ca

"""
Given a covering array and values of t, k and v, this function returns
a boolean that indicates if the given array is a covering array given the
values of t, k and v.
"""
def is_covering_array(ca,t,k,v):

    #represents the unique t way combinations of column positions
    comb = (list(combinations(list(np.arange(0,k,1)), t)))

    #represents all the possible t way interactions
    interact = {}
    for c in comb:
        if c not in interact:
            interact[c] = tup_to_list(list(product(range(v),repeat=t)))


    #for each t way column interaction
    for item in comb:
        #for each row in the covering array
        for row in ca:
            subset = []
            #for each parameter in t-way interaction
            for param in item:
                subset.append(row[param])
            if subset in interact[item]:
                interact[item].remove(subset)

    for k,v in interact.items():
        if len(v) > 0:
            print("NOT A COVERING ARRAY")
            return

    print("COVERING ARRAY!")
    return

"""
Testing Function
"""
def run_tests_2(num_iter,arrays):
    IPOS = [IPO,IPO_2]
    for arr in arrays:
        t = arr[0]
        k = arr[1]
        v = arr[2]
        num = 1
        for F in IPOS:
            ca_len = []
            for i in range(num_iter):
                ca = F(t,k,v)
                ca_len.append(len(ca))
            print('IPO '+ str(num) +': Min = '+ str(min(ca_len)) + ' Mean = ' + str(np.mean(ca_len)))
            num+=1


def run_tests(num_iter,arrays):
    IPOS = [IPO,IPO_2,IPO_3,IPO_4,IPO_5]
    for arr in arrays:
        t = arr[0]
        k = arr[1]
        v = arr[2]
        num = 1
        for F in IPOS:
            ca_len = []
            for i in range(num_iter):
                ca = F(t,k,v)
                ca_len.append(len(ca))
            print('IPO '+ str(num) +': Min = '+ str(min(ca_len)) + ' Mean = ' + str(np.mean(ca_len)))
            num+=1

def run_tests_factors(num_iter,arrays):
    IPOS = [IPO,IPO_2,IPO_3,IPO_4,IPO_6,IPO_8, IPO_12]
    num = [1,2,3,4,6,8,12]
    for arr in arrays:
        t = arr[0]
        k = arr[1]
        v = arr[2]
        for i in range(len(IPOS)):
            ca_len = []
            for j in range(num_iter):
                ca = IPOS[i](t,k,v)
                ca_len.append(len(ca))
            print('IPO '+ str(num[i]) +': Min = '+ str(min(ca_len)) + ' Mean = ' + str(np.mean(ca_len)))

"""
Figure 1 code

ns =[]
for i in range(10,51,2):
    ns.append([3,i,3])
cas = []
ipo_len =[]
for n in ns:
    l = []
    ca = []
    for i in range(10):
        t = n[0]
        k = n[1]
        v = n[2]
        c = IPO(t,k,v)
        ca.append(c)
        l.append(len(c))

    min_ca = min(l)
    idx = l.index(min_ca)
    cas.append(ca[idx])
    print(str(n) + ' ' + str(min_ca))
    ipo_len.append(min_ca)

ns = []
for i in range(10,51,2):
    ns.append([3,i,3])
cas = []
ipo2_len =[]
for n in ns:
    l = []
    ca = []
    for i in range(10):
        t = n[0]
        k = n[1]
        v = n[2]
        c = IPO_2(t,k,v)
        ca.append(c)
        l.append(len(c))

    min_ca = min(l)
    idx = l.index(min_ca)
    cas.append(ca[idx])
    print(str(n) + ' ' + str(min_ca))
    ipo2_len.append(min_ca)


ys = list(range(10,51,2))
plt.plot(ipo2_len, ys)
plt.plot(ipo_len, ys)
plt.title("IPO 2 vs. IPO for CA(3,k,3)")
plt.xlabel("N")
plt.ylabel("k")
plt.legend(("IPO 2", "IPO"))

ns =[]
for i in range(10,51,2):
    ns.append([2,i,5])
cas = []
ipo_len =[]
for n in ns:
    l = []
    ca = []
    for i in range(10):
        t = n[0]
        k = n[1]
        v = n[2]
        c = IPO(t,k,v)
        ca.append(c)
        l.append(len(c))

    min_ca = min(l)
    idx = l.index(min_ca)
    cas.append(ca[idx])
    print(str(n) + ' ' + str(min_ca))
    ipo_len.append(min_ca)

ns = []
for i in range(10,51,2):
    ns.append([2,i,5])
cas = []
ipo2_len =[]
for n in ns:
    l = []
    ca = []
    for i in range(10):
        t = n[0]
        k = n[1]
        v = n[2]
        c = IPO_2(t,k,v)
        ca.append(c)
        l.append(len(c))

    min_ca = min(l)
    idx = l.index(min_ca)
    cas.append(ca[idx])
    print(str(n) + ' ' + str(min_ca))
    ipo2_len.append(min_ca)


ys = list(range(10,51,2))
plt.plot(ipo2_len, ys)
plt.plot(ipo_len, ys)
plt.title("IPO 2 vs. IPO for CA(2,k,5)")
plt.xlabel("N")
plt.ylabel("k")
plt.legend(("IPO 2", "IPO"))

"""

"""
Figure 2 code

len_ca = {}
for i in range(10,86,1):
    run_tests_2(len_ca,50,[[2,i,2]])

ys = list(range(10,86,1))
for k,v in len_ca.items():
    plt.plot(v, ys)
    plt.title("Average N for CA(2,k,2)")
    plt.xlabel("N")
    plt.ylabel("k")
    plt.legend(("IPO", "IPO 2","IPO 3", "IPO 4","IPO 5"))
"""
def main():
    #Table 1
    run_tests_2(10000,[[2,10,3]])
    run_tests_2(10000,[[3,10,3]])

    #Table 2
    run_tests(10000,[[2,10,2]])
    run_tests(10000,[[2,12,2]])
    run_tests(10000,[[2,16,2]])

    #Table 3
    run_tests(100,[[2,30,3]])

    #Table 4
    run_tests_factors(100,[[2,26,2]])


if __name__ == '__main__':
    main()
