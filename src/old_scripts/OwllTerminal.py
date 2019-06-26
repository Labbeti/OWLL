from src.old_scripts.owll_clust import clust_op_names
from gen_opd import gen_opd
from gen_stats import gen_stats
from src.old_scripts.owll_typolink import typolink
from src.util import prt
from src.util import split_input


class Command:
    def __init__(self, name, description, labels, usage, fct):
        self.name = name
        self.description = description
        self.labels = labels
        self.usage = usage
        self.fct = fct

    def call(self, args: list):
        code = self.fct(args)
        if code != 0:
            prt("Error: Command %s exited with code %d." % (self.name, code))


class Terminal:
    def __init__(self):
        self.leaving = False
        self.commands = [
            Command("TypoLink", "Basic classification with relational words of \"Typologie des mots de liaisons\".",
                    ["typo", "typolink"], "typo|typolink", typolink),
            Command("Clust", "Test of some clusterisation algorithms on object properties names with FastText.",
                    ["clust"], "clust", clust_op_names),
            Command("Generate OPD", "Regenerate Object Property Database (OPD) with the ontologies found in "
                                    "\"dir_onto\"",
                    ["genopd"], "genopd [onto_dir [opd_filepath]]", gen_opd),
            Command("Get Stats", "Update all statistics from OPD.",
                    ["genstats"], "genstats", gen_stats()),
            Command("Help", "Display list of commands or show description and usage of a specific command.",
                    ["help"], "help [command]", self.help),
            Command("Quit", "Leave the OWLL terminal.",
                    ["quit", "exit"], "quit|exit", self.quit),
        ]

    def searchCommand(self, commandWithArgs: str) -> (Command, list):
        commandWithArgsList = split_input(commandWithArgs)

        if len(commandWithArgsList) == 0:
            return None, ""
        else:
            commandFound = None
            commandLabel = commandWithArgsList[0]
            args = commandWithArgsList[1:]

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

    def help(self, args: list) -> int:
        if len(args) == 0:
            prt("List of available commands: ")
            for command in self.commands:
                prt(" - %-35s : %s" % (command.usage, command.description))
            prt("Additional notes:")
            prt(" - You can also use \";\" as a separator to run a sequence of commands.")
            prt(" - Paths with spaces must be surrounded by double quotes (ex: genopd \"dir with space/tmp.txt\")")
        else:
            commandName = args[0]
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
                return 1
        return 0

    def quit(self, _: list) -> int:
        self.leaving = True
        return 0
