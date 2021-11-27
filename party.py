class Party:
    dealer = None
    p = None
    ID = None
    v = None
    a_shares = None 
    p = None
    values = None 

    def __init__(self, dealer, ID, v):
        self.dealer = dealer
        self.p = 2
        self.ID = ID
        self.v = v
        self.p = self.dealer.get_p()
        self.peers = {}
        
        self.share_a = -1
        
        self.a_shares = {}
        self.bedoza_vals = {}
        self.party_shares = {}
    
    


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
        #peers => har alle værder der bliver beregnet i bedoza. eps, delta, a,b,c

        print ("We are in open val...")
        if t == 'a':
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
    # mod 17 
    #a = sum of a1 a2 a3
    # delta = a - x
    # a = 15 a1 4 a2 5 a3 6
    # x = 9
    # delta = 6 
    # a1 = x - (delta_A + a_a2) - (delta_A + a_a3)
    # a1 = 9 - (6+5) - (6+6) mod 17 
    #     # a2 share af x = 6 + 5 = 11 mod 17
    # a3 share af x = 6 + 5 = 12 mod 17

    

    







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
