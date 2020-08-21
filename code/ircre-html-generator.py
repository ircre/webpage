#!/usr/bin/env python3

###
# 这是为了更新https://ircre.org/research.html文件而写的代码
# 目的是从ircre.bib自动生成我们格式的research.html文件
#
###

import sys
import os

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter

from datetime import datetime


currentdir = os.path.dirname(os.path.abspath(__file__))
ircre_bib_path = currentdir+r'/../bib7image/ircre.bib'
articles_bib_path = currentdir+r'/../bib7image/articles.bib'
others_bib_path = currentdir+r'/../bib7image/others.bib'
sorted_articles_bib_path = currentdir+r'/../bib7image/sorted-articles.bib'
top15_bib_path = currentdir+r'/../bib7image/top15.bib'
newircre_bib_path = currentdir+r'/../bib7image/newircre.bib'
researchnew_html_path = currentdir+r'/../www/researchnew.html'


def bibtexclassify():
    parser = BibTexParser(common_strings=False)
    parser.ignore_nonstandard_types = False
    with open(ircre_bib_path, encoding='utf8') as bibtexfile:
        ircrebib_database = bibtexparser.load(bibtexfile, parser)
    allentries = ircrebib_database.entries.copy()
    # ----------------------------------------
    # get all articles
    # -----------------------------------------
    article_entries = []
    for i in range(len(allentries)):
        if allentries[i]['ENTRYTYPE'] == 'article':
            article_entries.append(allentries[i].copy())

    article_database = BibDatabase()
    article_database.entries = article_entries

    writer = BibTexWriter()
    writer.indent = '    '
    writer.order_entries_by = ('order',)
    with open(articles_bib_path, 'w', encoding='utf8') as article_file:
        bibtexparser.dump(article_database, article_file, writer=writer)

    otherentries = []
    for i in range(len(allentries)):
        if allentries[i]['ENTRYTYPE'] == 'inbook' or allentries[i]['ENTRYTYPE'] == 'inproceedings' or allentries[i]['ENTRYTYPE'] == 'incollection':
            otherentries.append(allentries[i].copy())

    other_database = BibDatabase()
    other_database.entries = otherentries

    writer2 = BibTexWriter()
    writer2.indent = '    '
    writer2.order_entries_by = ('order',)
    with open(others_bib_path, 'w', encoding='utf8') as others_file:
        bibtexparser.dump(other_database, others_file, writer=writer2)

    return 0


def articlessort():
    parser = BibTexParser(common_strings=False)
    parser.ignore_nonstandard_types = False

    with open(articles_bib_path, encoding='utf8') as articlesfile:
        articles_database = bibtexparser.load(articlesfile, parser)

    articles = articles_database.entries.copy()

    for i in range(len(articles)):
        try:
            articles[i]['sortkey1'] = float(articles[i]['impactfactor'])
        except:
            articles[i]['sortkey1'] = float(0)
        try:
            articles[i]['sortkey2'] = int(articles[i]['cited'])
        except:
            articles[i]['sortkey2'] = int(0)

    sorted_by_journalif_cited = sorted(articles, key=lambda x: (
        x['sortkey1'], x['journal'], x['sortkey2'], x['year']), reverse=True)

    for i in range(len(sorted_by_journalif_cited)):
        sorted_by_journalif_cited[i]['order'] = str(i).zfill(6)

    for i in range(len(sorted_by_journalif_cited)):
        sorted_by_journalif_cited[i].pop('sortkey1')
        sorted_by_journalif_cited[i].pop('sortkey2')

    sortedarticlesdatabase = BibDatabase()
    sortedarticlesdatabase.entries = sorted_by_journalif_cited

    writer = BibTexWriter()
    writer.indent = '    '
    writer.order_entries_by = ('order',)
    with open(sorted_articles_bib_path, 'w', encoding='utf8') as sortedarticlesfile:
        bibtexparser.dump(sortedarticlesdatabase,
                          sortedarticlesfile, writer=writer)

    return 0


def getop15articles():
    parser = BibTexParser(common_strings=False)
    parser.ignore_nonstandard_types = False

    with open(articles_bib_path, encoding='utf8') as article_file:
        article_database = bibtexparser.load(article_file, parser)

    article_entries = article_database.entries.copy()

    for i in range(len(article_entries)):
        try:
            article_entries[i]['sortkey1'] = int(article_entries[i]['cited'])
        except:
            article_entries[i]['sortkey1'] = int(0)

    articles_sorted_by_cited = sorted(
        article_entries, key=lambda x: (x['sortkey1']), reverse=True)

    top15articles = []
    for i in range(15):
        top15articles.append(articles_sorted_by_cited[i].copy())

    for i in range(len(top15articles)):
        top15articles[i]['ENTRYTYPE'] = 'toparticle'
        top15articles[i]['ID'] = top15articles[i]['ID'] + 'a'

    for i in range(len(top15articles)):
        top15articles[i].pop('sortkey1')

    top15_database = BibDatabase()
    top15_database.entries = top15articles

    writer = BibTexWriter()
    writer.indent = '    '
    writer.order_entries_by = None

    with open(top15_bib_path, 'w', encoding='utf8') as top15_file:
        bibtexparser.dump(top15_database, top15_file, writer=writer)
    return 0


def ircrebibmerge():
    articlesparser = BibTexParser(common_strings=False)
    articlesparser.ignore_nonstandard_types = False

    with open(sorted_articles_bib_path, encoding='utf8') as sortedarticle_file:
        sortedarticle_database = bibtexparser.load(
            sortedarticle_file, articlesparser)

    sortedarticles = sortedarticle_database.entries.copy()

    top15parser = BibTexParser(common_strings=False)
    top15parser.ignore_nonstandard_types = False

    with open(top15_bib_path, encoding='utf8') as top15_file:
        top15_database = bibtexparser.load(top15_file, top15parser)

    top15articles = top15_database.entries.copy()

    othersparser = BibTexParser(common_strings=False)
    othersparser.ignore_nonstandard_types = False

    with open(others_bib_path, encoding='utf8') as others_file:
        others_database = bibtexparser.load(others_file, othersparser)

    others = others_database.entries.copy()

    alldb = BibDatabase()
    entries = []

    for i in range(len(top15articles)):
        entries.append(top15articles[i].copy())

    for i in range(len(sortedarticles)):
        entries.append(sortedarticles[i].copy())

    for i in range(len(others)):
        entries.append(others[i].copy())

    alldb.entries = entries

    writer = BibTexWriter()
    writer.indent = '    '
    writer.order_entries_by = None

    with open(newircre_bib_path, 'w', encoding='utf8') as newircrebibfile:
        bibtexparser.dump(alldb, newircrebibfile, writer=writer)

    return 0


