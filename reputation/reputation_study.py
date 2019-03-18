# MIT License
# 
# Copyright (c) 2018 Stichting SingularityNET
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Simulating reputation computation and assessment with Aigents Reputation CLI API

# Installation and Launch Instructions
# 1. Create some directory for Aigets.jar binary file and go to that directory.
# 2. Download Aigents.jar to that directory using either wget or curl:
# 2.a. wget http://aigents.com/download/latest/Aigents.jar
# 2.b. curl http://aigents.com/download/latest/Aigents.jar -o ./Aigents.jar
# 3. Select some simulation name (to identify data set).
# 4. Get transaction log file and expected user reputations file.
# 5. Run this script passing 7 parameters as directory of binary Aigents.jar file, simulation name, data directory, user reputations file, start date, end date and period for computing reputations. 

import sys
import os
import subprocess

java_options = '-Xms128m -Xmx256m -Dsun.zip.disableMemoryMapping=true'

if len(sys.argv) < 8 or len(sys.argv[1]) < 2 or len(sys.argv[2]) < 2 or len(sys.argv[3]) < 2:
	print('Usage: python reputation_simulate.py <bin_directory> <simulation_name> <data_directory> <user_reputations_file> <since_date> <until_date> <period>')
	sys.exit()

bin_dir = sys.argv[1]
sim_name = sys.argv[2]
data_dir = sys.argv[3]
reputations_file = sys.argv[4]
since_date = sys.argv[5]
until_date = sys.argv[6]
period = int(float(sys.argv[7]))
out_dir = data_dir + '/' + sim_name + '_out'
control_id = 0 # id of user to be controlled

print('')
	
print('Binary directory:', bin_dir)
print('Simulation name:', sim_name)
print('Data directory:', data_dir)
print('Output directory:', out_dir)
print('User reputations file:', reputations_file)
print('Since date:', since_date)
print('Until date:', until_date)
print('Period days:', str(period))


def os_command(command):
	#TODO: smarter way to handle that?
	#os.system(command)
	r = subprocess.check_output(command,shell=True) 
	print(r.decode())

def ai_command(command):
	aigents_command = 'java ' + java_options + ' -cp '+ bin_dir + '/Aigents.jar' \
		+ ' net.webstructor.peer.Reputationer' + ' path ' + data_dir + ' network ' \
		+ sim_name + ' ' + command
	#print(aigents_command)
	os_command(aigents_command)

print('')

if not os.path.exists(data_dir):
	print('Creating data directory: ' + data_dir)
	os.makedirs(data_dir)
        
if not os.path.exists(out_dir):
	print('Creating output directory: ' + out_dir)
	os.makedirs(out_dir)
        
print('Cleaning ranks data.')
ai_command('clear ranks')

print('Updating reputation ranks.')
ai_command('update ranks since ' + since_date + ' until ' + until_date + ' period ' + str(period) + ' default 0.1 conservatism 0.5')

print('Getting average ranks.')
ai_command('get ranks since ' + since_date + ' until ' + until_date + ' period ' + str(period) + ' average > ' + out_dir + '/average.tsv')

print('Getting latest ranks.')
ai_command('get ranks date ' + until_date + ' > ' + out_dir + '/latest.tsv')

print('Checking top 5 latest ranks:')
os_command('head -n 5 ' + out_dir + '/latest.tsv')

print('Checking bottom 10 latest ranks:')
os_command('tail -n 5 ' + out_dir + '/latest.tsv')

print('Getting checking ranks.')

print('Evaluating average ranks:')
ai_command('compute pearson file ' + reputations_file + ' file ' + out_dir + '/average.tsv')

print('Evaluating latest ranks:')
ai_command('compute pearson file ' + reputations_file + ' file ' + out_dir + '/latest.tsv')
