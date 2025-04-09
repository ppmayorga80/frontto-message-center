from dataclasses import asdict, dataclass
import os
import smart_open

from jsonl import Jsonl
from utils import curdt

LLM_PROMPT_PATH = os.environ.get("LLM_PROMPT_PATH", "")
MESSAGES_PATH_FMT = os.environ.get("MESSAGES_PATH_FMT","")

@dataclass
class History:
    phone: str
    message: str
    who: str = ""
    is_prompt: bool = False
    dt: str = ""
    
    def __post_init__(self):
        if not self.dt:
            self.dt = str(curdt())
        if not self.who:
            self.who = "system" if self.is_prompt else "user"
            
    @classmethod
    def read_history_and_update(cls, phone, message)->list['History']:
        path = MESSAGES_PATH_FMT.format(phone=phone)
        try:
            raw_history = Jsonl.read(path=path)
            history = [History(**x) for x in raw_history]
        except Exception:
            #1. read the prompt
            with smart_open.open(LLM_PROMPT_PATH,"r") as fp:
                prompt = fp.read()
            history = [History(phone="NA", is_prompt=True, message=prompt)]

        history.append(History(phone=phone, message=message))

        return history

    @classmethod
    def write_history(cls,phone:str,  history:list['History']):
        path = MESSAGES_PATH_FMT.format(phone=phone)
        raw_history = [asdict(x) for x in history]
        Jsonl.write(path=path, data=raw_history)


    def clean(self):
        pass

    