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

    def __init__(self):
        self.dict = {}
        self.quotations = []
        self.cur_valid = ""

    def load(self, s):
        # remove useless spaces
        self.removeSpace(s)
        s = self.cur_valid
        # update quotations
        self.scanQuotations(s)  # update quotations
        # remove sensitive char in quotations
        for pai in self.quotations:
            s = s[:pai[0]] + s[pai[0]:pai[1]].replace(',', '_').replace('=', '_').replace('{', '_').replace('}', '_') \
                + s[pai[1]:]
        # get all valid brackets
        brackets_stack = []
        brackets = []
        i = 0
        while i < len(s):
            if s[i] == '{':
                brackets_stack.append(i)
            elif s[i] == '}':
                brackets.append((brackets_stack[-1], i))
                brackets_stack.pop()
            i += 1
        if len(brackets_stack):
            raise Exception('lua table string format Error on {}')

        # Step 3: iterate brackets
        cur_res = {}
        work_dict = {}
        for i in xrange(0, len(brackets)):
            work_dict[brackets[i][0]] = False
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
                if work_dict[brackets[j][0]] is False:
                    pj_keys.append(brackets[j][0])
                    work_dict[brackets[j][0]] = True
                j += 1
            # deal with current bracket
            is_list = True
            content = s[cur_bracket[0] + 1:cur_bracket[1]]  # get content
            content_quotations = []
            for pp in self.quotations:
                if pp[0] >= cur_bracket[0] and pp[1] < cur_bracket[1]:
                    content_quotations.append(pp)
            self.quotations = list(set(self.quotations) - set(content_quotations))
            quo_index = 0
            ls = content.split(',')  # split with separator
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
                            if ls.index(l) != len(ls) - 1:
                                raise Exception('empty value after split')
                            continue
                        elif len(l) > 1 and l[0] == '{' and l[-1] == '}':
                            rls.append(cur_res[pj_keys[pj_i]])
                            del cur_res[pj_keys[pj_i]]
                            pj_i += 1
                        elif self.validStr(l):
                            ori = self.cur_valid[content_quotations[quo_index][0] + 1:content_quotations[quo_index][1]]
                            rls.append(ori)
                            quo_index += 1
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
                                ori = self.cur_valid[
                                      content_quotations[quo_index][0] + 1:content_quotations[quo_index][1]]
                                rls[index] = ori
                                quo_index += 1
                            else:
                                rls[index] = eval(l)
                        index += 1
                    else:
                        lk = l.split('=')
                        assert len(lk) == 2
                        if len(lk[0]) > 2 and lk[0][0] == '[' and lk[0][-1] == ']':
                            in_str = lk[0][1:-1]
                            if self.validStr(in_str):
                                ori = self.cur_valid[
                                      content_quotations[quo_index][0] + 1:content_quotations[quo_index][1]]
                                cur_key = ori
                                quo_index += 1
                            else:
                                cur_key = eval(in_str)
                        elif lk[0].find(' ') != -1:
                            raise Exception("error key")
                        else:
                            cur_key = lk[0]

                        if lk[1] == 'true':
                            b = True
                            rls[cur_key] = b
                        elif lk[1] == 'false':
                            b = False
                            rls[cur_key] = b
                        elif lk[1] == 'nil':
                            index += 1
                            continue
                        elif len(lk[1]) > 1 and lk[1][0] == '{' and lk[1][-1] == '}':
                            rls[cur_key] = cur_res[pj_keys[pj_i]]
                            del cur_res[pj_keys[pj_i]]
                            pj_i += 1
                        else:
                            if self.validStr(lk[1]):
                                ori = self.cur_valid[
                                      content_quotations[quo_index][0] + 1:content_quotations[quo_index][1]]
                                rls[cur_key] = ori
                                quo_index += 1
                            else:
                                rls[cur_key] = eval(lk[1])
            cur_res[cur_bracket[0]] = rls
            # replace separators
            s = s[:cur_bracket[0]] + s[cur_bracket[0]:cur_bracket[1]].replace(',', '_').replace('=', '_') \
                + s[cur_bracket[1]:]

        for key in cur_res:
            self.dict = cur_res[key]
        return

    def dump(self):
        return str(self.dict)

    def loadLuaTable(self, f):
        self.load(open(f).read())

    def dumpLuaTable(self, f):
        ss = self.genStr(self.dict)
        fw = open(f, 'wb')
        fw.write(ss)
        fw.close()

    def loadDict(self, d):
        self.dict = eval(str(d))

    def dumpDict(self):
        return eval(str(self.dict))

    # my functions
    def genStr(self, d):
        if isinstance(d, dict):
            res_str = '{'
            for k in d:
                res_str += '[' + self.genStr(k) + ']=' + self.genStr(d[k]) + ','
            res_str += '}'
            return res_str
        elif isinstance(d, list):
            res_str = '{'
            for k in d:
                res_str += self.genStr(k) + ','
            res_str += '}'
            return res_str
        elif isinstance(d, type(None)):
            return 'nil'
        elif isinstance(d, float) or isinstance(d, int):
            return str(d)
        elif isinstance(d, bool):
            if d == False:
                return 'false'
            else:
                return 'true'
        else:
            return repr(d)

    def validStr(self, s):
        if len(s) < 2:
            return False
        if s[0] == '\"' and s[-1] == '\"':
            return True
        elif s[0] == '\'' and s[-1] != '\'':
            return True
        else:
            return False

    def removeSpace(self, s):
        # step 1: scan for quotations
        self.scanQuotations(s)
        # step 2: iterate unquotation part
        b1 = 0
        b2 = 0
        while b2 < len(s):
            hitp = None
            for pai in self.quotations:
                if b2 in pai:
                    hitp = pai
                    break
            if hitp != None:
                b2 = hitp[0]
                nb1 = hitp[1]
                noquo = s[b1:b2]
                # remove useless space of cur noquo
                temp_valid = noquo
                temp_valid = "{".join(map(lambda x: x.strip(), temp_valid.split('{')))
                temp_valid = "}".join(map(lambda x: x.strip(), temp_valid.split('}')))
                temp_valid = ",".join(map(lambda x: x.strip(), temp_valid.split(';')))  # replace ; to ,
                temp_valid = ",".join(map(lambda x: x.strip(), temp_valid.split(',')))
                temp_valid = "=".join(map(lambda x: x.strip(), temp_valid.split('=')))
                temp_valid = "[".join(map(lambda x: x.strip(), temp_valid.split('[')))
                temp_valid = "]".join(map(lambda x: x.strip(), temp_valid.split(']')))
                self.cur_valid += temp_valid + s[b2:nb1]
                b1 = nb1
                b2 = b1
            b2 += 1
        # last noquo
        noquo = s[b1:b2]
        # remove useless space of cur noquo
        temp_valid = noquo
        temp_valid = "{".join(map(lambda x: x.strip(), temp_valid.split('{')))
        temp_valid = "}".join(map(lambda x: x.strip(), temp_valid.split('}')))
        temp_valid = ",".join(map(lambda x: x.strip(), temp_valid.split(';')))
        temp_valid = ",".join(map(lambda x: x.strip(), temp_valid.split(',')))
        temp_valid = "=".join(map(lambda x: x.strip(), temp_valid.split('=')))
        temp_valid = "[".join(map(lambda x: x.strip(), temp_valid.split('[')))
        temp_valid = "]".join(map(lambda x: x.strip(), temp_valid.split(']')))
        self.cur_valid += temp_valid

    def scanQuotations(self, s):
        quotation_1 = []
        quotation_2 = []
        quotation_stack_1 = []
        quotation_stack_2 = []
        for i in xrange(0, len(s)):
            if s[i] == '\"':
                if len(quotation_stack_2) == 1:
                    if len(quotation_stack_1) == 0:
                        quotation_2.append((quotation_stack_2[-1], i))
                        quotation_stack_2.pop()
                    elif len(quotation_stack_1) > 0 and quotation_stack_1[-1] > quotation_stack_2[-1]:
                        quotation_stack_1 = []
                        quotation_2.append((quotation_stack_2[-1], i))
                        quotation_stack_2.pop()
                    elif len(quotation_stack_1) > 0 and quotation_stack_1[-1] < quotation_stack_2[-1]:
                        quotation_stack_2.pop()
                else:
                    quotation_stack_2.append(i)
            elif s[i] == '\'':
                if len(quotation_stack_1) == 1:
                    if len(quotation_stack_2) == 0:
                        quotation_1.append((quotation_stack_1[-1], i))
                        quotation_stack_1.pop()
                    elif len(quotation_stack_2) > 0 and quotation_stack_2[-1] > quotation_stack_1[-1]:
                        quotation_stack_2 = []
                        quotation_1.append((quotation_stack_1[-1], i))
                        quotation_stack_1.pop()
                    elif len(quotation_stack_2) > 0 and quotation_stack_2[-1] < quotation_stack_1[-1]:
                        quotation_stack_1.pop()
                else:
                    quotation_stack_1.append(i)
        if len(quotation_stack_1) or len(quotation_stack_2):
            raise Exception('lua table string format Error on quotations')
        self.quotations = quotation_1 + quotation_2
