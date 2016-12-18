import re

# f=open('temp.res') #+47
# f=open('temp2.res')
f=open('temp3.res')
lines=f.readlines()
f.close()

f=open('PyLuaTblParser.py')
tlines=f.readlines()
f.close()
ss=''
pattern=re.compile('\d+')
for l in lines:
    if l.find("PyLuaTblParser")>-1:
        lno= int(re.findall(pattern,l)[0])
        if lno > 375:
            ss+=tlines[lno + 7].split('\'')[1]
            # print tlines[lno +7]
            # ss+=tlines[lno - 2].split('\'')[1]
            # ss+=str(tlines[lno-2][-4])
print ss
