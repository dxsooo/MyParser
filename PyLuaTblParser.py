class PyLuaTblParser():
    '''
    PyLuaTblparser
    '''

    def __init__(self):
        self.dict = {}
        self.quotations = []
        self.cur_valid = ''

    def load(self, s):
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
        # make escapes
        self.makeEscapes(s)
        s = self.cur_valid

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

        # iterate brackets
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
            self.quotations = sorted(list(set(self.quotations) - set(content_quotations)))
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
                            index += 1
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
        # at last the only key-value is final result
        for key in cur_res:
            self.dict = cur_res[key]

    def dump(self):
        return str(self.dict)

    def loadLuaTable(self, f):
        in_str = open(f).read()
        self.load(in_str)

    def dumpLuaTable(self, f):
        ss = self.genStr(self.dict)
        fw = open(f, 'w')
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
        self.cur_valid = ''
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
        in_esca = False
        x_cnt = 0
        for i in xrange(0, len(s)):
            if s[i] == '\\' and not in_esca:
                in_esca = True
                continue
            if in_esca:
                if s[i] in ['\'', '\"', '\\', 'b', 't', 'r', 'n', 'f']:
                    in_esca = False
                    continue
                elif s[i] == 'x' or x_cnt > 0:
                    x_cnt += 1
                    if x_cnt == 3:
                        x_cnt = 0
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

    escape_map = {'\'': '\'', '\"': '\"', '\\': '\\', 'b': '\b', 't': '\t', 'n': '\n', 'f': '\f', 'r': '\r',
                  'x08': '\b', 'x0c': '\f'}

    def makeEscapes(self, s):
        self.cur_valid = s
        for j in xrange(0, len(self.quotations)):
            p = self.quotations[j]
            sub_str = self.cur_valid[p[0]:p[1]]
            n_sub_str = ''
            i = 0
            in_esca = False
            cnt = 0
            while i < len(sub_str):
                if sub_str[i] == '\\' and not in_esca:
                    in_esca = True
                    cnt += 1
                elif in_esca:
                    if sub_str[i] in ['\'', '\"', '\\', 'b', 't', 'r', 'n', 'f']:
                        in_esca = False
                        n_sub_str += self.escape_map[sub_str[i]]
                    elif sub_str[i] == 'x':
                        in_esca = False
                        n_sub_str += self.escape_map[sub_str[i:i + 3]]
                        i += 3
                        cnt += 2
                        continue
                    else:
                        raise Exception('lua table string format Error on escape')
                else:
                    n_sub_str += sub_str[i]
                i += 1
            self.cur_valid = self.cur_valid[:p[0]] + n_sub_str + self.cur_valid[p[1]:]
            self.quotations[j] = (p[0], p[1] - cnt)
            for k in range(j + 1, len(self.quotations)):
                self.quotations[k] = (self.quotations[k][0] - cnt, self.quotations[k][1] - cnt)

    def removeComment(self, s):
        state = 'Empty'
        self.cur_valid = ''
        ctype = 1
        i = 0
        while i < len(s):
            if state == 'Empty':
                if s[i] == '-':
                    state = 'Ready'
                else:
                    for pai in self.quotations:
                        if i == pai[0]:
                            self.cur_valid += s[i:pai[1]]
                            i = pai[1]
                    self.cur_valid += s[i]
            elif state == 'Ready':
                if s[i] == '-':
                    if s[i + 1:i + 3] == '[[':
                        ctype = 2
                    else:
                        ctype = 1
                    state = 'Begin'
                else:
                    state = 'Empty'
                    self.cur_valid += s[i - 1]
                    self.cur_valid += s[i]
            elif state == 'Begin':
                if ctype == 1 and s[i] == '\n':
                    state = 'Empty'
                elif ctype == 2 and s[i:i + 2] == ']]':
                    state = 'Empty'
                    i += 1
            i += 1
