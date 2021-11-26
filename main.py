import time 
import dealer
import party
n = 3
p = 123123288677
d = dealer.Dealer(n, p)


lst = []

for x in range(1, n+1):
    lst.append(party.Party(d,x,x*12312))
    print(x*12312)
input()
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

#x+2+y+2+z+3+z+y
vals = []
for x in lst:
    tmp1 = x.add_const(2, x.party_shares['1'], 3)
    print("tmp1: ", tmp1)
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
    tmp1 = x+2 % p
    tmp2 = y+2 % p
    tmp3 = z+3 % p
    tmp4 = y+z % p
    tmp5 = tmp1 + tmp2 % p
    tmp6 = tmp3 + tmp4 % p
    tmp7 = tmp5+tmp6 % p
    return (x+2+y+2+z+3+z+y) % p



