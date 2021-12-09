import random 
class Dealer:
    def __init__(self, number_of_parties, p):
        """
            self.parties  -> Dictionary mapping party ID -> party object
            self.p        -> Modulus to be used in operations
            self.a        -> a value generated at random in Z_p
            self.a_shares -> shares ([a_1, ..., [a_number_of_parties]])
        """
        self.parties = {}
        self.p = p
        self.number_of_parties = number_of_parties
        self.a, self.a_shares = self.compute_shares()

    def distribute_a_shares(self):
        """
            Functions that distributes shares of self.a
        """
        for _, v in self.parties.items():
            v.share_a = self.a_shares.pop() 
        assert(len(self.a_shares) == 0)
    
    def compute_mult_shares(self):
        """
            Function that computes w = uv and shares of the 3 values.
            Returns the shares computed.
        """        
        u = random.randint(0, self.p)
        v = random.randint(0, self.p)
        w = (u * v) % self.p
        v_shares = self.compute_shares(v)
        u_shares = self.compute_shares(u)
        w_shares = self.compute_shares(w)    
        return w_shares, u_shares, v_shares
        
    def distribute_mult_shares(self, t):
        """
            Computes and distributes values of the shares used in the arithmetic multiplication.
        """
        w_shares, u_shares, v_shares = self.compute_mult_shares()
        c = 0
        for _, v in self.parties.items():
            v.bedoza_vals[str(v.ID) +'-'+ t[0]] = w_shares[c]
            v.bedoza_vals[str(v.ID) +'-'+ t[1]] = u_shares[c]
            v.bedoza_vals[str(v.ID) +'-'+ t[2]] = v_shares[c]
            c += 1

    def prepare_new_a_shares(self):
        self.a, self.a_shares = self.compute_shares()
   
    def compute_shares(self, a = None):
        """
            a -> Value to compute shares of. 
                 The number of shares computed equals the number of parties participating
            
            If a = None then it returns a value (v, shares) where v is the value shares are computed for
        """
        val_none = True if a == None else False
        fail = True
        while fail:
            if a == None:
                a = random.randint(0, self.p)
            v = a
            shares = []
            for x in range(self.number_of_parties):
                b = random.randint(0, a)
                a = a-b   
                if x == self.number_of_parties-1:
                    b +=a
                shares.append(b)
            if not 0 in shares:
                fail = False
        assert(v==sum(shares))
        if val_none:
            return (v, shares)
        return shares

    def new_party(self, party):
        self.parties[party.ID] = party
