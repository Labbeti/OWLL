from owll_clust import clust_op_names
from owll_opd import gen_opd
from owll_stats import update_all_stats
from owll_typoclass import class_with_typo_words
from utils import prt


class Command:
    def __init__(self, name, description, strings, usage, fct):
        self.name = name
        self.description = description
        self.strings = strings
        self.usage = usage
        self.fct = fct


class Terminal:
    def __init__(self):
        self.commands = [
            Command("TypoClass", "Basic classification with relational words of \"Typologie des mots de liaisons\"",
                    ["typo"], "typo", class_with_typo_words),
            Command("Clust", "Test of some clusterisation algorithms on object properties names with FastText.",
                    ["clust"], "clust", clust_op_names),
            Command("Generate OPD", "Regenerate Object Property Database (OPD)",
                    ["genopd"], "genopd", gen_opd),
            Command("Get Stats", "Update all statistics from OPD.",
                    ["genstats"], "genstats", update_all_stats),
            Command("Help", "Display list of commands or show description and usage of a specific command.",
                    ["help"], "help [command]", self.help),
            Command("Quit", "Leave the application.",
                    ["quit", "exit", "logout"], "quit|exit|logout", self.quit),
        ]
        self.leaving = False
        self.userInput = ""

    def searchCommand(self, userIn: str) -> Command:
        found = False
        commandFound = None
        for command in self.commands:
            for string in command.strings:
                if userIn.startswith(string):
                    found = True
                    commandFound = command
                    break
            if found:
                break
        return commandFound

    def launch(self):
        prt("Sub terminal launch. Enter your command: ")
        while not self.leaving:
            self.userInput = input("> ")
            self.userInput = self.userInput.lower()
            command = self.searchCommand(self.userInput)
            if command is not None:
                command.fct()
                prt("Command \"%s\" finished." % self.userInput)
            else:
                prt("Unknown command \"%s\"." % self.userInput)

    def help(self):
        if self.userInput == "help":
            prt("List of availible commands: ")
            for command in self.commands:
                prt(" - %-20s : %s" % (command.usage, command.description))
        else:
            splitted = self.userInput.split(" ")
            commandName = " ".join(splitted[1:])
            found = False
            for command in self.commands:
                if commandName == command.name or commandName in command.strings:
                    prt("%-15s %-20s" % ("Name:", command.name))
                    prt("%-15s %-20s" % ("Usage:", command.usage))
                    prt("%-15s %-20s" % ("Description:", command.description))
                    found = True
                    break
            if not found:
                prt("Unknown command \"%s\"." % commandName)

    def quit(self):
        self.leaving = True


def main():
    terminal = Terminal()
    terminal.launch()


if __name__ == "__main__":
    main()
