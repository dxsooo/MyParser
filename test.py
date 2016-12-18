from PyLuaTblParser import PyLuaTblParser

a1 = PyLuaTblParser()
a2 = PyLuaTblParser()
a3 = PyLuaTblParser()

# test_str = '{array = {65,23,5,},--dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},\n}'
test_str=r"""
{
root = {
"Test Pattern String",
-- {"object with 1 member" = {"array with 1 element",},},
{["object with 1 member"] = {"array with 1 element",},},
{},
[99] = -42,
[98] = {{}},
[97] = {{},{}},
[96] = {{}, 1, 2, nil},
[95] = {1, 2, {["1"] = 1}},
[94] = { {["1"]=1, ["2"]=2}, {1, ["2"]=2}, ["3"] = 3 },
true,
false,
nil,  {
["integer"]= 1234567890,  --355 363
real=-9876.543210,
e= 0.123456789e-12,
E= 1.234567890E+34,
zero = 0,
one = 1,
space = " ",
quote = "\"",
backslash = "\\",  --499 502
controls = "\b\f\n\r\t",  --520 540
slash = "/ & \\",
alpha= "abcdefghijklmnopqrstuvwyz",
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWYZ",
digit = "0123456789",
special = "`1~!@#$%^&*()_+-={\':[,]}|;.</>?",
hex = "0x01230x45670x89AB0xCDEF0xabcd0xef4A",
["true"] = true,
["false"] = false,
["nil"] = nil,
array = {nil, nil,},
object = {  },
address = "50 St. James Street",
url = "http://www.JSON.org/",
comment = "// /* <!-- --",
["# -- --> */"] = "",
[" s p a c e d " ] = {1,2 , 3,
4 , 5        ,          6           ,7        },
0.5 ,31415926535897932384626433832795028841971693993751058209749445923.
,
1066,"rosebud"
}
}
}"""
a1.load(test_str)
d1 = a1.dumpDict()
file_path='lua.tbl'
print d1
a2.loadDict(d1)
a2.dumpLuaTable(file_path)
a3.loadLuaTable(file_path)

d3 = a3.dumpDict()
print d3

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

# a1 = PyLuaTblParser()
# test_str = """{array = {65,23,5,},dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},}"""
# # test_str = """  {  {  65,23,5,  },   {7,8,false,"va ='lue"}   ,}   """
# a1.load(test_str)
# d1 = a1.dumpDict()
# print d1
# a1.removeSpace(test_str)
# print a1.cur_valid
# a='123'
# b=a
# a='456'
# print b