def getstatistics():
    articlesparser = BibTexParser(common_strings=False)
    articlesparser.ignore_nonstandard_types = False
    with open(articles_bib_path, encoding='utf8') as articlesfile:
        articles_database = bibtexparser.load(articlesfile, articlesparser)

    articleentries = articles_database.entries
    totalcitations = 0
    totalif = 0.0
    citationlist = []
    jourallist = []
    hihonumber = 0
    totalpublications = len(articleentries) + 28
    totalarticles = len(articleentries)
    for i in range(len(articleentries)):

        if 'cited' in articleentries[i]:
            citednumber = int(articleentries[i]['cited'])
        else:
            citednumber = 0
        if 'impactfactor' in articleentries[i]:
            impactfactor = float(articleentries[i]['impactfactor'])
        else:
            impactfactor = 0.0

        if 'hihosubject' in articleentries[i]:
            hihonumber = hihonumber + 1

        citationlist.append(citednumber)
        jourallist.append(articleentries[i]['journal'])
        totalcitations = totalcitations + citednumber
        totalif = totalif + impactfactor
    hindex = Hindex(citationlist)
    i10index = I10index(citationlist)
    totalcitations = totalcitations + 19
    citationperpaper = totalcitations / len(articleentries)
    journalnumber = len(set(jourallist))
    averageif = totalif / len(articleentries)
    return (hindex, i10index, totalcitations, citationperpaper, journalnumber, averageif)


def Hindex(citationlist):
    """根据citationlist获得h因子。
    citationlist是按顺序的每篇文章引用次数列表
    """
    indexSet = sorted(list(set(citationlist)), reverse=True)
    for index in indexSet:
        clist = [i for i in citationlist if i >= index]
        if index <= len(clist):
            break
    return index


def I10index(citationlist):
    """根据citationlist计算i10因子。
    citationlist是按顺序的每篇文章引用次数列表
    """
    i10index = 0
    for i in range(len(citationlist)):
        if citationlist[i] >= 10:
            i10index = i10index + 1
    return i10index


def filecopyback():
    ircrebibwebsitefile = '/srv/main-websites/ircre/js/ircre.bib'
    ircrestatwebsitefile = '/srv/main-websites/ircre/js/statistics.js'
    currentdir = '/home/limingtao/ircre-bibtex/ircreupdate'
    os.system(
        '''cd ''' + currentdir + ''';''' +
        '''cp /home/limingtao/ircre-bibtex/ircreupdate/newircre.bib ''' + ircrebibwebsitefile + ''' -f ;''')
    os.system(
        '''cd ''' + currentdir + ''';''' +
        '''cp /home/limingtao/ircre-bibtex/ircreupdate/newstatistics.js ''' + ircrestatwebsitefile + ''' -f ;''')
    return 0


