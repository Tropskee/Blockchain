## Creating a Blockchain From Scratch
I was struggling to understand the technology behind Blockchains, and decided that the best way to learn is by doing. 

Here is my attempt at creating a (very basic) Blockchain from scratch.

I’ve written the initial project with Python, using Flask for the API.

I am currently working on a few other versions which I will add upon completion:
	- Javascript version
	- Dockerized version

### Flask PostMan API Commands
These are the commands used to interact with the Blockchain via http.
I am using PostMan as it makes this easy, but you could just as easily curl.

Mine 1 block on current node
GET
http://localhost:5000/mine

Create a new transaction
POST
http://localhost:5000/transactions/new

'''JSON
{
	“sender” : “d4ee26eee15148ee92c6cd394edd974e”
	"recipient": "someone-other-address",
 	"amount": 5
}
'''

Examine current chain

GET

http://localhost:5000/chain

Register a new node on a different port

POST

http://localhost:5000/nodes/register

‘’’JSON
{
	“nodes”: [“http://127.0.0.1:5001”]
}
‘’’


Resolve nodes to find true chain

Note: Longer chain wins

GET

http://localhost:5000/nodes/resolve



