from owll_clust import clust_op_names
from owll_opd import gen_opd
from owll_stats import update_all_stats
from owll_typoclass import class_with_typo_words
from util import prt
from util import rem_empty


class Command:
    def __init__(self, name, description, labels, usage, fct):
        self.name = name
        self.description = description
        self.labels = labels
        self.usage = usage
        self.fct = fct

    def call(self, args: str):
        self.fct(args)


class Terminal:
    def __init__(self):
        self.leaving = False
        self.userInput = ""
        self.commands = [
            Command("TypoClass", "Basic classification with relational words of \"Typologie des mots de liaisons\".",
                    ["typo"], "typo", class_with_typo_words),
            Command("Clust", "Test of some clusterisation algorithms on object properties names with FastText.",
                    ["clust"], "clust", clust_op_names),
            Command("Generate OPD", "Regenerate Object Property Database (OPD).",
                    ["genopd"], "genopd", gen_opd),
            Command("Get Stats", "Update all statistics from OPD.",
                    ["genstats"], "genstats", update_all_stats),
            Command("Help", "Display list of commands or show description and usage of a specific command.",
                    ["help"], "help [command]", self.help),
            Command("Quit", "Leave the OWLL terminal.",
                    ["quit", "exit"], "quit|exit", self.quit),
        ]

    def searchCommand(self, userIn: str) -> (Command, str):
        commandFound = None
        userInSplit = rem_empty(userIn.split(" "))
        commandName = userInSplit[0]
        args = " ".join(userInSplit[1:])

        for command in self.commands:
            if commandName in command.labels:
                commandFound = command
                break
        return commandFound, args

    def launch(self):
        prt("OWLL terminal is launched. Enter your command (type \"help\" for details):")
        while not self.leaving:
            self.userInput = input("> ")
            self.userInput = self.userInput.lower().strip()
            command, args = self.searchCommand(self.userInput)
            if command is not None:
                command.call(args)
                prt("Command \"%s\" finished." % self.userInput)
            else:
                prt("Unknown command \"%s\"." % self.userInput)

    def help(self, args: str):
        argsSp = args.split()
        if len(argsSp) == 0:
            prt("List of availible commands: ")
            for command in self.commands:
                prt("  %-20s : %s" % (command.usage, command.description))
        else:
            commandName = argsSp[0]
            found = False
            for command in self.commands:
                if commandName == command.name or commandName in command.labels:
                    prt("%-20s %-20s" % ("Name:", command.name))
                    prt("%-20s %-20s" % ("Usage:", command.usage))
                    prt("%-20s %-20s" % ("Description:", command.description))
                    found = True
                    break
            if not found:
                prt("Unknown command \"%s\"." % commandName)

    def quit(self, args: str):
        self.leaving = True


def main():
    terminal = Terminal()
    terminal.launch()


if __name__ == "__main__":
    main()