def generatehtml():
    (hindex, i10index, totalcitations, citationperpaper,
     journalnumber, averageif) = getstatistics()

    resulthtml = ''

    before_output = '''<html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"><meta http-equiv="Content-type" content="text/html;charset=UTF-8"><script src="./js/jquery.min.js" type="text/javascript"></script><script src="./js/moment.min.js" type="text/javascript"></script><script src="./js/reverse_list.js" type="application/javascript"></script><script async="" src="./js/popper.min.js" crossorigin="anonymous"></script><script async="" src="./js/bootstrap.min.js" crossorigin="anonymous"></script><script type="text/javascript" async="" src="./js/bibtex_js.js"></script></head><body><link rel="stylesheet" type="text/css" href="./css/ircre.css" media="all"><title>International Research Center for Renewable Energy</title><div id="header-ban"><p>&nbsp;</p><div id="logo"><img src="images/ircre-logo.jpg" width="360" height="153" alt=""></div><ul><li><a href="index.html"><span>home</span></a></li><li><a href="people.html"><span>People</span></a></li><li><a href="facility.html"><span>Facility</span></a></li><li><a href="about.html"><span>About IRCRE</span></a></li><li class="selected"><a href="research.html"><span>Research</span></a></li><li><a href="press.html">PRESS</a></li><li><a href="events.html"><span>EVENTS</span></a></li><li><a href="contact.html"><span>contact us</span></a></li></ul><p></p></div><div id="body">
    <div class="products"><div id="second-header-ban"><span id="second-header-ban-title"><h2>RESEARCH</h2></span><ul id="second-header-menu"><li id="second-menu-articles"><a href="#articles"><span id="articlesm">ARTICLES</span></a></li><li id="second-menu-bookchapters"><a href="#bookchapters"><span id="booksm">BOOK CHAPTERS</span></a></li><li id="second-menu-conferences"><a href="#conferences"><span id="conferencesm">CONFERENCES</span></a></li><li id="second-menu-organizers"><a href="#organizers"><span id="organizersm">ORGANIZERS</span></a></li><li id="second-menu-proceedings"><a href="#proceedings"><span id="proceedingsm">PROCEEDINGS</span></a></li><li id="second-menu-editorials"><a href="#editorials"><span id="editorialsm">EDITORIALS</span></a></li><li id="second-menu-seminars"><a href="#seminars"><span id="seminarsm">SEMINARS</span></a></li><li id="second-menu-committee"><a href="#committee"><span id="committeesm">COMMITTEE</span></a></li></ul></div>'''

    after_output = '''<div id="backtothetop"><a href="#top"><img src="images/buttons/5.jpg" width="105" height="28" class="button"></a></div></div></div><div id="footer">
    <div id="footeraddress"><h3>International Research Center for Renewable Energy(IRCRE)</h3>
     <ul><li>Tel: +86-29-82664664 Email: wangge2017@xjtu.edu.cn</li><li>No.28,Xianning West road,Xi'an,Shaanxi,710049 CHINA</li></ul></div><div id="copyright"><p>Copyright 2019. All rights reserved</p></div></div></body></html>'''

    top15parthtml = ''

    articleparthtml = ''

    after_output = ''

    # def generateTop15ArtitleHtml(bibFilePath):
    #     # 生成TOP15Articles部分,返回HTML
    #     parser = BibTexParser(common_strings=False)
    #     parser.ignore_nonstandard_types = False

    #     with open(bibFilePath, encoding='utf8') as bibtexFile:
    #         ircreDatabase = bibtexparser.load(bibtexFile, parser)

    #     allEntries = ircreDatabase.entries.copy()

    #     a = 0
    #     for i in range(len(allEntries)):
    #         if allEntries[i]['ENTRYTYPE'] == 'article':
    #             a += 1
    #     b = 0
    #     for i in range(len(allEntries)):
    #         if allEntries[i]['ENTRYTYPE'] == 'inbook':
    #             b += 1
    #     c = 0
    #     for i in range(len(allEntries)):
    #         if allEntries[i]['ENTRYTYPE'] == 'inproceedings':
    #             c += 1
    #     d = 0
    #     for i in range(len(allEntries)):
    #         if allEntries[i]['ENTRYTYPE'] == 'incollection':
    #             d += 1
    #     allnum = a+b+c+d
    #     print(allnum)

    #     num = 0
    #     for i in range(len(allEntries)):
    #         if allEntries[i]['ENTRYTYPE'] == 'toparticle':
    #             num += 1
    #     print(num)
    #     # 初始值为TOP15article的标题
    #     Top15Article = '''
    #     <div id="output">
    #         <div id="total-statistics">
    #             <h2>IRCRE Scientific Output</h2>
    #             <h3><span class="listcountred"><span id="totalpublications">%s</span>+</span><strong>Publications
    #                 &amp; </strong><span class="listcountblue"><span id="totalcitations">17493span>+</span> <strong>Citations since
    #                 2011</strong>
    #             </h3>
    #         </div>
    #     <div id="top15mostcitedarticles">
    #                     <h3>
    #                         <strong>Top %s Most Cited Articles</strong>
    #                     </h3></div>
    #     ''' % (allnum, num)
    #     top15ArticleBody = ''
    #     for i in range(len(allEntries)):
    #         tempHtml = ''

    #         hiho = ''
    #         image = ''
    #         formattedAuthor = ''
    #         formattedtTitle = ''
    #         journal = ''
    #         year = ''
    #         volume = ''
    #         number = ''
    #         pages = ''
    #         paperid = ''
    #         url = ''
    #         impactFactor = ''
    #         cited = ''
    #         if allEntries[i]['ENTRYTYPE'] == 'toparticle':
    #             # keys = allEntries[i].keys()
    #             # 无法显示 hihoimage
    #             if 'hihoimage' in allEntries[i].keys():
    #                 hiho = '''
    #                 <div style="float:inherit; height:40px; width:500px;text-align: left;"><img
    #             src="./images/articlecover/ISIHighlycitedlogo.jpg" alt="" width="77" height="31">
    #                 <a class="newlink" a href="./%s"
    #             target="_blank"><strong><em> %s</em></strong></a></div>
    #                 ''' % (allEntries[i]['hiholink'], allEntries[i]['hihosubject'])
    #             if 'image' in allEntries[i].keys():
    #                 image = '''<span style="float: left; width: 48px; height: 54px;"><img src="./images/articlecovers/%s" alt="" width="42" height="51"></span> ''' % (
    #                     allEntries[i]['image'])
    #             if 'formattedauthor' in allEntries[i].keys():
    #                 formattedAuthor = allEntries[i]['formattedauthor']
    #             if 'formattedtitle' in allEntries[i].keys():
    #                 formattedtTitle = ',&ldquo;<strong>%s</strong> &rdquo;' % allEntries[i]['formattedtitle']
    #             if 'journal' in allEntries[i].keys():
    #                 journal = ',&nbsp;<em>%s</em>&nbsp;' % (
    #                     allEntries[i]['journal'])
    #             if 'year' in allEntries[i].keys():
    #                 year = '<strong>%s</strong>,' % allEntries[i]['year']
    #             if 'volume' in allEntries[i].keys():
    #                 if 'number' in allEntries[i].keys():
    #                     volume = '<em>%s(%s)</em>' % (
    #                         allEntries[i]['volume'], allEntries[i]['number'])
    #                 else:
    #                     volume = '<em>%s</em>' % (allEntries[i]['volume'])
    #             elif 'number' in allEntries[i].keys():
    #                 number = '<em>%s</em>' % (allEntries[i]['number'])
    #             if 'pages' in allEntries[i].keys():
    #                 pages = ','+allEntries[i]['pages']
    #             if 'cited' in allEntries[i].keys():
    #                 cited = '<br><span class="cited">&nbsp;&nbsp;Cited: %s</span>' % allEntries[i]['cited']
    #             if 'impactfactor' in allEntries[i].keys():
    #                 impactFactor = '<span class="infact">(<strong>IF 2018: %s</strong>)</span><br>' % allEntries[
    #                     i]['impactfactor']
    #             if 'url' in allEntries[i].keys():
    #                 url = '''<a href="%s" target="_blank">%s</a>''' % (
    #                     allEntries[i]['url'], allEntries[i]['url'])

    #             tempHtml = hiho+image+formattedAuthor+formattedtTitle + \
    #                 journal+year+volume+number+pages+cited+impactFactor+url
    #             tempHtml = '<li style="padding:5px 0px">' + tempHtml + '</li>'
    #             top15ArticleBody = top15ArticleBody + tempHtml
    #     top15ArticleBody = '<ol>%s</ol>' % top15ArticleBody
    #     Top15Article = Top15Article + top15ArticleBody
    #     return Top15Article

    # def generateAricleHtml(bibFilePath):
    #     # 生成Articles部分,返回HTML
    #     parser = BibTexParser(common_strings=False)
    #     parser.ignore_nonstandard_types = False

    #     with open(bibFilePath, encoding='utf8') as bibtexFile:
    #         ircreDatabase = bibtexparser.load(bibtexFile, parser)

    #     allEntries = ircreDatabase.entries.copy()
    #     num = 0
    #     for i in range(len(allEntries)):
    #         if allEntries[i]['ENTRYTYPE'] == 'article':
    #             num += 1
    #     print(num)
    #     # article的初始值为 artile部分的信息
    #     # 包括article整体资料与标题
    #     article = '''
    #     <div id="articlestatics" style="margin-top:20px;margin-bottom:20px;">
    #         <h3 class="title">
    #             <strong><a id="articles"></a>Articles</a></strong>
    #             <span class="listcountred">(<span id="totalarticles">%s</span>)</span>
    #         </h3>

    #             <div>
    #                 <span class="index">h-index = </span><span class="index_number"><span
    #                         id="hindex">63</span></span><span class="index">, i10-index = </span><span
    #                     class="index_number"><span id="i10index">323</span></span><span class="index">,
    #                     Citations/Paper = </span><span class="index_number"><span
    #                         id="citationperpaper">31.92</span></span><span class="index">, Journals =
    #                 </span><span class="index_number"><span id="numberjournals">159</span></span><span
    #                     class="index">, Average IF = </span><span class="index_number"><span
    #                         id="averageif">6.724</span></span><span class="index">, ESI Highly Cited =
    #                 </span><span class="index_number"><span id="numberesihighlycited">26</span></span>
    #                 <br>
    #                 <span class="sorted">sorted by Impact Factor (2018 Journal Citation Reports®,
    #                     Clarivate Analytics), citations from Google Scholar, CrossRef, SciFinder,
    #                     Scopus...</span><br>
    #             </div>
    #         </div>''' % num
    #     articleBody = ''
    #     for i in range(len(allEntries)):
    #         tempHtml = ''
    #         hiho = ''
    #         image = ''
    #         formattedAuthor = ''
    #         formattedtTitle = ''
    #         journal = ''
    #         year = ''
    #         volume = ''
    #         number = ''
    #         pages = ''
    #         paperid = ''
    #         url = ''
    #         impactFactor = ''
    #         cited = ''
    #         if allEntries[i]['ENTRYTYPE'] == 'article':
    #             # keys = allEntries[i].keys()
    #             # 无法显示 hihoimage
    #             if 'hihoimage' in allEntries[i].keys():
    #                 hiho = '''
    #                 <div style=" height:40px; width:500px;text-align: left;"><img
    #             src="./images/articlecover/ISIHighlycitedlogo.jpg" alt="" width="77" height="31">
    #                 <a class="hiholinka" a href="./%s"
    #             target="_blank"><strong><em> %s</em></strong></a></div>
    #                 ''' % (allEntries[i]['hiholink'], allEntries[i]['hihosubject'])
    #             if 'image' in allEntries[i].keys():
    #                 if 'imagewidth' in allEntries[i].keys():
    #                     imagewidth = allEntries[i]['imagewidth']
    #                     if imagewidth == 'Beilstein Journal of Nanotechnology':
    #                         image = '''<span style="float: left; width: 190px;"><img class="bibtexVar" src="./images/articlecovers/%s" alt=""  width="184" height="22" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Nature Communications':
    #                         image = '''<span style="float: left; width: 108px;"><img class="bibtexVar" src="./images/articlecovers/%s" alt=""   width="102" height="32" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Physical Review B':
    #                         image = '''<span style="float: left; width: 102px;"><img class="bibtexVar" src="./images/articlecovers/%s" alt=""   width="96" height="32" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Scientific Reports':
    #                         image = '''<span style="float: left; width: 165px;"><img class="bibtexVar" src="./images/articlecovers/%s" alt=""   width="160" height="32" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                 else:
    #                     image = '''<span style="float: left; width: 48px;"><img class="bibtexVar" src="./images/articlecovers/%s" alt=""   width="42" height="51" text-align="left"></span> ''' % (
    #                         allEntries[i]['image'])
    #             if 'formattedauthor' in allEntries[i].keys():
    #                 formattedAuthor = allEntries[i]['formattedauthor']
    #             if 'formattedtitle' in allEntries[i].keys():
    #                 formattedtTitle = ',&ldquo;<strong>%s</strong> &rdquo;' % allEntries[i]['formattedtitle']
    #             if 'journal' in allEntries[i].keys():
    #                 journal = ',&nbsp;<em>%s</em>&nbsp;' % (
    #                     allEntries[i]['journal'])
    #             if 'year' in allEntries[i].keys():
    #                 year = '<strong>%s</strong>,' % allEntries[i]['year']
    #             if 'volume' in allEntries[i].keys():
    #                 if 'number' in allEntries[i].keys():
    #                     volume = '<em>%s(%s)</em>' % (
    #                         allEntries[i]['volume'], allEntries[i]['number'])
    #                 else:
    #                     volume = '<em>%s</em>' % (allEntries[i]['volume'])
    #             elif 'number' in allEntries[i].keys():
    #                 number = '<em>%s</em>' % (allEntries[i]['number'])
    #             if 'pages' in allEntries[i].keys():
    #                 pages = ','+allEntries[i]['pages']
    #             if 'cited' in allEntries[i].keys():
    #                 cited = '<br><span class="cited">&nbsp;&nbsp;Cited: %s</span>' % allEntries[i]['cited']
    #             if 'impactfactor' in allEntries[i].keys():
    #                 impactFactor = '<span class="infact">(<strong>IF 2018: %s</strong>)</span><br>' % allEntries[
    #                     i]['impactfactor']
    #             if 'url' in allEntries[i].keys():
    #                 url = '''<a href="%s" target="_blank" style="float: left">%s</a>''' % (
    #                     allEntries[i]['url'], allEntries[i]['url'])

    #             tempHtml = hiho + image + formattedAuthor + formattedtTitle + \
    #                 journal + year + volume + number + pages + cited + impactFactor + url
    #             tempHtml = '<li style="float: left;padding:5px 0px">' + tempHtml + '</li>'
    #             articleBody = articleBody + tempHtml
    #     articleBody = '<ol style="margin-top: 0px;padding-top:0px">%s</ol>' % articleBody
    #     article = article + articleBody
    #     return article

    # def generateBookHtml(bibFilePath):
    #     # 生成Articles部分,返回HTML
    #     parser = BibTexParser(common_strings=False)
    #     parser.ignore_nonstandard_types = False

    #     with open(bibFilePath, encoding='utf8') as bibtexFile:
    #         ircreDatabase = bibtexparser.load(bibtexFile, parser)

    #     allEntries = ircreDatabase.entries.copy()
    #     num = 0
    #     for i in range(len(allEntries)):
    #         if allEntries[i]['ENTRYTYPE'] == 'inbook':
    #             num += 1
    #     print(num)
    #     # article的初始值为 artile部分的信息
    #     # 包括article整体资料与标题
    #     book = '''
    #     <div id="bookchapters" style="margin-top:20px;margin-bottom:20px;">
    #         <h3 class="title">
    #             <strong><a id="articles"></a>Book Chapters</a></strong>
    #             <span class="listcountred">(<span id="totalarticles">%s</span>)</span>
    #         </h3>
    #         </div>''' % num
    #     bookBody = ''
    #     for i in range(len(allEntries)):
    #         tempHtml = ''
    #         hiho = ''
    #         image = ''
    #         formattedAuthor = ''
    #         formattedtTitle = ''
    #         journal = ''
    #         year = ''
    #         volume = ''
    #         number = ''
    #         pages = ''
    #         paperid = ''
    #         url = ''
    #         impactFactor = ''
    #         cited = ''
    #         if allEntries[i]['ENTRYTYPE'] == 'inbook':
    #             # keys = allEntries[i].keys()
    #             # 无法显示 hihoimage
    #             if 'hihoimage' in allEntries[i].keys():
    #                 hiho = '''
    #                 <div style=" height:40px; width:500px;text-align: left;"><img
    #             src="./images/articlecover/ISIHighlycitedlogo.jpg" alt="" width="77" height="31">
    #                 <a class="hiholinka" a href="./%s"
    #             target="_blank"><strong><em> %s</em></strong></a></div>
    #                 ''' % (allEntries[i]['hiholink'], allEntries[i]['hihosubject'])
    #             if 'image' in allEntries[i].keys():
    #                 if 'imagewidth' in allEntries[i].keys():
    #                     imagewidth = allEntries[i]['imagewidth']
    #                     if imagewidth == 'Beilstein Journal of Nanotechnology':
    #                         image = '''<span style="float: left; width: 190px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""  width="184" height="22" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Nature Communications':
    #                         image = '''<span style="float: left; width: 108px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="102" height="32" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Physical Review B':
    #                         image = '''<span style="float: left; width: 102px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="96" height="32" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Scientific Reports':
    #                         image = '''<span style="float: left; width: 165px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="160" height="32" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                 else:
    #                     image = '''<span style="float: left; width: 48px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="42" height="51" text-align="left"></span> ''' % (
    #                         allEntries[i]['image'])
    #             if 'formattedauthor' in allEntries[i].keys():
    #                 formattedAuthor = allEntries[i]['formattedauthor']
    #             if 'formattedtitle' in allEntries[i].keys():
    #                 formattedtTitle = ',&ldquo;<strong>%s</strong> &rdquo;' % allEntries[i]['formattedtitle']
    #             if 'journal' in allEntries[i].keys():
    #                 journal = ',&nbsp;<em>%s</em>&nbsp;' % (
    #                     allEntries[i]['journal'])
    #             if 'year' in allEntries[i].keys():
    #                 year = '<strong>%s</strong>,' % allEntries[i]['year']
    #             if 'volume' in allEntries[i].keys():
    #                 if 'number' in allEntries[i].keys():
    #                     volume = '<em>%s(%s)</em>' % (
    #                         allEntries[i]['volume'], allEntries[i]['number'])
    #                 else:
    #                     volume = '<em>%s</em>' % (allEntries[i]['volume'])
    #             elif 'number' in allEntries[i].keys():
    #                 number = '<em>%s</em>' % (allEntries[i]['number'])
    #             if 'pages' in allEntries[i].keys():
    #                 pages = ','+allEntries[i]['pages']
    #             if 'cited' in allEntries[i].keys():
    #                 cited = '<br><span class="cited">&nbsp;&nbsp;Cited: %s</span>' % allEntries[i]['cited']
    #             if 'impactfactor' in allEntries[i].keys():
    #                 impactFactor = '<span class="infact">(<strong>IF 2018: %s</strong>)</span><br>' % allEntries[
    #                     i]['impactfactor']
    #             if 'url' in allEntries[i].keys():
    #                 url = '''<a href="%s" target="_blank" style="float: left">%s</a>''' % (
    #                     allEntries[i]['url'], allEntries[i]['url'])

    #             tempHtml = hiho + image + formattedAuthor + formattedtTitle + \
    #                 journal + year + volume + number + pages + cited + impactFactor + url
    #             tempHtml = '<li style="float: left;padding:5px 0px">' + tempHtml + '</li>'
    #             bookBody = bookBody + tempHtml

    #     a = 0
    #     for i in range(len(allEntries)):
    #         if allEntries[i]['ENTRYTYPE'] == 'article':
    #             a += 1
    #     b = a+1
    #     bookBody = '<ol start=%s style="margin-top: 0px;padding-top:0px">%s</ol>' % (
    #         b, bookBody)
    #     book = book + bookBody
    #     return book

    # def generateProceedHtml(bibFilePath):
    #     # 生成Articles部分,返回HTML
    #     parser = BibTexParser(common_strings=False)
    #     parser.ignore_nonstandard_types = False

    #     with open(bibFilePath, encoding='utf8') as bibtexFile:
    #         ircreDatabase = bibtexparser.load(bibtexFile, parser)

    #     allEntries = ircreDatabase.entries.copy()
    #     num = 0
    #     for i in range(len(allEntries)):
    #         if allEntries[i]['ENTRYTYPE'] == 'inproceedings':
    #             num += 1
    #     print(num)
    #     # article的初始值为 artile部分的信息
    #     # 包括article整体资料与标题
    #     proceed = '''
    #     <div id="proceedings" style="margin-top:20px;margin-bottom:20px;">
    #         <h3 class="title">
    #             <strong><a id="articles"></a>Proceedings</a></strong>
    #             <span class="listcountred">(<span id="totalarticles">%s</span>)</span>
    #         </h3>
    #         </div>''' % num
    #     proceedBody = ''
    #     for i in range(len(allEntries)):
    #         tempHtml = ''
    #         hiho = ''
    #         image = ''
    #         formattedAuthor = ''
    #         formattedtTitle = ''
    #         journal = ''
    #         year = ''
    #         volume = ''
    #         number = ''
    #         pages = ''
    #         paperid = ''
    #         url = ''
    #         impactFactor = ''
    #         cited = ''
    #         if allEntries[i]['ENTRYTYPE'] == 'inproceedings':
    #             # keys = allEntries[i].keys()
    #             # 无法显示 hihoimage
    #             if 'hihoimage' in allEntries[i].keys():
    #                 hiho = '''
    #                 <div style=" height:40px; width:500px;text-align: left;"><img
    #             src="./images/articlecover/ISIHighlycitedlogo.jpg" alt="" width="77" height="31">
    #                 <a class="hiholinka" a href="./%s"
    #             target="_blank"><strong><em> %s</em></strong></a></div>
    #                 ''' % (allEntries[i]['hiholink'], allEntries[i]['hihosubject'])
    #             if 'image' in allEntries[i].keys():
    #                 if 'imagewidth' in allEntries[i].keys():
    #                     imagewidth = allEntries[i]['imagewidth']
    #                     if imagewidth == 'MRS Proceedings':
    #                         image = '''<span style="float: left; width: 156px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""  width="148" height="31" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Nature Communications':
    #                         image = '''<span style="float: left; width: 156px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="148" height="28" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Beilstein Journal of Nanotechnology':
    #                         image = '''<span style="float: left; width: 190px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""  width="184" height="22" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Nature Communications':
    #                         image = '''<span style="float: left; width: 108px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="102" height="32" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Physical Review B':
    #                         image = '''<span style="float: left; width: 102px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="96" height="32" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Scientific Reports':
    #                         image = '''<span style="float: left; width: 165px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="160" height="32" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                 else:
    #                     image = '''<span style="float: left; width: 48px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="42" height="51" text-align="left"></span> ''' % (
    #                         allEntries[i]['image'])
    #             if 'formattedauthor' in allEntries[i].keys():
    #                 formattedAuthor = allEntries[i]['formattedauthor']
    #             if 'formattedtitle' in allEntries[i].keys():
    #                 formattedtTitle = ',&ldquo;<strong>%s</strong> &rdquo;' % allEntries[i]['formattedtitle']
    #             if 'journal' in allEntries[i].keys():
    #                 journal = ',&nbsp;<em>%s</em>&nbsp;' % (
    #                     allEntries[i]['journal'])
    #             if 'year' in allEntries[i].keys():
    #                 year = '<strong>%s</strong>,' % allEntries[i]['year']
    #             if 'volume' in allEntries[i].keys():
    #                 if 'number' in allEntries[i].keys():
    #                     volume = '<em>%s(%s)</em>' % (
    #                         allEntries[i]['volume'], allEntries[i]['number'])
    #                 else:
    #                     volume = '<em>%s</em>' % (allEntries[i]['volume'])
    #             elif 'number' in allEntries[i].keys():
    #                 number = '<em>%s</em>' % (allEntries[i]['number'])
    #             if 'pages' in allEntries[i].keys():
    #                 pages = ','+allEntries[i]['pages']
    #             if 'cited' in allEntries[i].keys():
    #                 cited = '<br><span class="cited">&nbsp;&nbsp;Cited: %s</span>' % allEntries[i]['cited']
    #             if 'impactfactor' in allEntries[i].keys():
    #                 impactFactor = '<span class="infact">(<strong>IF 2018: %s</strong>)</span><br>' % allEntries[
    #                     i]['impactfactor']
    #             if 'url' in allEntries[i].keys():
    #                 url = '''<a href="%s" target="_blank" style="float: left">%s</a>''' % (
    #                     allEntries[i]['url'], allEntries[i]['url'])

    #             tempHtml = hiho + image + formattedAuthor + formattedtTitle + \
    #                 journal + year + volume + number + pages + cited + impactFactor + url
    #             tempHtml = '<li style="float: left;padding:5px 0px">' + tempHtml + '</li>'
    #             proceedBody = proceedBody + tempHtml
    #     a = 0
    #     for i in range(len(allEntries)):
    #         if allEntries[i]['ENTRYTYPE'] == 'article':
    #             a += 1
    #     b = 0
    #     for i in range(len(allEntries)):
    #         if allEntries[i]['ENTRYTYPE'] == 'inbook':
    #             b += 1
    #     c = a+b+1
    #     proceedBody = '<ol start=%s style="margin-top: 0px;padding-top:0px">%s</ol>' % (
    #         c, proceedBody)
    #     proceed = proceed + proceedBody
    #     return proceed

    # def generateEditorialsHtml(bibFilePath):
    #     # 生成Articles部分,返回HTML
    #     parser = BibTexParser(common_strings=False)
    #     parser.ignore_nonstandard_types = False

    #     with open(bibFilePath, encoding='utf8') as bibtexFile:
    #         ircreDatabase = bibtexparser.load(bibtexFile, parser)

    #     allEntries = ircreDatabase.entries.copy()
    #     num = 0
    #     for i in range(len(allEntries)):
    #         if allEntries[i]['ENTRYTYPE'] == 'incollection':
    #             num += 1
    #     print(num)
    #     # article的初始值为 artile部分的信息
    #     # 包括article整体资料与标题
    #     editorials = '''
    #     <div id="editorials" style="margin-top:20px;margin-bottom:20px;">
    #         <h3 class="title">
    #             <strong><a id="articles"></a>Editorials</a></strong>
    #             <span class="listcountred">(<span id="totalarticles">%s</span>)</span>
    #         </h3>
    #         </div>''' % num
    #     editorialsBody = ''
    #     for i in range(len(allEntries)):
    #         tempHtml = ''
    #         hiho = ''
    #         image = ''
    #         formattedAuthor = ''
    #         formattedtTitle = ''
    #         journal = ''
    #         year = ''
    #         volume = ''
    #         number = ''
    #         pages = ''
    #         paperid = ''
    #         url = ''
    #         impactFactor = ''
    #         cited = ''
    #         if allEntries[i]['ENTRYTYPE'] == 'incollection':
    #             # keys = allEntries[i].keys()
    #             # 无法显示 hihoimage
    #             if 'hihoimage' in allEntries[i].keys():
    #                 hiho = '''
    #                 <div style=" height:40px; width:500px;text-align: left;"><img
    #             src="./images/articlecover/ISIHighlycitedlogo.jpg" alt="" width="77" height="31">
    #                 <a class="hiholinka" a href="./%s"
    #             target="_blank"><strong><em> %s</em></strong></a></div>
    #                 ''' % (allEntries[i]['hiholink'], allEntries[i]['hihosubject'])
    #             if 'image' in allEntries[i].keys():
    #                 if 'imagewidth' in allEntries[i].keys():
    #                     imagewidth = allEntries[i]['imagewidth']
    #                     if imagewidth == 'The Scientific World Journal':
    #                         image = '''<span style="float: left; width: 138px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""  width="132" height="50" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'MRS Proceedings':
    #                         image = '''<span style="float: left; width: 156px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""  width="148" height="31" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Nature Communications':
    #                         image = '''<span style="float: left; width: 156px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="148" height="28" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Beilstein Journal of Nanotechnology':
    #                         image = '''<span style="float: left; width: 190px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""  width="184" height="22" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Nature Communications':
    #                         image = '''<span style="float: left; width: 108px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="102" height="32" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Physical Review B':
    #                         image = '''<span style="float: left; width: 102px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="96" height="32" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                     if imagewidth == 'Scientific Reports':
    #                         image = '''<span style="float: left; width: 165px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="160" height="32" text-align="left"></span> ''' % (
    #                             allEntries[i]['image'])
    #                 else:
    #                     image = '''<span style="float: left; width: 48px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="42" height="51" text-align="left"></span> ''' % (
    #                         allEntries[i]['image'])
    #             if 'formattedauthor' in allEntries[i].keys():
    #                 formattedAuthor = allEntries[i]['formattedauthor']
    #             if 'formattedtitle' in allEntries[i].keys():
    #                 formattedtTitle = ',&ldquo;<strong>%s</strong> &rdquo;' % allEntries[i]['formattedtitle']
    #             if 'journal' in allEntries[i].keys():
    #                 journal = ',&nbsp;<em>%s</em>&nbsp;' % (
    #                     allEntries[i]['journal'])
    #             if 'year' in allEntries[i].keys():
    #                 year = '<strong>%s</strong>,' % allEntries[i]['year']
    #             if 'volume' in allEntries[i].keys():
    #                 if 'number' in allEntries[i].keys():
    #                     volume = '<em>%s(%s)</em>' % (
    #                         allEntries[i]['volume'], allEntries[i]['number'])
    #                 else:
    #                     volume = '<em>%s</em>' % (allEntries[i]['volume'])
    #             elif 'number' in allEntries[i].keys():
    #                 number = '<em>%s</em>' % (allEntries[i]['number'])
    #             if 'pages' in allEntries[i].keys():
    #                 pages = ','+allEntries[i]['pages']
    #             if 'cited' in allEntries[i].keys():
    #                 cited = '<br><span class="cited">&nbsp;&nbsp;Cited: %s</span>' % allEntries[i]['cited']
    #             if 'impactfactor' in allEntries[i].keys():
    #                 impactFactor = '<span class="infact">(<strong>IF 2018: %s</strong>)</span><br>' % allEntries[
    #                     i]['impactfactor']
    #             if 'url' in allEntries[i].keys():
    #                 url = '''<a href="%s" target="_blank" style="float: left">%s</a>''' % (
    #                     allEntries[i]['url'], allEntries[i]['url'])

    #             tempHtml = hiho + image + formattedAuthor + formattedtTitle + \
    #                 journal + year + volume + number + pages + cited + impactFactor + url
    #             tempHtml = '<li style="float: left;padding:5px 0px">' + tempHtml + '</li>'
    #             editorialsBody = editorialsBody + tempHtml
    #     a = 0
    #     for i in range(len(allEntries)):
    #         if allEntries[i]['ENTRYTYPE'] == 'article':
    #             a += 1
    #     b = 0
    #     for i in range(len(allEntries)):
    #         if allEntries[i]['ENTRYTYPE'] == 'inbook':
    #             b += 1
    #     c = 0
    #     for i in range(len(allEntries)):
    #         if allEntries[i]['ENTRYTYPE'] == 'inproceedings':
    #             c += 1
    #     d = a+b+c+1
    #     editorialsBody = '<ol start=%s style="margin-top: 0px;padding-top:0px">%s</ol>' % (
    #         d, editorialsBody)
    #     editorials = editorials + editorialsBody
    #     return editorials
    resulthtml = before_output + after_output
    with open(researchnew_html_path, 'w', encoding='utf8') as htmlfile:
        htmlfile.write(resulthtml)

    return resulthtml


