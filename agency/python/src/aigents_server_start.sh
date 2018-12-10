# Pre-requisite:
# 1. Make sure the folder ../../bin contains Aigents.jar archive
# 2. Make sure the folder ../../bin contains the following  files (see details at https://github.com/aigents/aigents-java/blob/master/README.md):
# 2.1. mail.jar
# 2.2. javax.json-1.0.2.jar
# 3. Serve Web server at domain localtest.com:
# 3.1. Edit hosts file, adding the line with "127.0.0.1 localtest.com"
# Mac: /private/etc/hosts
# Linux: /etc/hosts
# Windows: c:\WINDOWS\system32\drivers\etc\hosts 

# Cleanup data
rm -rf ./al_test.txt *log.txt www is-instances is-text test*.txt

# Run Aigents
java -cp ../../bin/mail.jar:../../bin/javax.json-1.0.2.jar:../../bin/Aigents.jar net.webstructor.agent.Farm store path './al_test.txt', http port 1180, cookie domain localtest.com, console off &
sleep 5
echo Aigents server started.
