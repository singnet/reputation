import sys
import os
import subprocess
import json
from collections import OrderedDict


class Aigents():
    def __init__(self, study_path='study.json', opened_config= False):

        if opened_config:
            config = study_path
        else:
            with open(study_path) as json_file:
                config = json.load(json_file, object_pairs_hook=OrderedDict)

        self.runs = config['batch']['reputation_runs']
        self.output_path = config['parameters']['output_path']
        self.param_str = config['parameters']['param_str']
        self.java_options = '-Xms128m -Xmx256m -Dsun.zip.disableMemoryMapping=true'
        self.bin_dir = "bin"

        # MIT License
        #
        # Copyright (c) 2018 SingularityNET
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
        # 1. Create some home directory and go to that directory.
        # 2. Download Aigents.jar to that directory using either wget or curl:
        # 2.a. wget http://aigents.com/download/latest/Aigents.jar
        # 2.b. curl http://aigents.com/download/latest/Aigents.jar -o ./Aigents.jar
        # 3. Select some simulation name (to identify data set).
        # 4. Get transaction log file and expected user reputations file.
        # 5. Run this script passing 4 parameters as simulation name, home directory, transaction log file and user reputations file.



    def os_command(self,command):
        # TODO: smarter way to handle that?
        # os.system(command)
        r = subprocess.check_output(command, shell=True)
        print(r.decode())

    def ai_command(self,command):
        # aigents_command = 'java ' + java_options + ' -cp ' + bin_dir + '/Aigents.jar' \
        #                       + ' net.webstructor.peer.Reputationer' + ' path ' + data_dir + ' network ' \
        #                       + sim_name + ' ' + command

        aigents_command = 'java ' + self.java_options + ' -cp ' + self.bin_dir + '/Aigents.jar' \
                          + ' net.webstructor.peer.Reputationer' + ' path ' + self.data_dir + ' network ' \
                          + self.sim_name + ' ' + command



        print(aigents_command)
        #print (os.getcwd())
        self.os_command(aigents_command)


    def go(self):

        for run in self.runs:
            self.sim_name = self.param_str + run['run_name']
            self.data_dir = self.output_path+self.param_str + run['run_name']
            self.transactions_file = self.output_path + 'transactions_' + self.param_str[:-1] + '.tsv'
            self.reputations_file = self.output_path + 'users_' + self.param_str[:-1] + '.tsv'
            # self.data_dir = '/home/dduong'
            # self.transactions_file = 'transactions_' + self.param_str[:-1] + '.tsv'
            # self.reputations_file = 'users_' + self.param_str[:-1] + '.tsv'
            self.since_date = run['since_date']
            self.until_date = run['until_date']
            self.run()



    def run(self):
        print('')
        print('Cleaning data, but not calling rm -rf, please clear out the file area manually.')
        self.ai_command('clear')
        # os.system('rm -rf ' + data_dir + '/' + sim_name + '*')

        print('Loading transaction ratings.')
        self.ai_command('load ratings file ' + self.transactions_file + ' precision 0.01 logarithm')

        print('Updating reputation ranks.')
        self.ai_command('update ranks since ' + self.since_date + ' until ' + self.until_date + ' default 0.1 conservativity 0.5')

        print('Checking ranks:')
        self.ai_command('get ratings date ' + self.since_date + ' ids 730')

        print('Getting history of ranks.')
        self.ai_command('get ranks since ' + self.since_date + ' until ' +self.until_date + ' > ' + self.data_dir + '/history.tsv')

        print('Getting average ranks.')
        self.ai_command('get ranks since ' + self.since_date + ' until ' + self.until_date + ' average > ' + self.data_dir + '/average.tsv')

        print('Getting latest ranks.')
        self.ai_command('get ranks date ' + self.until_date + ' > ' + self.data_dir + '/latest.tsv')

        # print('Checking top 5 latest ranks:')
        # os_command('head -n 5 ' + data_dir + '/latest.tsv')

        # print('Checking bottom 10 latest ranks:')
        # os_command('tail -n 5 ' + data_dir + '/latest.tsv')

        print('Getting checking ranks.')

        print('Evaluating average ranks:')
        self.ai_command('compute pearson file ' + self.reputations_file + ' file ' + self.data_dir + '/average.tsv')

        print('Evaluating latest ranks:')
        self.ai_command('compute pearson file ' + self.reputations_file + ' file ' + self.data_dir + '/latest.tsv')


def main():
    if len(sys.argv) < 2:
        print(
            'Usage: configfile')
        sys.exit()

    aigent = Aigents(sys.argv[1])
    aigent.go()



if __name__ == '__main__':
    main()
