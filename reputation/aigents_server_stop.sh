# Kill all hanging Aigents processes by port number
kill -9 $(ps -A -o pid,args | grep java | grep 'net.webstructor.agent.Farm' | grep 1180 | awk '{print $1}')

# Cleanup data
rm -rf ./al_test.txt *log.txt www is-instances is-text test*.txt


