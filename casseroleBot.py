import discord
from tkinter import Tk, Label, Button, StringVar
import threading
import asyncio
import time, math, random
import sounddevice as sd
from audioHandling import *
from botGUIControl import *
from cheerHandler import *
from theBlueAlliance import *
from revolabsFLXInterface import *

import os,sys
sys.path.append("..")
import APIKeys


helpStr = " Hi {}! I'm the Casserole Discord Bot! \n" \
          " I know a few cheers which I'll respond to. \n" \
          " I also function as a conference phone (still WIP). \n" \
          " The phone is controlled with the following commands: \n" \
          "   `$callin` - Causes me to call into the Team Meetings channel \n" \
          "   `$hangup` - Causes me to leave the Team Meetings channel \n" \
          "   `$hold`   - Toggles whether I broadcast the microphone, or some spiffy on-hold music. \n" \
          " Finally, I'm hooked into the Blue Alliance for fun and profit. Ask me things like: \n" \
          "   `$whois <team number>` - I'll look up the team name. \n\n" \
          " Play around and have some fun! Talk to programming team if you want me to learn to do new things. \n"



# Actual discord API. This is what does the heavy lifting
class CasseroleDiscordBotClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #Because team spirit is a real award:
        self.cheer = CheerHandler()
        #And becuase looking up stuff on the TBA is fun
        self.tbaInfo = TBAInfo()

        #self.audioSource = TestAudioSource()
        print("Creating audio Sources & Sinks...")
        self.mikeAudioSource = MicrophoneAudioSource()
        self.holdAudioSource1 = WaveFileAudioSource('./hold1.wav')
        self.holdAudioSource2 = WaveFileAudioSource('./hold2.wav')
        self.audioSink = SpeakerAudioSink()
        #self.audioSink   = NullAudioSink()
        self.buttonsInterface = RevolabsFLXInterface()
        print("Audio hardware setup complete!")

        
        self.voiceClient = None

        #Inputs from the outside world - changing these will change the Client state
        self.connectRequest = False
        self.shutdownRequest = False
        self.holdRequest = False

        #Outputs to the rest of the world - other classes should read these
        self.speakingUserString = "..."

        self.isLoggedIn= False
        self.isConnected= False
        self.connectRequestPrev = False
        self.holdRequestPrev = False

        self.callBtnPressCntPrev = 0
        self.muteBtnPressCntPrev = 0

        # Trigger a periodic loop to update the Client state based on GUI inputs
        self.loop.create_task(self.periodicStateCheck())

    # Initiates the Audio Connection
    async def voiceConnect(self):
        if(self.voiceClient == None):
            print("Attempting to connect to voice channel {}".format(PHONE_VOICE_CHANNEL_NAME))
            channel = discord.utils.get(client.get_all_channels(), name=PHONE_VOICE_CHANNEL_NAME)
            self.voiceClient = await channel.connect()
            self.voiceClient.play(self.mikeAudioSource)
            self.voiceClient.listen(self.audioSink)
            self.isConnected = True
            self.holdRequest = False
            self.holdRequestPrev = False
            print("Connected!")

    # Starts on-hold music
    async def enableHold(self):
        if(self.voiceClient is not None):
            try:
                self.voiceClient.stop()
                self.voiceClient.stop_listening()
            except Exception as e:
                print(e)
            time.sleep(0.5)
            if(bool(random.getrandbits(1))):
                self.voiceClient.play(self.holdAudioSource1)
            else:
                self.voiceClient.play(self.holdAudioSource2)


    # Starts on-hold music
    async def disableHold(self):
        if(self.voiceClient is not None):
            try:
                self.voiceClient.stop()
            except Exception as e:
                print(e)
            time.sleep(0.5)
            self.voiceClient.play(self.mikeAudioSource)
            self.voiceClient.listen(self.audioSink)


    # Ends the Audio Connection
    async def hangUp(self):
        if(self.voiceClient is not None):
            print("Attempting to hang up from voice channel {}".format(PHONE_VOICE_CHANNEL_NAME))
            try:
                self.voiceClient.stop()
                self.voiceClient.stop_listening()
            except Exception as e:
                print(e)
            time.sleep(1.0)
            await self.voiceClient.disconnect()
            self.voiceClient = None
            self.isConnected = False
            print("Disconnected!")

    # Hook to capture Discord Login Event
    async def on_ready(self):
        print('Logged in to Discord as {} - ID {}'.format(self.user.name, self.user.id))
        print('Ready to recieve commands!')
        self.isLoggedIn = True
        

    # Hook to process incoming text
    async def on_message(self, message):
        if message.author == self.user:
            return

        await self.cheer.update(message)

        # Handle phone commands
        if message.content.startswith('$callin'):
            print("Connect Command from {}".format(message.author))
            await self.voiceConnect()

        if message.content.startswith('$hangup'):
            print("Disconnect Command from {}".format(message.author))
            await self.hangUp()

        if message.content.startswith('$hold'):
            print("Hold State Change Command from {}".format(message.author))
            self.holdRequest = not(self.holdRequest)

        # Handle help commands
        if message.content.startswith('$help'):
            print("Help request {}".format(message.author))
            await message.channel.send(helpStr.format(message.author))

        # Handle some lookup commands
        results = re.search("\$whois ([0-9]+)", message.content)
        if(results):
            lookupStr = results.group(1).strip()
            try:
                teamNum = int(lookupStr)
                await message.channel.send("Team {} is '{}'".format(teamNum, self.tbaInfo.lookupTeamName(teamNum)))
            except Exception as e:
                print(e)
                await message.channel.send("Sorry, not sure what team '{}' is.".format(lookupStr))


    # Main periodic loop 
    async def periodicStateCheck(self):
        while(True):
            if(self.isLoggedIn):    
                #Only run updates if we're connected

                #Handle inputs from the physical speaker
                if(self.buttonsInterface.callBtnPressCount != self.callBtnPressCntPrev):
                    self.callBtnPressCntPrev = self.buttonsInterface.callBtnPressCount
                    self.connectRequest = not(self.connectRequest)

                if(self.buttonsInterface.muteBtnPressCount != self.muteBtnPressCntPrev):
                    self.muteBtnPressCntPrev = self.buttonsInterface.muteBtnPressCount
                    self.holdRequest = self.buttonsInterface.phoneMute


                #Check if connection request has changed
                if(self.connectRequest != self.connectRequestPrev):
                    #Call or hang up as needed
                    print("Connection request changed to {}".format(self.connectRequest))
                    if(self.connectRequest):
                        await self.voiceConnect()
                    else:
                        await self.hangUp()
                    self.connectRequestPrev = self.connectRequest

                #Check if hold request has changed
                if(self.holdRequest != self.holdRequestPrev):
                    print("Hold request changed to {}".format(self.holdRequest))
                    if(self.holdRequest == True):
                        await self.enableHold()
                    else:
                        await self.disableHold()
                    self.holdRequestPrev = self.holdRequest

                #Update LED State
                # print("hold: {} | connect: {}".format(self.holdRequest, self.connectRequest))
                # if(self.holdRequest == True or self.connectRequest == False):
                #     self.buttonsInterface.setLedsMuted()
                # else:
                #     print("here")
                #     self.buttonsInterface.setLedsUnmuted()

                # Update the string representing the curretly-speaking user
                if(self.connectRequest == True ):
                    member = self.guilds[0].get_member(self.audioSink.curSpeakerID)
                    if(member is not None):
                        if member.nick is not None:
                            self.speakingUserString = str(member.nick)
                        else:
                            self.speakingUserString = str(member)
                else:
                    self.speakingUserString = "..."

                # Check if we're supposed to shut down.
                if(self.shutdownRequest == True):
                    print("Shutting Down...")
                    await self.shutDown()
                    return

            # Allow other stuff to run
            await asyncio.sleep(0.25)


    async def shutDown(self):
        await self.logout()


#############################################
## Main code execution starts here
if __name__ == "__main__":
    client = CasseroleDiscordBotClient()
    #gui = CasseroleDiscordBotGUI(client) #temp, no gui for now.
    #gui.start()
    print("Starting up Casserole Discord Bot....")
    client.run(APIKeys.DISCORD_CLIENT_BOT_KEY)


