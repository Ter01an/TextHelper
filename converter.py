import pymorphy2
import re
from natasha import (
    Segmenter,
    NewsEmbedding,
    NewsSyntaxParser,
    Doc
)
from inc import resource_path


class Converter:

    def __init__(self):
        self.replacer = ""
        self.text_gender = 'masc'
        self.setting_gender = 'auto'
        self.syntax_map = []
        self.segmenter = Segmenter()
        self.emb = NewsEmbedding()
        self.syntax_parser = NewsSyntaxParser(self.emb)
        self.morph = pymorphy2.MorphAnalyzer(lang='ru', path=resource_path('data/'))

    def Process(self, buffer, debug=False):
        text = buffer[0]
        html = buffer[1]
        html_body = ""

        # Remove \x00
        if text:
            text = text.rstrip('\x00')

        if html:
            html_body = html.rstrip('\x00')

        sents = self.Sentenize(text)
        self.GenderInit(sents)
        self.SyntaxMap(sents)

        position_text = 0
        position_html = html_body.find('<!--StartFragment-->')
        if position_html == -1:
            output = re.search('<body.*?>', html_body)
            if output is not None:
                positions = self.find(html_body, output.group(0))
                position_html = positions[1]

        for n, sent in enumerate(sents):
            words = self.Words(sent, n)
            for i, token in enumerate(sent.tokens):
                # Html
                if html_body:
                    temp = position_html
                    position_html = html_body.find(token.text, position_html)
                    before = html_body[:position_html]

                    if position_html == -1:
                        position_html = temp
                    else:
                        if words[i] != token.text:
                            if debug:
                                after = "<span style='background:yellow;mso-highlight:yellow'>" + words[
                                    i] + "</span>" + html_body[position_html + len(token.text):]
                            else:
                                after = words[i] + html_body[position_html + len(token.text):]
                        else:
                            after = html_body[position_html:]

                        if words[i] != '':
                            position_html = position_html + len(token.text)

                        html_body = before + after

                # Text
                temp = position_text
                position_text = text.find(token.text, position_text)
                before = text[:position_text]

                if position_text == -1:
                    position_text = temp
                else:
                    if words[i] != token.text:
                        after = words[i] + text[position_text + len(token.text):]
                    else:
                        after = text[position_text:]

                    if words[i] != '':
                        position_text = position_text + len(token.text)

                    text = before + after

        html_end = len(html_body.encode("utf-8"))

        output = re.search('EndHTML:\d{10}', html_body)
        if output is not None:
            html_body = html_body.replace(output.group(0), 'EndHTML:%010d' % html_end)

        output = re.search('EndFragment:\d{10}', html_body)
        if output is not None:
            pos = self.find(html_body, "<!--EndFragment-->")
            if pos[0] == -1:
                end = re.search('</html>', html_body)
                if end is not None:
                    pos = self.find(html_body, end.group(0))
                    html_body = html_body.replace(output.group(0), 'EndFragment:%010d' % pos[0])
            else:
                html_body = html_body.replace(output.group(0), 'EndFragment:%010d' % pos[0])

        if not html_body:
            html_body = None

        return text, html_body

    def Words(self, sent, n):
        genders = self.GenderSent(sent)
        gender = self.GenderMost(genders)

        if gender and len(genders):
            sent_gender = gender
        else:
            sent_gender = self.text_gender

        if self.setting_gender != 'auto':
            sent_gender = self.setting_gender

        prev_word = False
        stop = False

        final_sent = []

        for i, token in enumerate(sent.tokens):
            morphs = self.morph.parse(token.text)
            morph = morphs[0]

            if morphs[0].score == 0.5 and morphs[1].score == 0.5:
                items = self.FindChild(sent.syntax.tokens[i].id, sent.syntax.tokens, ['obj', 'obl'])
                for item in items:
                    morphs_item = self.morph.parse(item.text)
                    morph_item = morphs_item[0]

                    # loct or gent
                    if morph_item.tag.animacy == 'anim':
                        if re.search('ить$', morphs[0].normal_form):
                            morph = morphs[0]
                        if re.search('ить$', morphs[1].normal_form):
                            morph = morphs[1]

                    if morph_item.tag.animacy == 'inan':
                        if re.search('еть$', morphs[0].normal_form):
                            morph = morphs[0]
                        if re.search('еть$', morphs[1].normal_form):
                            morph = morphs[1]

            word = self.pronoun(token.text, sent_gender)
            if token.text in ['"', '«']:
                stop = True

            if token.text in ['"', '»']:
                stop = False

            if not stop and morph.tag.person == '1per' and (morph.tag.POS in ['VERB', 'NPRO']):
                inflect = morph.inflect({'3per'})

                prep = False

                if inflect:
                    word = inflect.word
                else:
                    if i - 1 >= 0:
                        text_prev = sent.tokens[i - 1].text
                        morphs_prev = self.morph.parse(text_prev)
                        morph_prev = morphs_prev[0]

                        if morph_prev.tag.POS == 'PREP':
                            word = self.pronoun(text_prev.lower() + " " + token.text.lower(), sent_gender)
                            prev_word = text_prev
                            final_sent[len(final_sent) - 1] = ""

                            prep = True

                    if not prep:
                        if self.syntax_map[n] and morph.tag.number == 'sing' and morph.tag.case == 'nomn':
                            morphs_rep = self.morph.parse(self.replacer)
                            morph_rep = morphs_rep[0]
                            replacer = morph_rep.inflect({sent_gender, morph.tag.case})

                            word = replacer.word
                        else:
                            word = self.pronoun(token.text.lower(), sent_gender)

            if token.text[0].isupper() or (prev_word and prev_word[0].isupper()):
                string_list = list(word)
                string_list[0] = string_list[0].upper()
                word = "".join(string_list)
                prev_word = None

            final_sent.append(word)

        return final_sent

    def Sentenize(self, text):
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.parse_syntax(self.syntax_parser)

        return doc.sents

    def setReplacer(self, value):
        self.replacer = value

    def setGender(self, value):
        self.setting_gender = value

    def SyntaxMap(self, sents):
        map = []
        for sent in sents:
            stop = False
            firstPerson = 0
            thirdPerson = 0
            thirdNPRO = 0
            for token in sent.syntax.tokens:

                if token.text in ['"', '«']:
                    stop = True

                if token.text in ['"', '»']:
                    stop = False

                if token.rel in ['nsubj', 'obj', 'obl'] and not stop:
                    morphs = self.morph.parse(token.text)
                    morph = morphs[0]

                    if morph.tag.person == '1per' and morph.tag.case == 'nomn':
                        firstPerson += 1

                    if (morph.tag.person == '3per' or morph.tag.animacy == 'anim') and morph.tag.number == 'sing':
                        thirdPerson += 1

                    if morph.tag.person == '3per' and morph.tag.case == 'nomn' and morph.tag.POS == 'NPRO':
                        thirdNPRO += 1

            map.append((firstPerson, thirdPerson, thirdNPRO))

        result = []
        for i, item in enumerate(map):
            replace = False
            if i > 0:
                prev = map[i - 1]
                if prev[1] >= 1 and item[0] >= 1:
                    replace = True
            if item[2] > 0:
                replace = True

            result.append(replace)

        self.syntax_map = result

    @staticmethod
    def find(text, word):
        en_text = bytes(text, encoding="utf-8")
        en_word = bytes(word, encoding="utf-8")
        start = en_text.find(en_word)
        return (start, start + len(en_word))

    @staticmethod
    def FindChild(id, tokens, rel=['nsubj', 'conj']):
        list = []
        for token in tokens:
            if token.head_id == id and (not rel or token.rel in rel):
                list.append(token)
        return list

    def GenderInit(self, sents):
        self.text_gender = self.Gender(sents)

    def GenderSent(self, sent):
        genders = []
        for token in sent.syntax.tokens:
            if re.search('_0$', token.head_id):
                morph_parse = self.morph.parse(token.text)
                morph_item = morph_parse[0]

                if morph_item.tag.POS != "VERB" and morph_item.tag.gender not in ['masc', 'femn']:
                    for morph in morph_parse:
                        if morph.tag.POS == "VERB":
                            morph_item = morph

                childs = self.FindChild(token.id, sent.syntax.tokens)

                if len(childs):
                    for child in childs:
                        morph_child = self.morph.parse(child.text)
                        morph_child_item = morph_child[0]

                        if child.rel in ['nsubj', 'conj'] and (morph_child_item.tag.person == '1per' or morph_child_item.tag.POS == 'VERB') and morph_item.tag.gender and morph_item.tag.gender in ['masc', 'femn']:
                            genders.append(morph_item.tag.gender)

        return genders

    @staticmethod
    def GenderMost(genders):
        if len(genders) == 0:
            return 'masc'

        most = None
        qty_most = 0

        for item in genders:
            qty = genders.count(item)
            if qty > qty_most:
                qty_most = qty
                most = item

        if most is None:
            return 'masc'

        return most

    def Gender(self, sents):
        genders = []
        for sent in sents:
            genders += self.GenderSent(sent)

        return self.GenderMost(genders)

    @staticmethod
    def pronoun(word, gender):
        masc_pronouns = {
            'я': 'он',
            'мы': 'они',
            'ко мне': 'к нему',
            'к нам': 'к ним',
            'для меня': 'для него',
            'за мной': 'за ним',
            'у меня': 'у него',
            'при мне': 'при нём',
            'на меня': 'на него',
            'мне': 'ему',
            'наши': 'их',
            'меня': 'его',
            'мною': 'им',
            'моих': 'его',
            'мою': 'его',  # !
            'мои': 'его',  # !
            'моя': 'его',  # !
            'мое': 'его',  # !
            'моё': 'его',  # !
        }
        femn_pronouns = {
            'я': 'она',
            'мы': 'они',
            'ко мне': 'к ней',
            'к нам': 'к ним',
            'для меня': 'для неё',
            'за мной': 'за ней',
            'у меня': 'у нее',
            'при мне': 'при ней',
            'на меня': 'на неё',
            'мне': 'ей',
            'наши': 'их',
            'меня': 'её',
            'мною': 'ею',
            'моих': 'её',
            'мою': 'её',  # !
            'мои': 'её',  # !
            'моя': 'её',  # !
            'мое': 'её',  # !
            'моё': 'её',  # !
        }
        if gender == 'masc':
            if word in masc_pronouns:
                return masc_pronouns[word]
            else:
                return word

        if gender == 'femn':
            if word in femn_pronouns:
                return femn_pronouns[word]
            else:
                return word

        return word
