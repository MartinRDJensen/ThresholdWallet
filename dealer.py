import random 
class Dealer:
    parties = None
    a = None 
    a_shares = None
    def __init__(self, n, p) -> None:
        self.parties = {}
        self.p = p
        self.n = n
        self.a, self.a_shares = self.gen_shares_of_a(self.n)

    def distribute_shares(self):
        for _, v in self.parties.items():
            v.share_a = self.a_shares.pop() 
        assert(len(self.a_shares) == 0)
    def gen_mult_vals(self):        
        u = random.randint(0, self.p)
        v = random.randint(0, self.p)
        w = (u * v) % self.p
        v_shares = self.gen_shares_of_a2(v, self.n)
        u_shares = self.gen_shares_of_a2(u, self.n)
        w_shares = self.gen_shares_of_a2(w, self.n)    
        return w_shares, u_shares, v_shares
        
    def distribute_mult_shares(self):
        w_shares, u_shares, v_shares = self.gen_mult_vals()
        c = 0
        for _, v in self.parties.items():
            v.bedoza_vals[str(v.ID) + '-w'] = w_shares[c]
            v.bedoza_vals[str(v.ID) + '-u'] = u_shares[c]
            v.bedoza_vals[str(v.ID) + '-v'] = v_shares[c]
            c += 1
    
    def distribute_mult_shares2(self, t):
        w_shares, u_shares, v_shares = self.gen_mult_vals()
        c = 0
        for _, v in self.parties.items():
            v.bedoza_vals[str(v.ID) +'-'+ t[0]] = w_shares[c]
            v.bedoza_vals[str(v.ID) +'-'+ t[1]] = u_shares[c]
            v.bedoza_vals[str(v.ID) +'-'+ t[2]] = v_shares[c]
            c += 1
    

    def prepare_new_a_shares(self):
        self.a = random.randint(0, self.p)
        self.a_shares = self.gen_shares_of_a2(self.a, self.n)

   
    def gen_shares_of_a2(self, val, n):
        fail = True
        while fail:
            # # use n to create n shares
            v = val
            lst = []
            for x in range(n):
                b = random.randint(0, val)
                val = val-b   
                if x == n-1:
                    b +=val
                lst.append(b)
            if not 0 in lst:
                fail = False
        assert(v==sum(lst))
        return lst


    def gen_shares_of_a(self, n):
        fail = True
        while fail:
            a = random.randint(0, self.p) # use n to create n shares
            v = a
            lst = []
            for x in range(n):
                b = random.randint(0, a)
                a = a-b   
                if x == n-1:
                    b +=a
                lst.append(b)
            if not 0 in lst:
                fail = False
        assert(v==sum(lst))
        return (v, lst)

    def get_p(self):
        return self.p 

    def new_party(self, party):
        self.parties[party.ID] = party
