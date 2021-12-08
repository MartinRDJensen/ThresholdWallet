import time 
import dealer
import party
import ecdsa
import random
from ecpy.curves import Curve, Point
from ecpy.keys import ECPrivateKey, ECPublicKey

curve = Curve.get_curve('secp256k1')
sk = ECPrivateKey(10, curve)
pk = sk.get_public_key()
M = b'fakjhfljas'

n = 4

#P = PRIME USED IN BITCOIN
p = 2**256-2**32-2**9-2**8-2**7-2**6-2**4-1
#d = dealer.Dealer(n, p)
before = time.time()
yolo = []
for x in range(100):
    n = random.randint(2, 100)
    yolo.append(n)
    if x % 10 == 0:
        print(x/100)
    
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

    d.prepare_new_a_shares()
    d.distribute_shares()
    for x in lst:
        x.private_open_a(1)
    d.parties[1].alpha_comp_open()
    for x in lst:
        x.compute_share_of_party(1)


    d.distribute_mult_shares(('c', 'a', 'b'))
    for x in lst:
        x.open_c_ind_pre()

    for x in lst:
        x.independent_preprocessing()


    d.distribute_mult_shares(('w','u','v'))

    for x in lst:
        x.dependent_preprocessing(1)

    for x in lst:
        x.dpre2()

    for x in lst:
        x.pre_sign()

    for x in lst:
        x.sign(M)

    signatures = []
    for x in range(0, n):
        signatures.append(lst[x].gather_signature())

    for x in signatures:
        for y in signatures:
            assert(x == y)


    a = ecdsa.Ecdsa(p)


    qad = a.sign(M, sk)
    assert(a.verify(M, qad, pk))
    assert(a.verify(M, signatures[0], pk))
print("In seconds")
print("Total time for 1000 signatures: ", time.time() - before)
print("Time per sighnature on avergae: ", (time.time() - before) / 1000 )
print("Average numbber of parties: ", sum(yolo) / 100)
yolo.sort()
print(yolo)