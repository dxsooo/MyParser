from PyLuaTblParser import PyLuaTblParser

# a1 = PyLuaTblParser()
# a2 = PyLuaTblParser()
# a3 = PyLuaTblParser()
#
# test_str = '{array = {65,23,5,},dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},}'
# a1.load(test_str)
# d1 = a1.dumpDict()
#
# a2.loadDict(d1)
# file_path='lua.tbl'
#
# a2.dumpLuaTable(file_path)
# a3.loadLuaTable(file_path)
#
# d3 = a3.dumpDict()
# # aa={1:2,"3":6}
# # print type(aa)
# a1 = PyLuaTblParser()
# # test_str = '{array = {65,23,5,},dict = {7,8,false,string="value"},}'
# # test_str = """{a={132,123},b={456}}"""
# test_str = """{x={132,123},456,nil,True,"1321"}"""
# a1.load(test_str)
# # a1.loadLuaTable('lua.tbl')
# d1 = a1.dumpDict()
# # dd={1:2,2:3,'123':456}
# # a1.loadDict(d1)
# print d1

a1 = PyLuaTblParser()
test_str = """  {  array    = {  65,23,5,  },  di  ct = {7,8,false,string="va ='lue"}   ,}   """
a1.load(test_str)
d1 = a1.dumpDict()
print d1
# a1.removeSpace(test_str)
# print a1.cur_valid
# a='123'
# b=a
# a='456'
# print b