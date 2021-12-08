from ecpy.curves import Curve, Point
from ecpy.keys import ECPrivateKey, ECPublicKey
import hashlib
import random


#section 4 points to 
# 2) Papers https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf
# 3) which points to https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.202.2977&rep=rep1&type=pdf 



#https://en.bitcoin.it/wiki/Secp256k1
#https://ec-python.readthedocs.io/en/latest/#install  library



class Ecdsa:
    def __init__(self, p) -> None:

        """
            self.p right det er modulu værdien i bitcoin
            Kurven i bitcoin er secp256k1. Dens order er forskellig fra self.p
            secp256k1 => y^2 = x^3 + 7 mod secp256k1.order
        """
        #self.p = p
        self.curve = Curve.get_curve('secp256k1')
        #self.sk = ECPrivateKey(0xfb26a4e75eec75544c0f44e937dcf5ee6355c7176600b9688c667e5c283b43c5, self.curve)
        #self.pk = ECPublicKey(Point(0x65d5b8bf9ab1801c9f168d4815994ad35f1dcb6ae6c7a1a303966b677b813b00, 0xe6b865e529b8ecbf71cf966e900477d49ced5846d7662dd2dd11ccd55c0aff7f, self.curve))
    def sign(self, M, sk):
        #sk is private key in ecpy
        #has attributes;
        #  d (int) : private key scalar curve (Curve) : curve 
        curve = sk.curve
        G = curve.generator # generator (int[2]) : x,y coordinate of generator

        order = curve.order
        
        k = random.randint(0, order)
        k_inv = pow(k, -1, order) 
        assert(k*k_inv % order == 1)
                
        rxry = k * G
        rx = rxry.x
        if rx == 0:
            #8.636168555094445e-78 chance. Should we iterate it?
            #Since the prob is so low that it almost doesn't make sense...
            #Redo message digesting???
            #Chance 1/p
            return None
           
        hash = hashlib.sha256(M)
        hex_hash = hash.hexdigest()
        e_ = int(hex_hash, 16) #Skal det være mod p?
        
        #Hvad type vil M være?????
        #Kan H(M) være modulus eller er det gg?
        s = (k_inv*(e_+sk.d*rx)) % order
        if s == 0:
            #Chance 1/p
            return None
        return (rx, s)
    def verify(self, M, s, pk):
        hash = hashlib.sha256(M)
        hex_hash = hash.hexdigest()
        e_ = int(hex_hash, 16) #Skal det være mod p?
        
      
        rx, s_ = s

        curve = pk.curve
        order = curve.order
        G = curve.generator
        Q = pk.W

#        assert(rx >= 1 and rx <= self.p-1)
 #       assert(s_ >= 1 and s_ <= self.p-1)

        c = pow(s_, -1, order)
        u1 = (e_ * c) % order
        u2 = (rx * c) % order

        tmp = u1*G +u2*Q
        #if tmp = inf reject
        #Convert field elem x1 to int  ### NOt needed since we have mod an odd prime
        #comp v = x1_int mod self.p
        #if rx = v yay else corrupt message

        v = tmp.x % order
        
        return rx == v

#a = Ecdsa(2**256-2**32-2**9-2**8-2**7-2**6-2**4-1)
#z= a.sign(b"asa", a.sk)
#assert(a.verify(b"asa", z, a.pk))



    