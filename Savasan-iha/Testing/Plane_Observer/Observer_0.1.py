import time
from typing import List
import threading

class pipe:

    def __init__(self,name="Unnamed") -> None:
        self.pipeName = name
        
    def launch():        
        pass
    
    def send():
        pass
    
    def receive():
        pass

class _Observer:
    def __init__(self,pipes) -> None:
        pass
    
    def pipe_error_handler():
        pass
    
    def pipe_manager():
        pass
    
    def pipe_intersection():
        pass
    
    def main_loop():
        pass

def init_pipes(pipes):
    pipe_thread = []
    status = False
    for pipe in pipes:
        thread = threading.Thread(target=pipe.launch)
        pipe_thread.append(thread)
        thread.start()
        
    return pipes_list

if __name__ == "__main__":
    
    kalman_pipe=pipe(name="Kalman")
    Yonelim_pipe=pipe(name="Yonelim")
    Hss_pipe=pipe(name="HSS")
    
    pipes = [Yonelim_pipe,kalman_pipe,Hss_pipe]
    
    pipes_list=init_pipes(pipes=pipes)
    
    Observer = _Observer(pipes= pipes_list)