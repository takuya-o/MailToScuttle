#!/usr/bin/env python
# -*- coding: utf-8 -*-
#see http://qiita.com/stkdev/items/a44976fb81ae90a66381
import sys
import email.parser
import email.header
import urllib2
import urllib
from HTMLParser import HTMLParser
import re
import requests

#Global変数
url = [];

class MyHTMLParser(HTMLParser):
    flg=False
    last=""
    def handle_starttag(self, tagname, attribute):
        if tagname.lower() == "a":
            for i in attribute:
                if i[0].lower() == "href":
                    if re.match(r"^https?://", i[1]):
                        #mailto:とかあるのでhttp://だけ保存対象にする
                        if re.match(r"https://www.facebook.com/", i[1]):
                            if re.match(r"https://www.facebook.com/n/\?saved%2Fredirect%2F", i[1]):
                                 matched = re.search("&uri=[^&]*", i[1]).group()
                                 self.last =  urllib.unquote( re.sub(r"^&uri=", "", matched) )
                            else:
                                #facebookではリンク以外の配信停止などは保存しない
                                continue
                        else:
                            #facebook以外
                            self.last= i[1]
                        self.flg=True
    def handle_data(self, data):
        if self.flg:
            url.append({'url': self.last, 'title':data, 'desc': "", 'tags': "", 'private': False})
            self.flg=False
        #TODO: urlとdescriptしか対応できていない。最低でもtagsとかほしいよね

class MyTextParser():
#http://URLSs  --URLが来たときに前のがあったらpush
#(title:|)
#desc:
#tags:
    uri = ""
    title = ""
    desc = ""
    tags = ""
    private = False
    urlflg = False
    subject = ""
    def flash(self):
        #print "Flash: " + self.uri
        if self.uri != "":
            if self.title== "": #タイトル無いときにはメールSubjectで代替
                self.title = self.subject
                self.subject = "" #一度つかったらクリア
            url.append({'url': self.uri, 'title': self.title, 'desc': self.desc, 'tags': self.tags,
                      'private': self.private});
            #print self.uri + self.title
            self.uri = ""
            self.title = ""
            self.desc = ""
            self.tags = ""
            self.uriflg = False
    def parse(self, body, subject):
        self.subject = subject
        self.flash()
        for line in body.splitlines():
            #print line
            matched = re.search(r"\s*https?://[^\s]*", line)
            #TODO: 説明 http:// タイプもあるよ
            if matched:
                self.flash()
                self.uri = matched.group()
                self.uriflg = True
                #print "FIND url:" + self.uri
            elif re.search(r"^\s*title:\s", line, re.IGNORECASE):
                self.title = line.sub(r"^\s*title:\s", "", line, re.IGNORECASE)
                #print "FIND title:" + self.title
            elif re.search(r"^\s*desc:\s", line, re.IGNORECASE):
                self.desc = line.sub(r"^\s*desc:\s", "", line, re.IGNORECASE)
                #print "FIND desc:" + self.desc
            elif re.search(r"^\s*tags:\s", line, re.IGNORECASE):
                self.tags = line.sub(r"^\s*tags:\s", "", line, re.IGNORECASE)
                #print "FIND tags:" + self.tags
            elif re.search(r"^\s*private:\s", line, re.IGNORECASE):
                self.private = ( line.sub(r"^\s*private:\s", "", line, re.IGNORECASE) == "True" )
                #print "FIND private:" + str(self.tags)
            elif self.uriflg and self.tile == "":
                self.title = line.sub(r"^\s*", "", line, re.IGNORECASE)
                #print "FIND title:" + self.title
            self.uriflg=False #urlの次の行だけね
        self.flash()


