from PyLuaTblParser import PyLuaTblParser

a1 = PyLuaTblParser()
a2 = PyLuaTblParser()
a3 = PyLuaTblParser()

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
["\"\b\f\n\r\t`1~!@#$%^&*()_+-=[]{}|;:\',./<>?"]
= "A key can be any string"
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