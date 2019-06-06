from owll_clust import clust_op_names
from owll_gensim import gen_gensim_clust
from owll_opd import gen_opd
from owll_stats import update_all_stats
from owll_typoclass import class_with_typo_words
from util import prt
from util import split_input


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
        self.commands = [
            Command("TypoClass", "Basic classification with relational words of \"Typologie des mots de liaisons\".",
                    ["typo"], "typo", class_with_typo_words),
            Command("Clust", "Test of some clusterisation algorithms on object properties names with FastText.",
                    ["clust"], "clust", clust_op_names),
            Command("Generate OPD", "Regenerate Object Property Database (OPD) with the ontologies found in "
                                    "\"dir_onto\"",
                    ["genopd"], "genopd [dir_onto [dir_results]]", gen_opd),
            Command("Get Stats", "Update all statistics from OPD.",
                    ["genstats"], "genstats", update_all_stats),
            Command("Test gensim", "Try Agglomerative clusterisation with distance matrix generated with gensim.",
                    ["gengensim"], "gengensim", gen_gensim_clust),
            Command("Help", "Display list of commands or show description and usage of a specific command.",
                    ["help"], "help [command]", self.help),
            Command("Quit", "Leave the OWLL terminal.",
                    ["quit", "exit"], "quit|exit", self.quit),
        ]

    def searchCommand(self, commandWithArgs: str) -> (Command, str):
        commandWithArgsList = split_input(commandWithArgs, " ")

        if len(commandWithArgsList) == 0:
            return None, ""
        else:
            commandFound = None
            commandLabel = commandWithArgsList[0]
            args = " ".join(commandWithArgsList[1:])

            for command in self.commands:
                if commandLabel in command.labels:
                    commandFound = command
                    break
            return commandFound, args

    def launch(self):
        prt("[ ------ OWLL Terminal ------ ]\n")
        prt("Enter your command (type \"help\" to display list of available commands):")
        while not self.leaving:
            userInput = input("> ")
            userInput = userInput.lower()
            userInputList = userInput.split(";")
            userInputList = [string.strip() for string in userInputList if string.strip() != ""]

            i = 1
            for commandWithArgs in userInputList:
                command, args = self.searchCommand(commandWithArgs)
                if command is not None:
                    command.call(args)
                    prt("Command \"%s\" finished (%d/%d)." % (commandWithArgs, i, len(userInputList)))
                else:
                    prt("Unknown command \"%s\" (%d/%d)." % (commandWithArgs, i, len(userInputList)))
                i += 1

    def help(self, args: str):
        argsSp = args.split()
        if len(argsSp) == 0:
            prt("List of available commands: ")
            for command in self.commands:
                prt("  %-20s : %s" % (command.usage, command.description))
            prt("- You can also use \";\" as a separator to run a sequence of commands.")
            prt("- Paths in command arguments cannot contains any spaces.")
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

    def quit(self, _: str):
        self.leaving = True


def main():
    terminal = Terminal()
    terminal.launch()


if __name__ == "__main__":
    main()
