# MIT License
# 
# Copyright (c) 2018-2019 Stichting SingularityNET
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
Reputation Generic Service interface definition
"""        
class ReputationService(abc.ABC):

	"""
	Input: dict of all parameters that needs to be set (not listed parameters are not affected)
	Output: 0 on success, integer error code on error 
	"""
	@abc.abstractmethod
	def set_parameters(self,parameters):
		pass

	@abc.abstractmethod
	def get_parameters(self):
		pass


"""
Reputation Rating Service interface definition
"""        
class RatingService(ReputationService):

	"""
	Input: List of dicts with the key-value pairs for the attributes: "from","type","to","value","weight","time"
	Output: 0 on success, integer error code on error 
	"""
	@abc.abstractmethod
	def put_ratings(self,ratings):
		pass

	"""
	Input: filter as dict of the following:
		since - starting time inclusively
		until - ending time inclusively
		ids - list of ids to retrieve incoming AND outgoing ratings BOTH
		from - list of ids to retrieve outgoing ratings ONLY (TODO later)
		to - list of ids to retrieve incoming ratings ONLY (TODO later)
	Output: tuple of the pair:
		0 on success, integer error code on error
		List of dicts with the key-value pairs for the attributes: "from","type","to","value","weight","time"
	"""
	@abc.abstractmethod
	def get_ratings(self,filter):
		pass

	"""
	Input: None
	Output: 0 on success, integer error code on error 
	"""
	@abc.abstractmethod
	def clear_ratings(self):
		pass
		
"""
Reputation Ranking Service interface definition
"""        
class RankingService(ReputationService):

	"""
	Input: Date to update the ranks for
	Output: 0 on success, integer error code on error 
	"""
	@abc.abstractmethod
	def update_ranks(self,date):
		pass

	"""
	Input: Date and list of dicts with two key-value pairs for "id" and "rank" 
	Output: 0 on success, integer error code on error 
	"""
	@abc.abstractmethod
	def put_ranks(self,date,ranks):
		pass

	"""
	Input: filter as dict of the following:
		date - date to provide the ranks
		ids - list of ids to retrieve the ranks
	Output: tuple of the pair:
		0 on success, integer error code on error
		List of dicts with the two key-value pairs for "id" and "rank"
	"""
	@abc.abstractmethod
	def get_ranks(self,filter):
		pass

	"""
	Input: None
	Output: 0 on success, integer error code on error 
	"""
	@abc.abstractmethod
	def clear_ranks(self):
		pass

	@abc.abstractmethod
	def get_ranks_dict(self,filter):
		pass
