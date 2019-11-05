import re


class CheerHandler():

    def __init__(self):
        self.message = None
        self.responsePhrase = ""

    async def callResponse(self, call, response):
        if self.message.content.strip().lower() == call.lower():
            await self.message.channel.send(response)

    async def update(self, message):

        if message.content.startswith('$hello'):
            print("Responding to greeting from {}".format(message.author))
            await message.channel.send("Hello!")
        
        # Handle Simple call/response cheers
        self.message = message
        await self.callResponse("17", "36!")
        await self.callResponse("Robot", "Casserole!")
        await self.callResponse("Casserole Casserole", "Eat it Up! Eat it Up!")
        await self.callResponse("What time is it?", "Nine Thirty!")
        await self.callResponse("Four on Three", "One! Two! Three! Four!")
        await self.callResponse("Who's Hungry?", "I'm Hungry!")
        await self.callResponse("For What?", "Casserole!!!")
        await self.callResponse("yay", "YAAAAAYYYYY!!!!")
        await self.callResponse("Who's Hungary?", "The Hungarians! https://en.wikipedia.org/wiki/Hungary")

        ## Handle "Give me a..." cheers
        results = re.search("Give me a[n]? (.*)", message.content)
        if(results):
            subphrase = results.group(1).strip()
            self.responsePhrase += subphrase
            await self.message.channel.send(subphrase + "!")
        if(self.message.content.startswith("What does that spell?")):
            if(len(self.responsePhrase) > 0):
                await self.message.channel.send(self.responsePhrase + "!")
                self.responsePhrase = ""


        
