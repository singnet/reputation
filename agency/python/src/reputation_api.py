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

# Reputation Service API, including Rating Service and Ranking Service

import abc

#TODO @anton provide proper parameters for the methods

"""
Reputation Rating Service interface definition
"""        
class RatingService(abc.ABC):

	"""
	List of dicts with the key-value pairs for the attributes: "from","type","to","value","weight","time"
	"""
	@abc.abstractmethod
	def put_ratings(self,ratings):
		pass
        
	@abc.abstractmethod
	def get_ratings(self):
		pass

	@abc.abstractmethod
	def clear_ratings(self):
		pass

"""
Reputation Ranking Service interface definition
"""        
class RankingService(abc.ABC):
	@abc.abstractmethod
	def update_ranks(self):
		pass

	@abc.abstractmethod
	def put_ranks(self,ranks):
		pass

	@abc.abstractmethod
	def get_ranks(self):
		pass

	@abc.abstractmethod
	def clear_ranks(self):
		pass


#TODO @neic take this out to separate file and implement

"""
Reputation Service native implementation in Python
"""        
class PythonReputationService(RatingService,RankingService):

	def clear_ratings(self):
		return("clear_ratings")

	def put_ratings(self):
		return("put_ratings")

	def get_ratings(self):
		return("get_ratings")

	def clear_ranks(self):
		return("clear_ranks")

	def put_ranks(self):
		return("put_ranks")

	def get_ranks(self):
		return("get_ranks")

	def update_ranks(self):
		return("update_ranks")

