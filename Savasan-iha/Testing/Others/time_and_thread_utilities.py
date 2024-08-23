import threading
import time

class time_manager:
    
    def __init__(self) -> None:
        pass

    def repeat_on_seconds(self, func_to_run, interval_second,*args ,infinite_loop:bool=True, run_then_wait:bool=True , number_of_loops=1, **kwargs):
        """
        func_to_run : "()" olmadan çalıştırılacak fonksiyon \n
        interval_second : Tekrar edilecek süre(saniye cinsinden) \n

        infinite loop : Sonsuz döngü yerine belirli sayıda döngü için False yapın.(Default=True) \n
        number_of_loops : Sonsuz döngü False yapıldıktan sonra istenen döngü sayısı. \n

        *args : Fonksiyona verilecek argümanlar \n
        **kwargs: Fonksiyona verilecek keyword argümanlar

        """

        while True:
            
            next_time_run = time.time() + interval_second

            if (self.run_then_wait) == True:
                func_to_run(*args,**kwargs)
                
            while time.time() < next_time_run:
                #looping for n seconds
                pass

            if (self.run_then_wait) == False :
                func_to_run(*args,**kwargs)
            
            if infinite_loop == False:
                break

    def run_func_on_thread(self,func, *args, set_daemon=False, **kwargs):
        """
        func = Çalıştırılacak fonksiyon \n
        *args = Çalıştırılacak fonksiyona verilecek argümanlar \n
        set_daemon = Thread tipi değiştirmek için \n
        *kwargs = Çalıştırılacak fonksiyona verilecek keyword argümanlar

        """

        thread = threading.Thread(target=func,args=(*args,),kwargs={**kwargs,} )

        if set_daemon == True:
            thread.setDaemon(True)

        thread.start()

    

#Kilitlenme için 4 saniyelik süre denemesi
def lock_on_enemy(enemy_seen:bool = False):
   print("enemy_status : ",enemy_seen)
   return enemy_seen


if __name__ == "__main__":
    manager = time_manager()

    manager.run_func_on_thread(manager.repeat_on_seconds,lock_on_enemy,1,True)
    manager.run_func_on_thread(manager.repeat_on_seconds,lock_on_enemy,3)
