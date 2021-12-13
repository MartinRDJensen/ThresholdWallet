from ecpy.curves import Curve
import hashlib
import random

class Ecdsa:
    def __init__(self) -> None:

        """
            Constructor for ECDSA class
            Elliptic curve used in bitcoin is secp256k1
            Sets up the curve values to be used in sign and verify

            Notation used in the function stems from https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.202.2977&rep=rep1&type=pdf 
        """
        self.curve = Curve.get_curve('secp256k1')
        self.order = self.curve.order
        self.G = self.curve.generator
        
    def sign(self, M, sk):
        """
            M  -> Bytestring of the message to be signed
            sk -> Is ecpy library private key. Has an attribute d which returns the private key scalar and a curve.
                  The curve is the secp256k1 curve
        """
        k = random.randint(0, self.order)
        k_inv = pow(k, -1, self.order) 
        assert(k*k_inv % self.order == 1)
                
        rxry = k * self.G
        rx = rxry.x
        if rx == 0:
            #8.636168555094445e-78 chance for this case to happen
            return None
           
        hash = hashlib.sha256(M)
        hex_hash = hash.hexdigest()
        e_ = int(hex_hash, 16) 
        
    
        s = (k_inv*(e_+sk.d*rx)) % self.order
        if s == 0:
            #8.636168555094445e-78 chance for this case to happen
            return None
        return (rx, s)
    def verify(self, M, s, pk):
        hash = hashlib.sha256(M)
        hex_hash = hash.hexdigest()
        e_ = int(hex_hash, 16)        
      
        rx, s_ = s
        Q = pk.W

        c = pow(s_, -1, self.order)
        u1 = (e_ * c) % self.order
        u2 = (rx * c) % self.order

        tmp = u1*self.G +u2*Q
 
        v = tmp.x % self.order
        
        return rx == v



    