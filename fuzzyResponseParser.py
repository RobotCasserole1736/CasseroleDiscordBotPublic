from fuzzywuzzy import fuzz
from fuzzywuzzy import process

class FuzzyResponseParser():

    """
    Fuzzy text string parser to attempt to figure out what you wanted, based on some known things to do.
    """

    #Strings which carry no meaning and can be safely removed prior to process
    discardStrings = ["can you", "please", "will you", "I need a", "just", "would you", "pretty please"]

    # Fuzzy Match commands
    callinCommandMentors = ["Call in to mentor voice channel", "Start mentor voice call", "Call mentors", "callinMentor", "Call the mentors"]
    callinCommandTeam = ["Call in to team voice channel", "Start team voice call", "Call team", "Call in", "Team call", "callin", "callinTeam", "Call the team"]
    holdCommands = ["Hold", "silence the line", "Apply the cone of silence"]
    hangUpCommands = ["Hang Up", "hangup", "say goodbye", "end call"]
    helpCommands = ["Help", "What do I do", "How do I"]
    rebootCommands = ["Restart", "reboot", "turn on and off again"]
    greetings = ["hello", "hi", "how are you", "how ya doin", "greetings", "salutations"]


    CALLIN_MENTORS_REQUESTED = 1
    CALLIN_TEAM_REQUESTED    = 2
    HOLD_REQUESTED           = 2
    HANG_UP_REQUESTED        = 4
    HELP_REQUESTED           = 5
    REBOOT_REQUESTED         = 6
    GREETING                 = 7

    fuzzyMatchDict = {CALLIN_MENTORS_REQUESTED:callinCommandMentors,
                      CALLIN_TEAM_REQUESTED   :callinCommandTeam,
                      HOLD_REQUESTED          :holdCommands,
                      HANG_UP_REQUESTED       :hangUpCommands,
                      HELP_REQUESTED          :helpCommands,
                      REBOOT_REQUESTED        :rebootCommands,
                      GREETING                :greetings
                     }

    niceNameMatchDict = {CALLIN_MENTORS_REQUESTED:"Call-In Mentors",
                         CALLIN_TEAM_REQUESTED   :"Call-In Team",
                         HOLD_REQUESTED          :"Hold",
                         HANG_UP_REQUESTED       :"Hang Up",
                         HELP_REQUESTED          :"Help",
                         REBOOT_REQUESTED        :"Reboot",
                         GREETING                :"Greeting"
                        }

    # Default fallback response
    response = "Did you ever hear the tragedy of Darth Plagueis The Wise? I thought not. It's not a story the Jedi would tell you. It's a Sith legend. Darth Plagueis was a Dark Lord of the Sith, so powerful and so wise he could use the Force to influence the midichlorians to create life… He had such a knowledge of the dark side that he could even keep the ones he cared about from dying. The dark side of the Force is a pathway to many abilities some consider to be unnatural. He became so powerful… the only thing he was afraid of was losing his power, which eventually, of course, he did. Unfortunately, he taught his apprentice everything he knew, then his apprentice killed him in his sleep. Ironic. He could save others from death, but not himself."


    def __init__(self):
        pass

    def getBestFuzzyMatchScore(self, inputString, testStrings):
        maxScore = 0
        inputString = inputString.lower()
        for string in testStrings:
            string = string.lower()
            score = 100
            score *= fuzz.partial_ratio(inputString, string)/100
            score *= fuzz.token_sort_ratio(inputString, string)/100
            score *= fuzz.token_set_ratio(inputString, string)/100
            maxScore = max(score, maxScore)
        return maxScore

    def fuzzyParse(self, inputString):
        self.results = {}
        print(inputString)
        for key in self.fuzzyMatchDict:
            self.results[key] = self.getBestFuzzyMatchScore(inputString, self.fuzzyMatchDict[key])

        bestGuess = max(self.results, key=self.results.get)
        bestPct = self.results[bestGuess]
        if(bestPct < 15.0):
            bestGuess = None
            msg = "FuzzyParse: Unknown input string"
        else:
            msg = "FuzzyParse: Resolved input string to {} with {}%% certanty".format(self.niceNameMatchDict[bestGuess], bestPct)

        print(msg)
        return(bestGuess)

    def parse(self, inputString):
        # Clean up the querey
        for discardString in self.discardStrings:
            inputString = inputString.replace(discardString, "")

        inputString = inputString.strip()
        return self.fuzzyParse(inputString)


if __name__ == "__main__":
    testObj = FuzzyResponseParser()
    testObj.parse("Hello")
    testObj.parse("Call in")
    testObj.parse("Plase cal in")
    testObj.parse("Please call in to the mentor voice channel")

    while(True):
        inString = input(">")
        print(testObj.parse(inString))