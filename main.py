import time 
import dealer
import party
import ecdsa
from ecpy.curves import Curve
from ecpy.keys import ECPrivateKey


def input_sharing(parties, issuer, trusted_dealer):
    """
        parties         -> A list containing parties participating in the protocol
        issuer          -> The party who is doing the input sharing
        trusted_dealer  -> The trusted dealer the is used in the protocol 

        Helper function to the main protocol which handles the input sharing of the secret key.
    """
    #Dealer prepares a shares for input sharing
    trusted_dealer.prepare_new_a_shares()    
    #Dealer distributes shares to all parties
    trusted_dealer.distribute_a_shares()

    #All parties open [a] to party 1 which is the one having the sk in case
    for party in parties:
        party.private_open_a(1)

    #Party IDs starts from 1. Hence issuer-1.
    parties[issuer-1].alpha_comp_open()

    for party in parties:
        party.compute_share_of_party(issuer)

def status_printer(epoch, total):
    """
        Helper function to print how far we are.
        Prints every 5 percent.
    """
    if epoch % (total / 10):
        print("{0} % done so far".format(int(epoch/total*100)))

def run_protocol(number_of_parties, p, sk, pk, total = 1):
    """
        number_of_parties -> Specifies the number of parties that are participating in the protocol
        p                 -> Modulus to be used. Is the order of the group of the elliptic curve used in Bitcoin.
        sk                -> The secret key to be used in the protocol. Based on an elliptic curve.
        pk                -> The public key to be used in  the protocol. Based on an elliptic curve.
        total             -> The number of times to execute the signature generation.

        The final MPC ECDSA signature is: s = rx * [sk_prime] + H(M) * inverse of k
        The protocol splits the computation into three parts
        1) Independent preprocessing
        2) Dependent preprocessing
        3) Signature generation!?!??!?!?!?!??!
    """
    before = time.time()
    trusted_dealer = dealer.Dealer(number_of_parties, p)
    ecdsa_signer = ecdsa.Ecdsa()
    parties = []

    #Creates n parties in a map
    # ID -> Party object
    for ID in range(1, number_of_parties+1):
        parties.append(party.Party(trusted_dealer,ID,0))
    parties[0].v = sk.d

    #Makes it so each party knows of each other
    for participant in parties:
        for tmp in parties:
            participant.parties[tmp.ID] = tmp

    #Adds the parties to the trusted dealer
    for x in parties:
        trusted_dealer.new_party(x)

    for epoch in range(total):
        status_printer(epoch, total)
        input_sharing(parties, 1, trusted_dealer)

        trusted_dealer.distribute_mult_shares(('c', 'a', 'b'))        
        
        for x in parties:
            x.independent_preprocessing_setup()

        for x in parties:
            x.independent_preprocessing()

        trusted_dealer.distribute_mult_shares(('w','u','v'))

        for x in parties:
            x.dependent_preprocessing_setup(1)

        for x in parties:
            x.dependent_preprocessing()

        for x in parties:
            x.sign_setup()

        for x in parties:
            x.sign(M)

        signatures = []
        for x in range(0, n):
            signatures.append(parties[x].gather_signature())

        for x in signatures:
            for y in signatures:
                assert(x == y)

        ecdsa_class_sign = ecdsa_signer.sign(M, sk)
        
        #Asserts that the signature computed using ECDSA class and the MPC ECDSA actually is verifiable. 
        assert(ecdsa_signer.verify(M, ecdsa_class_sign, pk))
        assert(ecdsa_signer.verify(M, signatures[0], pk))
    print("In seconds")
    print("Total time for {0} signatures: {1}".format(total, time.time() - before))
    print("Time per sighnature on avergae: ", (time.time() - before) / total)



#Curve used in bitcoin is secp256k1
curve = Curve.get_curve('secp256k1')
sk = ECPrivateKey(12341239804712098341234123412351234126354233141, curve)
pk = sk.get_public_key()
M = b'MessageToBeSigned!' 
n = 20
p = curve.order

run_protocol(n, p, sk, pk, 100)