from ecpy.curves import Curve, Point
from ecpy.keys import ECPrivateKey, ECPublicKey
import hashlib
class Party:
    def __init__(self, dealer, ID, v):
        """
            self.ID           -> Is the ID of the party
            self.parties        -> List of other parties participating in the protocol
            self.bedoza_vals  -> Dictionary that stores bedoza values. e.g. ID-alpha -> secret sharing of alpha
            self.party_shares -> Stores the shares received from the input sharing phase
                                 For BeDOZa ECDSA party_j has: 1 -> party_j shares of party 1's secret key.
            self.v            -> Is the value that the party supplies to the protocol. I.e the secret key.
        """
        self.dealer = dealer
        self.ID = ID
        self.v = v
        self.share_a = -1

        self.parties = {}
        self.a_shares = {}
        self.bedoza_vals = {}
        self.party_shares = {}

        self.curve = Curve.get_curve('secp256k1')
        self.order = self.curve.order
        self.p = self.curve.order 

    def alpha_comp_open(self):
        """
            Computes and opens the alpha value used in the input sharing phase.
            This is the value that other parties will use to compute their own share of the value v
        """
        a = sum(self.a_shares.values()) + self.share_a
        alpha = (a - self.v) % self.p
        self.public_open(alpha, 'alpha')

    def private_open_a(self, ID):
        self.parties[ID].a_shares[str(self.ID)] = self.share_a

    def public_open(self, v, t):
        """
            v  -> The value to be publicly opened
            t  -> The extension the value is stored with in self.bedoza_vals
        """
        for _, c in self.parties.items():
            c.bedoza_vals[str(self.ID)+'-'+t]=v
    
    def compute_share_of_party(self, ID):
        """
            ID -> The ID of the party who's value parties are computing a share for

            The function is called by a party that wants to compute its own share of some value
            The randomness of a generated by the dealer masks the real value
        """
        if self.ID == ID:
            tmp = 0 
            for k, _  in self.a_shares.items():
                if not k == str(self.ID):
                    tmp += (self.bedoza_vals[str(ID)+'-'+'alpha'] + self.a_shares[k]) % self.p
            self.party_shares[str(ID)] = (self.v - tmp) % self.p
        else:
            self.party_shares[str(ID)] = (self.bedoza_vals[str(ID)+'-'+'alpha'] + self.share_a) % self.p
    
    def independent_preprocessing_setup(self):
        """
            1. The servers run ([a], [b], [c]) ← RandMul(). 
            2. Run c ← Open([c]).
        """
        self.public_open(self.bedoza_vals[str(self.ID)+'-c'], 'c')

    def independent_preprocessing(self):
        """
            Called after independent_preprocessing_setup
            Computes the steps:
                3. Let [k−1] = [a].
                4. Define ⟨k⟩ ← Convert([b]) · c−1
                5. Output (⟨k⟩, [k−1]).
            Returns a pair (⟨k⟩, [k−1])
        """
        c = 0
        for x, y in self.bedoza_vals.items():
            if 'c' in x:
                c += y % self.p
        self.k_inv_share = self.bedoza_vals[str(self.ID)+'-a']
        self.angular_k = self.bedoza_vals[str(self.ID) + '-b'] * pow(c, -1, self.p)
        
     
    def dependent_preprocessing_setup(self, ID):
        """
            ID -> The ID of the party who input shared his secret key
        
            Does the first part of BeDOZa multiplication 
            as we want to compute [sk′j] = [skj/k] ← Mul([k−1],[skj])

        """
        sk_share = self.party_shares[str(ID)]
        self.mult_p1(self.k_inv_share, sk_share)

    def dependent_preprocessing(self):
        """
            Computes the second part of the BeDOZa multiplication
            Herein the party has computed [sk′j] = [skj/k] ← Mul([k−1],[skj])
        """
        self.sk_share_prime = self.mult_p2()

    def sign_setup(self):
        """
            1. Runs R ← Open(⟨k⟩) = (bc−1)·G = a−1 ·G = k·G 2.
        """
        self.G = self.curve.generator
        R = self.angular_k * self.G
        self.public_open(R, 'R')
        
    def sign(self, M):
        """
            M -> bytestring message to be signed.        
            
            Function is called after sign_setup

            To compute the signature the following steps are computed
            2. Compute [s] = H(M) · [k−1] + rx · [sk′j].
            3. Open s ← Open([s]) and output σ = (rx, s).
        """
        
        R_shares = []
        for x, y in self.bedoza_vals.items():
            if 'R' in x:
                R_shares.append(y)

        R = self.curve.add_point(R_shares[0], R_shares[1])

        for x in R_shares[2:]:
            R = self.curve.add_point(R, x)

        self.rx = R.x
        
        hash = hashlib.sha256(M)
        hex_hash = hash.hexdigest()
        e_ = int(hex_hash, 16) 
        
        
        rx_sk_share_prime_mult = self.mult_const(self.rx, self.sk_share_prime)
        hash_M_k_inv_share_mult = self.mult_const(e_, self.k_inv_share)
        s = self.add_two_values(rx_sk_share_prime_mult, hash_M_k_inv_share_mult)
        self.public_open(s, 's')

    def gather_signature(self):
        """
            Computes the final signature by summing up all the shares
        """
        s = 0
        for x, y in self.bedoza_vals.items():
            if '-s' in x:
                s += y 
        return (self.rx, s % self.p) 
    
    def mult_const(self, c, val):
        #BeDOZa gate
        return (c * val) % self.p 

    def add_const(self, c, val):
        #BeDOZa gate
        if self.ID == 2:
            return (c + val) % self.p 
        return val
    
    def add_two_values(self, x, y):
        #BeDOZa gate
        return (x + y) % self.p

    def mult_p1(self,  x, y):
        #BeDOZa gate
        u = self.bedoza_vals[str(self.ID)+'-u']
        v = self.bedoza_vals[str(self.ID)+'-v']
        e = (x - u) % self.p
        d = (y - v) % self.p
        self.bedoza_vals[str(self.ID)+'-eps-mult'] = e
        self.bedoza_vals[str(self.ID)+'-delta-mult'] = d
        self.public_open(d, 'delta-mult')
        self.public_open(e, 'eps-mult')

    def mult_p2(self):
        #BeDOZa gate
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