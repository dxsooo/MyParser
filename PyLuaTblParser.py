# -*- coding:utf-8 -*-

class PyLuaTblParser():
    '''
1. load(self, s)    读取Lua table数据，输入s为一个符合Lua table定义的字符串，无返回值；若遇到Lua table格式错误抛出异常；
2. dump(self)  根据类中数据返回Lua table字符串
3. loadLuaTable(self, f)  从文件中读取Lua table字符串，f为文件路径，异常处理同1，文件操作失败抛出异常；
4. dumpLuaTable(self, f) 将类中的内容以Lua table格式存入文件，f为文件路径，文件若存在则覆盖，文件操作失败抛出异常；
5. loadDict(self, d)   读取dict中的数据，存入类中，只处理数字和字符串两种类型的key，其他类型的key直接忽略；
6. dumpDict(self)  返回一个dict，包含类中的数据
    '''
    dict = {}
    brackets = []
    brackets_stack = []

    def __init__(self):
        self.brackets = []
        self.brackets_stack = []
        self.dict = {}

    def load(self, s):
        # brackets
        for i in xrange(0, len(s)):
            if (s[i] == '{'):
                self.brackets_stack.append(i)
            elif (s[i] == '}'):
                # self.brackets_stack.pop()
                self.brackets.append((self.brackets_stack[-1], i))
                self.brackets_stack.pop()
        if len(self.brackets_stack):
            raise Exception('lua table string format Error on {}')
        # print self.brackets_info
        cur_res={}
        for i in xrange(0, len(self.brackets)):
            # cur_res = {}
            bracket = self.brackets[i]
            j = i - 1
            while j > -1:
                if self.brackets[j][0] < self.brackets[i][0]:
                    break
                j -= 1
            j += 1
            if j != i:
                pass
                # for bracket in self.brackets:
            is_list = True
            str = s[bracket[0] + 1:bracket[1]]
            ls = str.split(',')
            for l in ls:
                if l.find('=') > -1:
                    is_list = False
            if is_list:
                rls = []
                for l in ls:
                    if l == 'true':
                        b = True
                        rls.append(b)
                    elif l == 'false':
                        b = False
                        rls.append(b)
                    elif l == 'nil':
                        b = None
                        rls.append(b)
                    else:
                        if l == '':
                            continue
                        elif self.validStr(l):
                            rls.append(l[1:-1])
                        # elif l[0]=='\"' and l[-1]=='\"':
                        #     ts=l[1:-1]
                        #     if ts.find('\"')>-1:
                        #         raise Exception('lua table string format Error on string')
                        #     rls.append(ts)
                        # elif l[0]=='\'' and l[-1]=='\'':
                        #     ts = l[1:-1]
                        #     if ts.find('\'') > -1:
                        #         raise Exception('lua table string format Error on string')
                        #     rls.append(ts)
                        else:
                            # print len(l)
                            # print l[1:-1]
                            rls.append(eval(l))
                            # raise Exception('lua table string format Error on string')
            else:
                # dict
                rls = {}
                index = 1
                for l in ls:
                    if l.find('=') == -1:
                        if l == 'true':
                            b = True
                            rls[index] = b
                        elif l == 'false':
                            b = False
                            rls[index] = b
                        elif l == 'nil':
                            continue
                        else:
                            if l == '':
                                continue
                            elif self.validStr(l):
                                rls[index] = l[1:-1]
                            else:
                                rls[index] = eval(l)
                        index += 1
                    else:
                        lk = l.split('=')
                        assert len(lk) == 2
                        assert self.validKey(lk[0])
                        if lk[1] == 'true':
                            b = True
                            rls[lk[0]] = b
                        elif lk[1] == 'false':
                            b = False
                            rls[lk[0]] = b
                        elif lk[1] == 'nil':
                            continue
                        else:
                            if self.validStr(lk[1]):
                                rls[lk[0]] = lk[1][1:-1]
                            else:
                                rls[lk[0]] = eval(lk[1])
                    # index += 1
            cur_res[bracket[0]] = rls

        # if len(cur_res) == 1:
        for key in cur_res:
            self.dict = cur_res[key]
        return

    def dump(self):
        return self.dict

    def loadLuaTable(self, f):
        self.load(open(f).read())
        pass

    def dumpLuaTable(self, f):
        return self.dict

    def loadDict(self, d):
        self.dict = d
        pass

    def dumpDict(self):
        return self.dict

    def validStr(self, s):
        if len(s) < 2:
            return False
        if s[0] == '\"' and s[-1] == '\"':
            if s[1:-1].find('\"') > -1:
                return False
            else:
                return True
        elif s[0] == '\'' and s[-1] != '\'':
            if s[1:-1].find('\'') > -1:
                return False
            else:
                return True
        else:
            return False

    def validKey(self, s):
        return True
        # if len(s) < 2:
        #     return False
        # if(s[0]=='\"' and s[-1] == '\"'):
        #     if s[1:-1].find('\"') > -1:
        #         return False
        #     else:
        #         return True
        # elif(s[0]=='\'' and  s[-1]!='\'' ):
        #     if s[1:-1].find('\'') > -1:
        #         return False
        #     else:
        #         return True
        # else:
        #     return False
