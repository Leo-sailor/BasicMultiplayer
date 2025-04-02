import datetime
from datetime import timedelta
from typing import Any, Literal
import inspect

trace = True
level_codes = ["debug","info","warning","error","critical"]
class _Logger:
    def __init__(self,file_loc:str = None):
        if file_loc is None:
            file_loc = "logs/"
        if not file_loc.endswith("/"):
            file_loc = file_loc + "/"
        date = datetime.datetime.now()
        date_str = date.isoformat().split(".")[0].replace(":","-")
        file_loc = file_loc + date_str
        with open(file_loc,"x") as f:
            f.write("time,level,file,line,message,data,traceback(optional)")
        self.queue = []
        self.preserve_open = open
        self.last_time = date
        self.file = file_loc
    def log(self,level:Literal[0,1,2,3,4,"debug","info","warning","error","critical"],message:str,data: Any,traceback:bool = None):
        if isinstance(level,int):
            if 0<=level<=4:
                level_name = level_codes[level]
            else:
                raise ValueError("Level number is not in range 0->4")
        elif isinstance(level,str) and level.lower() in level_codes:
            level_name = level
        else:
            raise ValueError("Level is not in a recognisable format")
        if not hasattr(data,"__str__"):
            raise TypeError("Data submitted to logger does not support text conversion")
        if traceback is None:
            traceback = trace
        message.replace(",",";")
        data_str = str(data).replace(",",";")
        line = "unknown"
        file = "unknown"
        if traceback:
            stack = []
            for n,caller_frame_record in enumerate(inspect.stack()):
                frame = caller_frame_record[0]
                info = inspect.getframeinfo(frame)
                file = info.filename
                if n == 1:
                    line = info.lineno
                    file = file
                stack.append('[{}:{} {}()]'.format(file, info.lineno, info.function))
            stack = ";".join(stack)
        else:
            stack = "Traceback Disabled"
            caller_frame = inspect.stack()[1][0]
            info = inspect.getframeinfo(caller_frame)
            line = info.lineno
            file = info.filename
        self.queue.append([datetime.datetime.now().isoformat(),level_name,file,line,message,data_str,stack])
        self.check_queue()
    def check_queue(self):
        now = datetime.datetime.now()
        if now-self.last_time > timedelta(minutes=3) or len(self.queue)>1000:
            self.flush()
        self.last_time = now
    def flush(self):
        lines = ["\n"+(','.join(row)) for row in self.queue]
        self.queue = []
        with self.preserve_open(self.file, "a") as f:
            f.writelines(lines)
    def __del__(self):
        self.flush()
log = _Logger()