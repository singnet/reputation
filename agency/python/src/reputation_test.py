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

# Reputation Service API Interation Testing

import unittest

from aigents_reputation_cli import *

class TestStringMethods(unittest.TestCase):

	def setUp(self):
		self.rs = AigentsCLIReputationService('../','./','test',True)

	def test_smoke(self):
		rs = self.rs
		
		#clear everything
		self.assertEqual( rs.clear_ratings(), 0 )
		self.assertEqual( rs.clear_ranks(), 0 )
		
		#add ratings
		self.assertEqual( rs.put_ratings(), 'put_ratings' )
		self.assertEqual( rs.get_ratings(), 'get_ratings' )
		
		#update and get ranks
		self.assertEqual( rs.put_ranks(), 'put_ranks' )
		self.assertEqual( rs.update_ranks(), 'update_ranks' )
		self.assertEqual( rs.get_ranks(), 'get_ranks' )

if __name__ == '__main__':
    unittest.main()

