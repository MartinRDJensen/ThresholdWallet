from ecpy.curves import Curve, Point
from ecpy.keys import ECPrivateKey, ECPublicKey
import hashlib

class Party:
    dealer = None
    p = None
    ID = None
    v = None
    a_shares = None 
    values = None 

    def __init__(self, dealer, ID, v):
        self.dealer = dealer
        self.ID = ID
        self.v = v
        self.p = self.dealer.get_p()
        self.peers = {}
        
        self.share_a = -1
        
        self.a_shares = {}
        self.bedoza_vals = {}
        self.party_shares = {}

        self.curve = Curve.get_curve('secp256k1')
        self.order = self.curve.order
    
    def delta_comp_open(self):
        a = sum(self.a_shares.values()) + self.share_a
        delta = a - self.v
        self.open_val(delta, 'delta')

    def private_open_a(self, ID):
        if ID in self.peers:
            self.peers[ID].a_shares[str(self.ID)] = self.share_a
        else:
            self.a_shares[str(self.ID)] = self.share_a
    #store a til party i der er igang med at input en value til protocollen

    def open_val(self, v, t):
        #peers => har alle værder der bliver beregnet i bedoza. eps, delta, w,u,v
        print ("We are in open val...")
        if t == 'alpha':
            for k, c in self.peers.items():
                c.a_shares[str(self.ID)+'-'+t]=v
        else:
            for k, c in self.peers.items():
                c.bedoza_vals[str(self.ID)+'-'+t]=v
        print(str(self.ID)+'-'+t)
       # input()
        #for a ID-a

    def compute_share_of_party(self, ID):
        #Function to compute your own secret shares
        #the randomness of 'a' masks the true value that party ID inputs to the protocol
        if self.ID == ID:
            tmp = 0 
            for k, _  in self.a_shares.items():
                print("A shares: ", self.a_shares)
                if not k == str(self.ID):
                    #nani the fuck k er legit == self.ID .. ?
                    print("delta val, ", self.bedoza_vals[str(ID)+'-'+'delta'])
                    print("a val, ", self.a_shares[k])
                    print("tmp before, ", tmp)
                    print("delta comp: {0} - {1}", )
                    tmp += (self.bedoza_vals[str(ID)+'-'+'delta'] + self.a_shares[k])
                    print("tmp after, ", tmp)
                    # x - (delta + secreta) 
                   # input()
            print("Computation is {0} - {1}".format(self.v, tmp))
            self.party_shares[str(ID)] = (self.v - tmp) % self.p
        else:
            print("Computation is {0} - {1}".format(self.bedoza_vals[str(ID)+'-'+'delta'], self.share_a))
            self.party_shares[str(ID)] = (self.bedoza_vals[str(ID)+'-'+'delta'] + self.share_a) % self.p
    
    def open_c_ind_pre(self):
        self.open_val(self.bedoza_vals[str(self.ID)+'-c'], 'c')
    def convert(self, v):
        return v % self.order
    def ecdsa_sign(self, M, sk):
        pass
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
        print("Value of c: ", c)
        #Secret sharing of inv(k) is just str(id)-a in bedoza vals
        k_inv_share = self.bedoza_vals[str(self.ID)+'-a']
        angular_k = self.convert(self.bedoza_vals[str(self.ID) + '-b']) * pow(c, -1, self.order)
        return angular_k, k_inv_share
    
    def dependent_preprocessing(self, k_inv_share, ID):
        """
        User dependent preprocessing.
        1. Take as input [skj] (the sharing of the secret key of user Uj) and (⟨k⟩,[k−1]) (an unused tuple from the previous phase).
        2. Compute [sk′j] = [skj/k] ← Mul([k−1],[skj])
        3. Output a final tuple (⟨k⟩,[k−1],[sk′j]).
        """
        print("*"*1000)
        print(self.party_shares)
        sk_share = self.party_shares[str(ID)]
        self.mult_p1(k_inv_share, sk_share)
    def dpre2(self):
        sk_share_prime = self.mult_p2()
        return sk_share_prime
    
    def sign(self, angular_k, M, sk_share_prime, k_inv_share):
        """
        Given a message to be signed M and preprocessed tuple (⟨k⟩,[k−1],[sk′j]) for Uj.
        1. RunR←Open(⟨k⟩)=(bc−1)·G=a−1 ·G=k·G 2. Let(rx,ry)←R.
        3. Compute [s] = H(M) · [k−1] + rx · [sk′j].
        4. Open s ← Open([s]) and output σ = (rx, s).
        """
        G = self.curve.generator
        R = angular_k * G
        rx = R.x
        print("PARTY {0} HAS RX AS: {1}".format(self.ID, rx))
        #input("ENTER TO CONT")
        hash = hashlib.sha256(M)
        hex_hash = hash.hexdigest()
        e_ = int(hex_hash, 16) 
        rxskjprime = self.mult_const(rx, sk_share_prime)
        hashmkinvshare = self.mult_const(e_, k_inv_share)
        s = self.add_two_values(rxskjprime, hashmkinvshare)
        self.open_val(rx, '-rx')
        self.open_val(s, '-s')







    #alle får et random a
    # a \in_R 
    #pi får private open a 
    #dealer random gen a, bergner n antal [a] værider og sender dem rundt
    def open_mult(self, v):
        for i in self.peers:
            i.ed.append(v)
    
    def mult_const(self, c, val):
        return (c * val) % self.p 

    def private_open_share_a(self):
        return self.share_a

    # Spørg ind til add_const til møde
    # Er det altid samme party der vil beregne?
    # x*2+4*y (3+z), hvis dette var f, kan vi så hardcode til at self.id = 'z'?
    def add_const(self, c, val, id):
        if self.ID == 3:
            return (c + val) % self.p 
        return val
    
    def add_two_values(self, x, y):
        return (x + y) % self.p

    def send_share_a(self):
        return self.share_a
    def recv_share_a(self, a):
        self.a_shares.append(a)

    def open_eps_delt(self):
        d = self.bedoza_vals[str(self.ID)+'-delta-mult']
        e = self.bedoza_vals[str(self.ID)+'-eps-mult']
        self.open_val(d, 'delta-mult')
        self.open_val(e, 'eps-mult')
    def mult_p1(self,  x, y):
        u = self.bedoza_vals[str(self.ID)+'-u']
        v = self.bedoza_vals[str(self.ID)+'-v']
        e = (x - u) % self.p
        d = (y - v) % self.p
        self.bedoza_vals[str(self.ID)+'-eps-mult'] = e
        self.bedoza_vals[str(self.ID)+'-delta-mult'] = d

    def mult_p2(self):
        e = 0
        d = 0
        w = self.bedoza_vals[str(self.ID)+'-w']
        v = self.bedoza_vals[str(self.ID)+'-v']
        u= self.bedoza_vals[str(self.ID)+'-u']
        for x, y in self.bedoza_vals.items():
            if 'eps-mult' in x:
                e += y % self.p
            if 'delta-mult' in x:
                d += y % self.p
        tmp_res = (w + e * v + d * u) % self.p
        result = self.add_const(e * d, tmp_res, 3)
        return result
