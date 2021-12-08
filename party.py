from ecpy.curves import Curve, Point
from ecpy.keys import ECPrivateKey, ECPublicKey
import hashlib
class Party:
    #dealer = None
    #p = None
    #ID = None
    #v = None
    #a_shares = None 
    #values = None 

    def __init__(self, dealer, ID, v):
        self.dealer = dealer
        self.ID = ID
        self.v = v
        self.p = dealer.get_p() #2**256-2**32-2**9-2**8-2**7-2**6-2**4-1
        self.peers = {}
        
        self.share_a = -1
        
        self.a_shares = {}
        self.bedoza_vals = {}
        self.party_shares = {}

        self.curve = Curve.get_curve('secp256k1')
        self.order = self.curve.order
    

    def alpha_comp_open(self):
        a = sum(self.a_shares.values()) + self.share_a
        alpha = (a - self.v) % self.p
        self.open_val(alpha, 'alpha')

    def private_open_a(self, ID):
        self.peers[ID].a_shares[str(self.ID)] = self.share_a

    def open_val(self, v, t):
        for _, c in self.peers.items():
            c.bedoza_vals[str(self.ID)+'-'+t]=v
    
    def compute_share_of_party(self, ID):
        #Function to compute your own secret shares
        #the randomness of 'a' masks the true value that party ID inputs to the protocol
        if self.ID == ID:
            tmp = 0 
            for k, _  in self.a_shares.items():
                if not k == str(self.ID):
                    tmp += (self.bedoza_vals[str(ID)+'-'+'alpha'] + self.a_shares[k]) % self.p
            self.party_shares[str(ID)] = (self.v - tmp) % self.p
        else:
            self.party_shares[str(ID)] = (self.bedoza_vals[str(ID)+'-'+'alpha'] + self.share_a) % self.p
    
    def convert(self, v):
        return v % self.order
    
    def open_c_ind_pre(self):
        self.open_val(self.bedoza_vals[str(self.ID)+'-c'], 'c')

    def independent_preprocessing(self):
        """
    User independent preprocessing. The goal is to generate a pair (⟨k⟩, [k−1]) for each signature in the following way.
1. The servers run ([a], [b], [c]) ← RandMul(). 
2. Run c ← Open([c]).
3. Let [k−1] = [a].
4. Define ⟨k⟩ ← Convert([b]) · c−1
5. Output (⟨k⟩, [k−1]).
    """
        c = 0
        for x, y in self.bedoza_vals.items():
            if 'c' in x:
                c += y % self.p
        self.k_inv_share = self.bedoza_vals[str(self.ID)+'-a']

        self.angular_k = self.convert(self.bedoza_vals[str(self.ID) + '-b']) * pow(c, -1, self.order)
        
     
    def dependent_preprocessing(self, ID):
        """
        User dependent preprocessing.
        1. Take as input [skj] (the sharing of the secret key of user Uj) and (⟨k⟩,[k−1]) (an unused tuple from the previous phase).
        2. Compute [sk′j] = [skj/k] ← Mul([k−1],[skj])
        3. Output a final tuple (⟨k⟩,[k−1],[sk′j]).
        """
        sk_share = self.party_shares[str(ID)]
        self.mult_p1(self.k_inv_share, sk_share)

    def dpre2(self):
        self.sk_share_prime = self.mult_p2()

       
    def pre_sign(self):
        self.G = self.curve.generator
        R = self.angular_k * self.G
        self.open_val(R, 'R')
        
    def sign(self, M):
        """
        Given a message to be signed M and preprocessed tuple (⟨k⟩,[k−1],[sk′j]) for Uj.
        1. RunR←Open(⟨k⟩)=(bc−1)·G=a−1 ·G=k·G 2. Let(rx,ry)←R.
        3. Compute [s] = H(M) · [k−1] + rx · [sk′j].
        4. Open s ← Open([s]) and output σ = (rx, s).
        """
        
        lst = []
        for x, y in self.bedoza_vals.items():
            if 'R' in x:
                lst.append(y)

        R = self.curve.add_point(lst[0], lst[1])

        for x in lst[2:]:
            R = self.curve.add_point(R, x)

        self.rx = R.x
        
        hash = hashlib.sha256(M)
        hex_hash = hash.hexdigest()
        e_ = int(hex_hash, 16) 

        rxskjprime = self.mult_const(self.rx, self.sk_share_prime)
        hashmkinvshare = self.mult_const(e_, self.k_inv_share)
        s = self.add_two_values(rxskjprime, hashmkinvshare)
        self.open_val(s, 's')

    def gather_signature(self):
        s = 0
        for x, y in self.bedoza_vals.items():
            if '-s' in x:
                s += y #% self.order
        return (self.rx, s % self.order)


    
    def mult_const(self, c, val):
        return (c * val) % self.p 

    def private_open_share_a(self):
        return self.share_a

  
    def add_const(self, c, val):
        if self.ID == 2:
            return (c + val) % self.p 
        return val
    
    def add_two_values(self, x, y):
        return (x + y) % self.p

    def mult_p1(self,  x, y):
        u = self.bedoza_vals[str(self.ID)+'-u']
        v = self.bedoza_vals[str(self.ID)+'-v']
        e = (x - u) % self.p
        d = (y - v) % self.p
        self.bedoza_vals[str(self.ID)+'-eps-mult'] = e
        self.bedoza_vals[str(self.ID)+'-delta-mult'] = d
        self.open_val(d, 'delta-mult')
        self.open_val(e, 'eps-mult')

    def mult_p2(self):
        e = 0
        d = 0
        w = self.bedoza_vals[str(self.ID)+'-w']
        v = self.bedoza_vals[str(self.ID)+'-v']
        u = self.bedoza_vals[str(self.ID)+'-u']
        for x, y in self.bedoza_vals.items():
            if 'eps-mult' in x:
                e += y % self.p
            if 'delta-mult' in x:
                d += y % self.p
        
        tmp1 = self.mult_const(e, v)
        tmp2 = self.mult_const(d, u)
        tmp3 = self.add_two_values(w, tmp1)
        tmp4 = self.add_two_values(tmp3, tmp2)
        tmp5 = self.add_const((e*d), tmp4)
        return tmp5