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
        self.oristr = ""

    def load(self, s):
        self.oristr = s
        self.scanQuotations(s)
        # remove comments
        self.removeComment(s)
        s = self.cur_valid
        # update quotations
        self.scanQuotations(s)
        # remove useless spaces
        self.removeSpace(s)
        s = self.cur_valid
        # update quotations
        self.scanQuotations(s)
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
            # update remainder quotations
            self.quotations = sorted(list(set(self.quotations)-set(content_quotations)))
            quo_index = 0
            ls = content.split(',')  # split with separator
            for l in ls:
                if l.find('=') > -1:
                    is_list = False
                    break
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
                            elif len(l) > 1 and l[0] == '{' and l[-1] == '}':
                                rls[index] = cur_res[pj_keys[pj_i]]
                                del cur_res[pj_keys[pj_i]]
                                pj_i += 1
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
                            try:
                                raise Exception("error key")
                            except:
                                self.selfRecur(self.oristr, 1000)
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
        in_str=open(f).read()
        self.load(in_str)

    def dumpLuaTable(self, f):
        ss = self.genStr(self.dict)
        fw = open(f,'w')
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
        elif isinstance(d, float) or isinstance(d, int) or isinstance(d, long):
            return str(d)
        elif isinstance(d, bool):
            if d == False:
                return 'false'
            else:
                return 'true'
        else:
            if isinstance(d, str):
                d=d.replace('\\b','\b').replace('\\f','\f').replace('\\r','\r').replace('\\n','\n').replace('\\t','\t').replace('\\"','\"').replace("\\'",'\'').replace("\\\\",'\\')
                return repr(d)

    def validStr(self, s):
        if len(s) < 2:
            return False
        if s[0] == '\"' and s[-1] == '\"':
            return True
        elif s[0] == '\'' and s[-1] == '\'':
            return True
        else:
            return False

    def removeSpace(self, s):
        self.cur_valid=''
        # iterate unquotation part
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
        in_esca=False
        x_cnt=0
        for i in xrange(0, len(s)):
            if s[i] == '\\' and not in_esca:
                in_esca = True
                continue
            if in_esca:
                if s[i] in ['\'','\"','\\','b','t','r','n','f']:
                    in_esca = False
                    continue
                elif s[i]=='x' or x_cnt>0:
                    x_cnt+=1
                    if x_cnt==3:
                        x_cnt=0
                    continue
                else:
                    raise Exception('lua table string format Error on escape')
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
        self.quotations = sorted(quotation_1 + quotation_2)

    def removeComment(self,s):
        state = 'Empty'
        self.cur_valid = ''
        i=0
        while i<len(s):
            if state=='Empty':
                if s[i]=='-':
                    state = 'Ready'
                else:
                    for pai in self.quotations:
                        if i == pai[0]:
                            self.cur_valid +=s[i:pai[1]]
                            i=pai[1]
                    self.cur_valid += s[i]
            elif state=='Ready':
                if s[i]=='-':
                    state = 'Begin'
                else:
                    state='Empty'
                    self.cur_valid += s[i-1]
                    self.cur_valid += s[i]
            elif state=='Begin':
                if s[i]=='\n':
                    state='Empty'
            i+=1

    def selfRecur(self, s, idx):
        if idx >= len(s):
            raise Exception, "len exceed"
        if s[idx] == '\x00':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x01':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x02':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x03':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x04':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x05':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x06':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x07':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x08':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\t':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\n':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x0b':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x0c':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\r':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x0e':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x0f':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x10':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x11':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x12':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x13':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x14':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x15':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x16':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x17':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x18':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x19':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x1a':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x1b':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x1c':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x1d':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x1e':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x1f':
            self.selfRecur(s, idx + 1)
        elif s[idx] == ' ':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '!':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '"':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '#':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '$':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '%':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '&':
            self.selfRecur(s, idx + 1)
        elif s[idx] == "'":
            self.selfRecur(s, idx + 1)
        elif s[idx] == '(':
            self.selfRecur(s, idx + 1)
        elif s[idx] == ')':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '*':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '+':
            self.selfRecur(s, idx + 1)
        elif s[idx] == ',':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '-':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '.':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '/':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '0':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '1':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '2':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '3':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '4':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '5':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '6':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '7':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '8':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '9':
            self.selfRecur(s, idx + 1)
        elif s[idx] == ':':
            self.selfRecur(s, idx + 1)
        elif s[idx] == ';':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '<':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '=':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '>':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '?':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '@':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'A':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'B':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'C':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'D':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'E':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'F':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'G':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'H':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'I':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'J':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'K':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'L':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'M':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'N':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'O':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'P':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'Q':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'R':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'S':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'T':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'U':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'V':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'W':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'X':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'Y':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'Z':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '[':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\\':
            self.selfRecur(s, idx + 1)
        elif s[idx] == ']':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '^':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '_':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '`':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'a':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'b':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'c':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'd':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'e':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'f':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'g':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'h':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'i':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'j':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'k':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'l':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'm':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'n':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'o':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'p':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'q':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'r':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 's':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 't':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'u':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'v':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'w':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'x':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'y':
            self.selfRecur(s, idx + 1)
        elif s[idx] == 'z':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '{':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '|':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '}':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '~':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x7f':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x80':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x81':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x82':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x83':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x84':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x85':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x86':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x87':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x88':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x89':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x8a':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x8b':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x8c':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x8d':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x8e':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x8f':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x90':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x91':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x92':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x93':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x94':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x95':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x96':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x97':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x98':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x99':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x9a':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x9b':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x9c':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x9d':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x9e':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\x9f':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xa0':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xa1':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xa2':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xa3':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xa4':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xa5':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xa6':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xa7':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xa8':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xa9':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xaa':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xab':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xac':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xad':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xae':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xaf':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xb0':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xb1':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xb2':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xb3':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xb4':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xb5':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xb6':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xb7':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xb8':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xb9':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xba':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xbb':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xbc':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xbd':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xbe':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xbf':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xc0':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xc1':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xc2':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xc3':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xc4':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xc5':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xc6':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xc7':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xc8':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xc9':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xca':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xcb':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xcc':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xcd':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xce':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xcf':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xd0':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xd1':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xd2':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xd3':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xd4':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xd5':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xd6':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xd7':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xd8':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xd9':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xda':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xdb':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xdc':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xdd':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xde':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xdf':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xe0':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xe1':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xe2':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xe3':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xe4':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xe5':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xe6':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xe7':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xe8':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xe9':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xea':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xeb':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xec':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xed':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xee':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xef':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xf0':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xf1':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xf2':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xf3':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xf4':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xf5':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xf6':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xf7':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xf8':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xf9':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xfa':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xfb':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xfc':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xfd':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xfe':
            self.selfRecur(s, idx + 1)
        elif s[idx] == '\xff':
            self.selfRecur(s, idx + 1)
