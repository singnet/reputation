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
# 5. Run this script passing 7 parameters as directory of binary Aigents.jar file, simulation name, data directory, transaction log file, user reputations file, start date and end date. 

import sys
import os
import subprocess

def get_param(args, key, default):
	for s in args:
		if s.count('=') == 1:
			k, v = s.split('=', 1)
			if k == key:
				return v if len(v) > 0 else default
	return default

def get_option(args, key):
	value = get_param(sys.argv,key,'False')
	return True if value == 'True' else False


java_options = '-Xms1000m -Xmx2000m -Dsun.zip.disableMemoryMapping=true'

if len(sys.argv) < 8 or len(sys.argv[1]) < 2 or len(sys.argv[2]) < 2 or len(sys.argv[3]) < 2:
	print('Usage:')
	print('	<command> := python reputation_simulate.py <ordered_parameters> <optional_parameters>')
	print('	<ordered_parameters> := <bin_directory> <simulation_name> <data_directory> <transaction_log_file> <user_reputations_file> <since_date> <until_date>')
	print('	<optional_parameters> := <optional_parameter> (<optional_parameter>)*')
	print('	<optional_parameter> := <decimal_parameter>|<boolean_parameter>')
	print('	<decimal_parameter> := (precision | default | conservatism)=<decimal_value>')
	print('	<boolean_parameter> := (logratings | weighting | fullnorm | verbose)=(True | False)')
	print('Examples:')
	print('	python reputation_simulate.py ./bin testsim ./ transactions10_r_20_0.1.tsv users10.tsv 2018-01-01 2018-01-10')
	print('	python reputation_simulate.py ./bin testsim ./ transactions10_r_20_0.1.tsv users10.tsv 2018-01-01 2018-01-10 weighting=True fullnorm=True logratings=False downrating=False precision=0.01 default=0.5 conservatism=0.5 decayed=0.0')
	sys.exit()


#required ordered parameters
bin_dir = sys.argv[1]
sim_name = sys.argv[2]
data_dir = sys.argv[3]
transactions_file = sys.argv[4]
reputations_file = sys.argv[5]
since_date = sys.argv[6]
until_date = sys.argv[7]
out_dir = data_dir + '/' + sim_name + '_out'
control_id = 0 # id of user to be controlled

#default optional parameters
precision = get_param(sys.argv,'precision','0.01')
default = get_param(sys.argv,'default','0.5')
decayed = get_param(sys.argv,'decayed','0.0')
conservatism = get_param(sys.argv,'conservatism','0.5')
logratings = get_option(sys.argv,'logratings')
weighting = get_option(sys.argv,'weighting')
fullnorm = get_option(sys.argv,'fullnorm')
downrating = get_option(sys.argv,'downrating')
verbose = get_option(sys.argv,'verbose')

print('binary directory:', bin_dir)
print('simulation name:', sim_name)
print('data directory:', data_dir)
print('transaction log file:', transactions_file)
print('user reputations file:', reputations_file)
print('since date:', since_date)
print('until date:', until_date)
print('precision:', precision)
print('default:', default)
print('decayed:', decayed)
print('conservatism:', conservatism)
print('logratings:', logratings)
print('weighting:', weighting)
print('fullnorm:', fullnorm)
print('downrating:', downrating)
print('verbose:', verbose)


def os_command(command):
	#TODO: smarter way to handle that?
	#os.system(command)
	r = subprocess.check_output(command,shell=True) 
	print(r.decode())

def ai_command(command):
	aigents_command = 'java ' + java_options + ' -cp '+ bin_dir + '/Aigents.jar' \
		+ ' net.webstructor.peer.Reputationer' + ' path ' + data_dir + ' network ' \
		+ sim_name + ' ' + command
	if verbose:
		print(aigents_command)
	os_command(aigents_command)

if verbose:
	print('')
	print('Cleaning data.')
ai_command('clear ranks')
ai_command('clear ratings')

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

if not os.path.exists(out_dir):
	print('Creating output directory: ' + out_dir)
	os.makedirs(out_dir)

if verbose:
	print('Loading transaction ratings.')
ai_command('load ratings file ' + transactions_file \
		+ ' precision ' + precision \
		+ ' weighting ' + ('true' if weighting else 'false') \
		+ ' downrating ' + ('true' if downrating else 'false') \
		+ ' logratings ' + ('true' if logratings else 'false'))

if verbose:
	print('Updating reputation ranks.')
ai_command('update ranks since ' + since_date + ' until ' + until_date \
		+ ' precision ' + precision \
		+ ' weighting ' + ('true' if weighting else 'false') \
		+ ' downrating ' + ('true' if downrating else 'false') \
		+ ' logratings ' + ('true' if logratings else 'false') \
		+ ' default ' + default \
		+ ' decayed ' + decayed \
		+ ' conservatism ' + conservatism \
		+ ' fullnorm ' + ('true' if fullnorm else 'false'))

if verbose:
	print('Checking ranks:')
ai_command('get ratings date ' + until_date + ' ids ' + str(control_id))

if verbose:
	print('Getting history of ranks.')
ai_command('get ranks since ' + since_date + ' until ' + until_date + ' > ' + out_dir + '/history.tsv')

if verbose:
	print('Getting average and latest ranks.')
ai_command('get ranks since ' + since_date + ' until ' + until_date + ' average > ' + out_dir + '/average.tsv')
ai_command('get ranks date ' + until_date + ' > ' + out_dir + '/latest.tsv')

if verbose:
	print('Checking top 5 latest ranks:')
	os_command('head -n 5 ' + out_dir + '/latest.tsv')

	print('Checking bottom 10 latest ranks:')
	os_command('tail -n 5 ' + out_dir + '/latest.tsv')

if verbose:
	print('Evaluating average and latest ranks:')
ai_command('compute accuracy file ' + reputations_file + ' file ' + out_dir + '/average.tsv')
#ai_command('compute accuracy file ' + reputations_file + ' file ' + out_dir + '/latest.tsv')
ai_command('compute pearson file ' + reputations_file + ' file ' + out_dir + '/average.tsv')
ai_command('compute pearson file ' + reputations_file + ' file ' + out_dir + '/latest.tsv')
