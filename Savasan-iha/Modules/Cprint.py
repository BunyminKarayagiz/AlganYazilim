from termcolor import cprint

class cp:
    def __init__(self) -> None:
        pass

    @staticmethod
    def cp(message):
        cprint(message,attrs=("bold",))

    @staticmethod
    def ok(message):
        cprint(message,"light_cyan",attrs=("bold",))

    @staticmethod
    def info(message):
        cprint(message,"light_green",attrs=("bold",))

    @staticmethod
    def warn(message):
        cprint(message,"light_yellow",attrs=("bold",))

    @staticmethod
    def err(message):
        cprint(message,"light_red",attrs=("bold",))

    @staticmethod
    def fatal(message):
        cprint(message,"light_red",attrs=("reverse","bold"))

if __name__ == "__main__":
    print("default")
    cp.cp("cp-default")
    cp.ok("ok")
    cp.info("info")
    cp.warn("warn")
    cp.err("err")
    cp.fatal("fatal")