def main():
    # openproxy()

    # 从网站目录复制bib文件
    # bibtexfilecopy()

    # 分类，分成article.bib, bookchapter.bib, ...
    bibtexclassify()

    # entryadd()

    # getclusterid()

    # 更新引用次数
    # getcitation()

    # 按影响因子和引用次数对article排序，并取出top 15 most cited articles，
    articlessort()

    getop15articles()

    # 合并文件
    ircrebibmerge()

    # updatestatistics()

    generatehtml()

    # filecopyback()

    return 0


def getcitation():
    articlesparser = BibTexParser(common_strings=False)
    articlesparser.ignore_nonstandard_types = False
    with open('../bib7image/articles.bib', encoding='utf8') as articlesfile:
        articles_database = bibtexparser.load(articlesfile, articlesparser)

    articleentries = articles_database.entries

    import random
    samplelist = random.sample(range(len(articleentries)), 20)
    print(samplelist)

    for i in samplelist:
        print("---------------------------")
        print("Entry number: " + str(i))
        title = articleentries[i]['title']
        clusterid = articleentries[i]['clusterid']
        print("Title: " + title)
        print("Cluster ID: " + clusterid)

        if not clusterid == "unknown":
            print(str(i))
            try:
                citations = os.popen(
                    '''/usr/bin/python3 /home/limingtao/ircre-bibtex/ircreupdate/scholarpy/scholar.py -c 1 -C ''' + clusterid + ''' |grep -v list |grep Citations''').read().strip().split()[
                    -1]
            except:
                citations = "unknown"
        else:
            citations = "unknown"

        print("new Citations: " + citations)

        if 'cited' in articleentries[i]:
            oldcitednumber = int(articleentries[i]['cited'])
        else:
            oldcitednumber = 0

        print("Old Cited Number: " + str(oldcitednumber))

        if not citations == "unknown":
            citednumber = int(citations)
            if citednumber > oldcitednumber and ((citednumber - oldcitednumber) < 8):
                articleentries[i]['cited'] = str(citednumber)

        writer = BibTexWriter()
        writer.indent = '    '
        writer.order_entries_by = ('order',)

        with open('/home/limingtao/ircre-bibtex/ircreupdate/cited-add-articles.bib', 'w', encoding='utf8') as newarticlefile:
            bibtexparser.dump(articles_database, newarticlefile, writer=writer)

        os.popen(
            "cp /home/limingtao/ircre-bibtex/ircreupdate/cited-add-articles.bib tempcited-add-articles.bib")

    os.popen("cp /home/limingtao/ircre-bibtex/ircreupdate/articles.bib /home/limingtao/ircre-bibtex/ircreupdate/oldarticles.bib")
    with open('/home/limingtao/ircre-bibtex/ircreupdate/articles.bib', 'w', encoding='utf8') as newarticlefile:
        bibtexparser.dump(articles_database, newarticlefile, writer=writer)

    return 0


