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
    ori_str=""""""
    cur_valid=""

    def __init__(self):
        self.dict = {}

    def load(self, s):
        brackets_stack = []
        brackets = []
        ori_str=str(s)
        # get all valid brackets
        quotation_stack_1 = []
        quotation_stack_2 = []
        for i in xrange(0, len(s)):
            if s[i] == '{' and len(quotation_stack_1) == 0 and len(quotation_stack_2) == 0:
                brackets_stack.append(i)
            elif s[i] == '}' and len(quotation_stack_1) == 0 and len(quotation_stack_2) == 0:
                brackets.append((brackets_stack[-1], i))
                brackets_stack.pop()
            elif s[i] == '\'':
                if len(quotation_stack_1) == 1:
                    quotation_stack_1.pop()
                else:
                    quotation_stack_1.append(i)
            elif s[i] == '\"':
                if len(quotation_stack_2) == 1:
                    quotation_stack_2.pop()
                else:
                    quotation_stack_2.append(i)
        if len(brackets_stack):
            raise Exception('lua table string format Error on {}')

        # iterate brackets
        cur_res = {}
        for i in xrange(0, len(brackets)):
            cur_bracket = brackets[i]
            # reverse scan for smaller pre bracket: get the first sub bracket of current bracket
            j = i - 1
            while j > -1:
                if brackets[j][0] < brackets[i][0]:
                    break
                j -= 1
            j += 1
            # load bracket keys
            pj_keys = []
            while j != i:
                pj_keys.append(brackets[j][0])
                j += 1
            # deal with current bracket
            is_list = True
            content = s[cur_bracket[0] + 1:cur_bracket[1]]  # get content
            ls = self.mySplit(content)  # split with separator
            for l in ls:
                if l.find('=') > -1:
                    is_list = False
            if is_list:
                rls = []
                pj_i = 0
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
                            if ls.index(l)!=len(ls)-1:
                                raise Exception('empty value after split')
                            continue
                        elif len(l) > 1 and l[0] == '{' and l[-1] == '}':
                            rls.append(cur_res[pj_keys[pj_i]])
                            del cur_res[pj_keys[pj_i]]
                            pj_i += 1
                        elif self.validStr(l):
                            rls.append(l[1:-1])
                        else:
                            rls.append(eval(l))
            else:
                # dict
                rls = {}
                pj_i = 0
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
                            index += 1
                            continue
                        elif len(lk[1]) > 1 and lk[1][0] == '{' and lk[1][-1] == '}':
                            rls[lk[0]] = cur_res[pj_keys[pj_i]]
                            del cur_res[pj_keys[pj_i]]
                            pj_i += 1
                        else:
                            if self.validStr(lk[1]):
                                rls[lk[0]] = lk[1][1:-1].strip()
                            else:
                                rls[lk[0]] = eval(lk[1])
            cur_res[cur_bracket[0]] = rls
            # replace separators
            s=s[:cur_bracket[0]]+s[cur_bracket[0]:cur_bracket[1]].replace(',','_').replace(';','_')+s[cur_bracket[1]:]

        for key in cur_res:
            self.dict = cur_res[key]
        return

    def dump(self):
        return str(self.dict)

    def loadLuaTable(self, f):
        self.load(open(f).read())

    def dumpLuaTable(self, f):
        fw=open(f,'w')
        # self.dict

    def loadDict(self, d):
        self.dict = eval(d)
        pass

    def dumpDict(self):
        return eval(str(self.dict))

    # my functions
    def mySplit(self, s):
        # scan for quotations
        quotation_1 = []
        quotation_2 = []
        quotation_stack_1 = []
        quotation_stack_2 = []
        for i in xrange(0, len(s)):
            if s[i] == '\"':
                if len(quotation_stack_2) == 1:
                    quotation_2.append((quotation_stack_2[-1], i))
                    quotation_stack_2.pop()
                else:
                    quotation_stack_2.append(i)
            elif s[i] == '\'':
                if len(quotation_stack_1) == 1:
                    quotation_1.append((quotation_stack_1[-1], i))
                    quotation_stack_1.pop()
                else:
                    quotation_stack_1.append(i)
        if len(quotation_stack_1) or len(quotation_stack_2):
            raise Exception('lua table string format Error on ""')
        xstr = s
        for p in quotation_1:
            xstr = xstr[:p[0]] + xstr[p[0]:p[1] + 1].replace(',', '_').replace(';', '_') + xstr[p[1] + 1:]
        for p in quotation_2:
            xstr = xstr[:p[0]] + xstr[p[0]:p[1] + 1].replace(',', '_').replace(';', '_') + xstr[p[1] + 1:]
        xstr = xstr.replace(';', ',')
        return xstr.split(',')

    def validStr(self, s):
        if len(s) < 2:
            return False
        s=s.strip()
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
        if s[0] == '[' and s[-1] == ']':
            in_str=s[1:-1].strip()
            if in_str.find(']') > -1 or in_str.find('[')>-1:
                return False
            else:
                return True
        return True
        # if len(s) < 2:
        # return False
        # if(s[0]=='\"' and s[-1] == '\"'):
        # if s[1:-1].find('\"') > -1:
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