def main():
    if len(sys.argv) < 4:
        sys.stderr.write("Usage: " + sys.argv[0] + " URL user password")
        sys.exit(1)

    scuttle = sys.argv[1]   #Scuttle URL https://example.com/scuttle/
    user = sys.argv[2]     # User Name
    passwd = sys.argv[3]   # Password
    sys.argv[3]=""

    #print(scuttle + " : " + user )
    #メールを標準入力から読み込む
    email_default_encoding = 'utf-8' #'iso-2022-jp'

    msg = email.message_from_file(sys.stdin)
    #print(msg.keys())
    subject=msg.get("Subject")
    #print subject

    #エンコーディング判断
    try:
        msg_encoding = msg.get("Subject")[0][1] or email_default_encoding
    except Exception:
        #print("!!! Can't found Subject encording." )
        if re.match(r"=\?iso-2022-jp\?", subject, re.IGNORECASE):
            msg_encoding = 'iso-2022-jp'
        elif re.match(r"=\?utf-8\?", subject, re.IGNORECASE):
            msg_encoding = 'utf-8'
        else:
            msg_encoding = email_default_encoding
    #print("=== " + msg_encoding )

    #サブジェクト取り出し
    subjectbase = email.header.decode_header(msg.get('Subject'))
    subject = ""
    for sub in subjectbase:
        if isinstance(sub[0],bytes):
            subject += sub[0].decode(msg_encoding)
        else:
            subject += sub[0]
    #print("=== Subject: " + subject)

    #メッセージBodyを読み込む マルチパート対策
    body = ""
    if msg.is_multipart():
        for payload in msg.get_payload():
            if payload.get_content_type() == "text/html":
                body = payload.get_payload(decode=True)
                #aレコードを取り出す
                parser = MyHTMLParser()
                parser.feed(body)
                parser.close()
    else:
        if msg.get_content_type() == "text/plain":
            body = msg.get_payload(decode=True)
            #urlを取り出す
            myparser = MyTextParser()
            myparser.parse(body, subject)

    #とりだしたURLをscuttleへ
    while len(url):
        d=url.pop()
        #print d.keys()
        if d['tags'] == "":
            # if re.search("Raspberry", d['title']):
            #     d['tags'] = "Raspberry Pi" + " autoTag"
            if re.search("IoT", d['title']):
                d['tags'] = "IoT" + " autoTag"
            if re.search("経済", d['title']):
                d['tags'] = "経済" + " autoTag"
            if re.search("企業", d['title']):
                d['tags'] = "企業" + " autoTag"
            if re.search("新幹線", d['title']):
                d['tags'] = "新幹線" + " autoTag"
            if re.search("Windows", d['title']):
                d['tags'] = "Windows" + " autoTag"
            if re.search("SIM", d['title']):
                d['tags'] = "SIM" + " autoTag"

        #POSTパラメータは二つ目の引数に辞書で指定する
        response = requests.post(
            scuttle + 'api/posts/add',
            {'url': d['url'],
             'description': d['title'],
             'extended': d['desc'],
             'tags': d['tags'],
             'replace': 'no', #scuttleでは無効 'yes'にできない。新規登録のみ
             'shared': 'yes'  #scuttleでは無効 'no'にできない。常に共有
            },
            auth=(user, passwd))

        print("URL=" + d['url'])# + "  TITLE=" + d['title'])
        # print("DESC=" + d['desc'])
        # print("TAGS=" + d['tags'])
        # print("PRIVATE=" + str(d['private']))

        if response.status_code == 200:
            #<result code="done" /> 正常終了なら無言
            res = re.search(r'<result code="done" />', response.text)
            if not res:
                res = re.search(r' code="[^"]*" ', response.text)
                print "ERROR: " + res.group()
        else:
            print(response)

#        %2Fredirect%2F&amp;object_id=1363881683627184&amp;surface=saved_email_reminder&amp;mechanism=clickable_content&amp;ndid=536c57d79b0e1G5af37e34383eG0G377G4a4ad872&amp;uri=http%3A%2F%2Fwww.itmedia.co.jp%2Fbusiness%2Farticles%2F1607%2F01%2Fnews032_3.html&amp;ext=1468807559&amp;hash=AeSz2jckCsCTt-Bw&amp;medium=email&amp;mid=536c57d79b0e1G5af37e34383eG0G377G4a4ad872&amp;bcode=1.1467597959.Abn9JZ7_LOr1-2o3&amp;n_m=takuya%40page.on-o.com" style="color: #3b5998; text-decoration: none; font-family: Helvetica Neue,Helvetica,Lucida Grande,tahoma,verdana,arial,sans-serif; font-size: 16px; line-height: 21px; font-weight: bold" target="_blank" rel="noreferrer">東海道新幹線の新型車両「N700S」はリニア時代の布石 (3/4)</a>
# header=True
# while True:
#     try:
#         i = raw_input()
#         print(i)
#         if re.match("^$", i):
#             header=False
#             print("==Header END==")
#             continue
#         if header:
#             continue
#     except EOFError:
#         break

if __name__=='__main__':
    main()
