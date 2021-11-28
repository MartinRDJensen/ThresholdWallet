import time 
import dealer
import party
n = 3

#P = PRIME USED IN BITCOIN
p = 2**256-2**32-2**9-2**8-2**7-2**6-2**4-1
d = dealer.Dealer(n, p)

lst = []

for x in range(1, n+1):
    lst.append(party.Party(d,x,x*2))

for peer in lst:
    for tmp in lst:
        peer.peers[tmp.ID] = tmp
for x in lst:
    d.new_party(x)
#d.distribute_shares()

def secret_sharing(id):
    d.prepare_new_a_shares()
    d.distribute_shares()
    for x in lst:
        x.private_open_a(id)
    d.parties[id].delta_comp_open()
    for x in lst:
        x.compute_share_of_party(id)

    for x in lst:
        print("Party {0}'s value is {1}".format(x.ID, x.v))
    tmp = 0
    for x in lst:
        print("Party: ", x.ID)
        print(x.party_shares)
        tmp += x.party_shares[str(id)]
    assert(tmp %p == d.parties[id].v)

#f(x,y,z) = x*2+y*2+z*2+(x+2)+(y+2)+(z+2)*(x+y)

for x in lst:
    secret_sharing(x.ID)

#x = 1

#y = 2
#z = 3 

#x*y*z+y+2+z+3+z+y
#distribute_mult_shares
vals = []


######################################################################################
#Ugly as method to do the mult....
#find a better way
d.distribute_mult_shares()
for x in lst:
        x.mult_p1(x.party_shares['1'], x.party_shares['2'])
        x.open_eps_delt()
tmp1lst = []
for x in lst:
    tmp1lst.append(x.mult_p2())
d.distribute_mult_shares()
c = 0
for x in lst:
    x.mult_p1(tmp1lst[c], x.party_shares['3'])
    x.open_eps_delt()
    c+=1
tmp2lst = []
for x in lst:
    tmp2lst.append(x.mult_p2())
######################################################################################


c = 0
for x in lst:
    tmp1 = tmp2lst[c]
    c+=1
    #tmp1 = x.mult_p2()        
    #tmp1 = x.add_const(2, x.party_shares['1'], 3)
    #print("tmp1: ", tmp1)
    tmp2 = x.add_const(2, x.party_shares['2'], 3)
    print("tmp2: ", tmp2)
    tmp3 = x.add_const(3, x.party_shares['3'], 3)
    print("tmp3: ", tmp3)
    tmp4 = x.add_two_values(x.party_shares['2'], x.party_shares['3'])
    print("tmp4: ", tmp4)


    tmp5 = x.add_two_values(tmp1, tmp2)
    print("tmp5: ", tmp5)
    tmp6 = x.add_two_values(tmp3, tmp4)
    print("tmp6: ", tmp6)
    tmp7 = x.add_two_values(tmp5, tmp6)
    print("tmp7: ", tmp7)
    vals.append(tmp7)
    print(vals)

def kekw(x,y,z):
    return (x*y*z+y+2+z+3+z+y) % p

print("sum vals, ", sum(vals) % p)
print(kekw(2, 4, 6))
assert(sum(vals) % p == kekw(2, 4, 6))
