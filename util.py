import json
import ast
import re
import collections

'''TODO: compare_dictionaries & intOutString can be written in one function'''


def compare_dictionaries(oriDict, compDict, oriDict_name='d1', compDict_name='d2', path=""):
	"""Compare two dictionaries recursively to find non mathcing elements

	Args:
		oriDict(dict): original dictionary
		compDict(dict): dictionary to compare

	Returns:
		string: output string describing the different elements and its path in dictionary
	"""
	err = ''
	key_err = ''
	value_err = ''
	old_path = path
	for k in oriDict.keys():
		path = old_path + "(%s)" % k
		if not k in compDict:
			key_err += "+%s%s(%s) not in %s\n" % (oriDict_name, path, oriDict[k], compDict_name)
		else:
			if isinstance(oriDict[k], dict) and isinstance(compDict[k], dict):
				err += compare_dictionaries(oriDict[k],compDict[k],'d1','d2', path)
			else:
				if oriDict[k] != compDict[k]:
					value_err += "!%s%s(%s) not same as %s%s(%s)\n"\
						% (oriDict_name, path, oriDict[k], compDict_name, path, compDict[k])

	for k in compDict.keys():
		path = old_path + "(%s)" % k
		if not k in oriDict:
			key_err += "+%s%s(%s) not in %s\n" % (compDict_name, path, compDict[k], oriDict_name)

	return key_err + value_err + err


def intOutString(output):
	"""interpret the output string from compare dictionaries

	Args:
		output(string): string returned from compare_dictionaries

	Returns:
		masterList(list): interpreted output list of all differences
		
		example output:
			[['+', 'objectSet', 'defaultObjectSet', {u'aiOverride': True}]...]
			first element: '+' unique to compDict, '-' unique to oriDict, '!' change between dicts
			second element: node type that has difference
			third element: node object that has difference
			fourth element: object attribute and value that has difference
	"""
	masterList = []

	for line in output.split('\n')[:-1]:
		outputList = []  # reset output List
		filter = re.findall("\((.*?)\)", line)

		if line[0] == '!':  # value different
			try:
				outputList = ['!', str(filter[1]), str(filter[2]), {str(filter[3]): [str(filter[4]), str(filter[-1])]}]
			except:
				continue

		elif line[0] == '+':  # anything unique
			if line[2] == '1': outputList.append('-')
			elif line[2] == '2': outputList.append('+')

			if len(filter) == 3:  # missing node
				outputList.append(str(filter[1]))
				noriDictesDict = ast.literal_eval(filter[-1])
				for k, v in noriDictesDict.items():
					outputList.append(str(k))
					outputList.append(v)
			elif len(filter) == 4:  # missing object
				outputList.extend((str(filter[1]), str(filter[2])))
				attrDict = ast.literal_eval(filter[-1])
				outputList.append(attrDict)
			elif len(filter) == 5:  # missing attribute
				outputList.extend((str(filter[1]), str(filter[2])))
				outputList.append({filter[-2]: str(filter[-1])})
			else:
				print(len(filter))
				print(line)  # throw out entire line
				
		masterList.append(outputList)
	return masterList


def sortDict(oriDict):
	"""This is a function to sort a nested dictionary
	
	Args:
		oriDict(dict): original dictionary

	Returns:
		sortedDict(dict): sorted dictionary
	"""
	sortedDict = collections.OrderedDict()
	for k, v in sorted(oriDict.items()):
		if isinstance(v, dict):
			sortedDict[k] = sortDict(v)
		else:
			sortedDict[k] = v
	return sortedDict


def uniqueList(oriList):
	"""This is a function to make a list with no duplicate elements
	
	Args:
		oriList(list): original list

	Returns:
		uniqueList(list): unique list with no duplicate elements
	"""
	uniqueList = []
	for x in oriList: 
		if x not in uniqueList: 
			uniqueList.append(x) 
	return uniqueList





