from lucs_tools.util.command_line import *

class ez_parser:
    def __init__(self, description="default parser", default_args = [("samples", int, "s", 10000), ("benchmark", str, "b", "sm")]):
        self.parser = argparse.ArgumentParser(description=description)
        self.shortnames = set()
        self.names = set()
        self.DEFAULT_ARGS = default_args

    def add(
        self, name, argtype=str, shortname=None, default=None, help=None, action="store"
    ):

        if shortname is None:
            shortname = ""
            for word in name.split("_"):
                shortname += word[0]

        i = 0
        newname = shortname
        while newname in self.shortnames:
            newname = "{}{}".format(shortname, i)
            i += 1
        shortname = newname
        i = 0
        newname = name
        while newname in self.names:
            newname = "{}{}".format(name, i)
            i += 1
        name = newname

        self.shortnames.add(shortname)
        self.names.add(name)

        self.parser.add_argument(
            "-" + shortname,
            "--" + name,
            action=action,
            dest=name,
            default=default,
            type=argtype,
            help=help,
        )

    def setup_default(self):
        for arg in self.DEFAULT_ARGS:
            self.add(*arg)

    def parse(self, args=None):
        if args is None:
            args = sys.argv[1:]
        return self.parser.parse_args(args)

    def info(self):
        return self.parser.print_help()
