import logging
logging.basicConfig(level=logging.INFO)

def lprint(msg, level="error"):
    if level == "warning":
        logging.warning(str(msg))
    elif level == "error":
        logging.error(str(msg))
    else:
        logging.info(str(msg))

COUNTER=0
class LPrint:
    def __init__(self, name:str="", level="error"):
        global COUNTER
        COUNTER += 1
        self.counter = COUNTER
        self.level = level
        self.name = name

    def __enter__(self):
        lprint(f"{self.counter}. starting {self.name} ...", level=self.level)
        return self  # You can return an object to be used within the 'with' block

    def __exit__(self, exc_type, exc_value, traceback):
        lprint(f"{self.counter}. end {self.name}.", level=self.level)

    def log(self, msg, level=""):
        lprint(msg, level=self.level)


if __name__ == "__main__":
    with LPrint("Setup") as p:
        x=1
        y=x**2
        p.log("peter")

    with LPrint("Last step") as p:
        x=1
        y=x**2
        print(x,y)
