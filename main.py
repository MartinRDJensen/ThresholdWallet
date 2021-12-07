import time 
import dealer
import party
import ecdsa
import sys
from ecpy.curves import Curve, Point
from ecpy.keys import ECPrivateKey, ECPublicKey


curve = Curve.get_curve('secp256k1')
sk = ECPrivateKey(10, curve)
pk = sk.get_public_key()
print(curve.order)
input("order ^")
n = 3

#P = PRIME USED IN BITCOIN
p = 2**256-2**32-2**9-2**8-2**7-2**6-2**4-1
print(curve.order == p)
input("asdasdsa")

#d = dealer.Dealer(n, p)
d = dealer.Dealer(n, curve.order)

lst = []

for x in range(1, n+1):
    lst.append(party.Party(d,x,0))
lst[0].v = sk.d

for peer in lst:
    for tmp in lst:
        peer.peers[tmp.ID] = tmp

for x in lst:
    d.new_party(x)

#d.distribute_shares()

d.prepare_new_a_shares()
d.distribute_shares()
for x in lst:
    print("Party {0}'s share of a is {1}".format(x.ID, x.share_a))
    x.private_open_a(1)
d.parties[1].delta_comp_open()
for x in lst:
    x.compute_share_of_party(1)
    print("Party {0}'s share is {1}".format(x.ID, x.party_shares))
    input()

for x in lst:
    print("Party {0}'s value is {1}".format(x.ID, x.v))
    
#sys.exit()
tmp = 0
for x in lst:
    print("Party: ", x.ID)
    print(x.party_shares)
    tmp += x.party_shares[str(1)]
#assert(tmp % p == d.parties[1].v)
assert(tmp % curve.order == d.parties[1].v)
assert((100515067930398706113235707758617487464811881718976817032317256177315546085350+6551871769517909377616050998119117036343307990303054260159914864061069467253+8725149537399579932719226251951303351682374569795033090127992100141545941744)%curve.order == 10)
d.distribute_mult_shares2(('c', 'a', 'b'), True)
for x in lst:
    x.open_c_ind_pre()
qqq = []
for x in lst:
    qqq.append(x.independent_preprocessing())

c = 0
d.distribute_mult_shares2(('w','u','v'))
for x in lst:
    #qqq is list of touples of angular_k, k_inv_share
    x.dependent_preprocessing(qqq[c][1], 1)
    c+=1

qqqsk = []


for x in lst:
    qqqsk.append(x.dpre2())


M = b'fakjhfljas'
c= 0
for x in lst:
    x.pre_sign(qqq[c][0])
    c+=1 
c = 0
for x in lst:
    x.sign(qqq[c][0], M, qqqsk[c], qqq[c][1])
    c+=1
c = 0
z = 0
aaa = []
for x in range(0, n):
    aaa.append(lst[x].gather_signature())
    lst[x].rx
    #c+=lst[0].bedoza_vals[str(x)+'-c']
    #print(lst[0].bedoza_vals)
    #z = lst[0].bedoza_vals[str(x)+'--rx']
print("Following are the signatures")
for x in aaa:
    for y in aaa:
        if not x == y:
            print("error....")

#print("*"*1000)
#print(c)
#print(z)
a = ecdsa.Ecdsa(2**256-2**32-2**9-2**8-2**7-2**6-2**4-1)


qad = a.sign(M, sk)
print(aaa[0])
print("actual sign")
print(qad)
#print("rx")
#print(z)
#print("s")
#print(c)
#print("qad")
#print(qad)
assert(a.verify(M, aaa[0], pk))

sys.exit()



























def secret_sharing(id):
    d.prepare_new_a_shares()
    d.distribute_shares()
    for x in lst:
        x.private_open_a(id)
    d.parties[id].delta_comp_open()
    for x in lst:
        x.compute_share_of_party(id)

    for x in lst:
        ("Party {0}'s value is {1}".format(x.ID, x.v))
    tmp = 0
    for x in lst:
        #print("Party: ", x.ID)
        #print(x.party_shares)
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

#For independent processing
d.distribute_mult_shares2(('-c', '-a', '-b'))



#Ugly as method to do the mult....
#find a better way
d.distribute_mult_shares2(('-w', '-u', '-v'))
for x in lst:
        x.mult_p1(x.party_shares['1'], x.party_shares['2'])
        x.open_eps_delt()
tmp1lst = []
for x in lst:
    tmp1lst.append(x.mult_p2())
d.distribute_mult_shares2(('-w', '-u', '-v'))
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
