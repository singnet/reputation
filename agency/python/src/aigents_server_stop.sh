kill -9 $(ps -A -o pid,args | grep java | grep 'net.webstructor.agent.Farm' | awk '{print $1}')
