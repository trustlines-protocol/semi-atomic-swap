# semi-atomic-swap contracts

**Buy crypto with Trustlines.** 
This repository holds the proof-of-concept contracts necessary
to do a "semi-atomic-swap". One could for example exchange ETH against "Trustlines money" (TL Money)
provided that there is a path between the initiator and counterparty wishing to enter the deal.
**And this without a central party!**

I'm not calling the swap "atomic", because we are currently not locking the path capacity. This means
that even if at the moment of entering a deal there is a path between the users, there is no guarantee
that the path will still exist when the user wants to claim his TL Money.

In the future we can mitigate this problem by either locking the path capacity or on a failing `transferFrom` call
we could write a dept claim in the currency network.  