def entryadd(doi):
    pass


def openproxy():
    try:
        sshid = os.popen(
            '''ps aux | grep 9524| grep ssh''').read().strip().split()[1]
    except:
        sshid = None
    if sshid is not None:
        os.system('''kill ''' + sshid)
    os.system('''/home/limingtao/bin/proxy.sh''')
    return 0


def bibtexfilecopy():
    dt = datetime.now()
    ircrebibwebsitefile = '/srv/main-websites/ircre/js/ircre.bib'
    ircrestatwebsitefile = '/srv/main-websites/ircre/js/statistics.js'
    currentdir = '/home/limingtao/ircre-bibtex/ircreupdate'
    os.system(
        '''cd ''' + currentdir + ''';''' +
        '''cp ''' + ircrebibwebsitefile + ''' ''' +
        currentdir + '''/ -f ; cp ircre.bib ircre'''
        + str(dt.year) + str(dt.month) + str(dt.day) + '''.bib;''')
    os.system(
        '''cd ''' + currentdir + ''';''' +
        '''cp ''' + ircrestatwebsitefile + ''' ''' +
        currentdir + '''/ -f ; cp statistics.js statistics'''
        + str(dt.year) + str(dt.month) + str(dt.day) + '''.js;''')
    return 0


def getclusterid(title, author):
    parser = BibTexParser(common_strings=False)
    parser.ignore_nonstandard_types = False

    with open('../bib7image/articles.bib', encoding='utf8') as article_file:
        article_database = bibtexparser.load(article_file, parser)

    article_entries = article_database.entries.copy()

    entries = bib_database.entries
    print("---------------------------")
    print("---------------------------")
    print("---------------------------")
    print("Total articles number: " + str(len(entries)))
    print("---------------------------")
    print("---------------------------")
    print("---------------------------")

    writer = BibTexWriter()
    writer.indent = '    '
    writer.order_entries_by = ('order',)

    for i in range(len(entries)):
        if entries[i]['clusterid'] == 'unknown':
            print("---------------------------")
            print("Entry number: " + str(i))
            title = entries[i]['title']
            print("Title: " + title)
            clusterid = ''
            try:
                clusterid = os.popen(
                    '''/home/limingtao/ircre-bibtex/ircreupdate/scholarpy/scholar.py -c 1 -t --phrase="''' + title + '''" |grep ID| grep Cluster''').read().strip().split()[
                    -1]
            except:
                clusterid = "unknown"

            print("new Cluster ID: " + clusterid)
            entries[i]['clusterid'] = clusterid
        with open('/home/limingtao/ircre-bibtex/ircreupdate/clusterid-added-ircre.bib', 'w', encoding='utf8') as newbibfile:
            bibtexparser.dump(bib_database, newbibfile, writer=writer)
        os.popen("cp /home/limingtao/ircre-bibtex/ircreupdate/clusterid-added-ircre.bib /home/limingtao/ircre-bibtex/ircreupdate/tempclusterid-added-ircre.bib")

    with open('/home/limingtao/ircre-bibtex/ircreupdate/clusterid-added-ircre.bib', 'w', encoding='utf8') as newbibfile:
        bibtexparser.dump(bib_database, newbibfile, writer=writer)

    return 0


if __name__ == '__main__':
    sys.exit(main())
