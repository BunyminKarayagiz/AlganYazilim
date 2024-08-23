#!/bin/sh

echo "ScriptRunner: number of seconds to wait before execution? "
read time_var
echo -e "ScriptRunner: $time_var seconds selected. \n"

function run_python() {
	python  Iha_haberlesme.py
}


#check if pid exists;
function pid_check() {

run_python
py_pid=${!}
sleep 0.5

while :
do
 if kill -0 "$py_pid" &> /dev/null
  then
   echo "ScriptRunner: $py_pid exists"
  else
   echo "ScriptRunner: $py_pid does'nt exist---Restarting..."
   run_python &
   py_pid=${!}
   echo -e "ScriptRunner: new_pid is : ${!} \n"
  fi

 sleep $time_var
done

}

#MAIN CODE
pid_check
