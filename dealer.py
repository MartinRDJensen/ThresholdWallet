import random 
class Dealer:
    parties = None
    a = None 
    a_shares = None
    def __init__(self, n, p) -> None:
        self.parties = {}
        self.p = p
        self.n = n
#        self.a, self.a_shares = self.gen_shares_of_a(self.n)

    def distribute_shares(self):
        for k, v in self.parties.items():
            v.share_a = self.a_shares.pop() 
        assert(len(self.a_shares) == 0)

    def prepare_new_a_shares(self):
        self.a, self.a_shares = self.gen_shares_of_a(self.n)

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

#lav dealer
#cliensts får dealer med
#client enlist 
