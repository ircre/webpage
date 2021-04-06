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
    # totalcitations = totalcitations + 19
    citationperpaper = totalcitations / len(articleentries)
    citationperpaper = round(citationperpaper, 2)
    journalnumber = len(set(jourallist))
    averageif = totalif / len(articleentries)
    averageif = round(averageif, 3)
    return (totalarticles, totalcitations, hindex, i10index,  citationperpaper, journalnumber, averageif, hihonumber)


def getsothers():
    othersparser = BibTexParser(common_strings=False)
    othersparser.ignore_nonstandard_types = False
    with open(others_bib_path, encoding='utf8') as othersfile:
        others_database = bibtexparser.load(othersfile, othersparser)

    othersentries = others_database.entries
    totalbooks = 0
    totalproceeds = 0
    totaleditors = 0
    totalcitations = 0
    for i in range(len(othersentries)):
        if othersentries[i]['ENTRYTYPE'] == 'inbook':
            totalbooks += 1
        if othersentries[i]['ENTRYTYPE'] == 'inproceedings':
            totalproceeds += 1
        if othersentries[i]['ENTRYTYPE'] == 'incollection':
            totaleditors += 1
        if 'cited' in othersentries[i]:
            citednumber = int(othersentries[i]['cited'])
        else:
            citednumber = 0
        totalcitations = totalcitations + citednumber
    # totalcitations = totalcitations + 19
    return (totalbooks, totalcitations, totalproceeds, totaleditors)


def generateTop15ArtitleHtml(bibFilePath):
    # 生成TOP15Articles部分,返回HTML
    parser = BibTexParser(common_strings=False)
    parser.ignore_nonstandard_types = False

    with open(bibFilePath, encoding='utf8') as bibtexFile:
        ircreDatabase = bibtexparser.load(bibtexFile, parser)

    allEntries = ircreDatabase.entries.copy()

    (totalarticles, articaltotalcitations, hindex, i10index,
     citationperpaper, journalnumber, averageif, hihonumber) = getstatistics()
    (totalbooks, othertotalcitations, totalproceeds, totaleditors) = getsothers()
    allnumber = totalarticles+totalbooks+totalproceeds+totaleditors
    allcitations = articaltotalcitations+othertotalcitations
    # 初始值为TOP15article的标题
    Top15Article = '''
    <div id="output">
        <div id="total-statistics">
            <h2>IRCRE Scientific Output</h2>
            <h3><span class="listcountred"><span id="totalpublications">'''+str(allnumber)+'''</span>+</span><strong>Publications
                &amp; </strong><span class="listcountblue"><span id="totalcitations">'''+str(allcitations)+'''</span>+</span> <strong>Citations since
                2011</strong>
            </h3>
        </div>
    <div id="top15mostcitedarticles">
                    <h3>
                        <strong>Top 15 Most Cited Articles</strong>
                    </h3></div>
    '''
    top15ArticleBody = ''
    for i in range(len(allEntries)):
        tempHtml = ''

        hiho = ''
        image = ''
        formattedAuthor = ''
        formattedtTitle = ''
        journal = ''
        year = ''
        volume = ''
        number = ''
        pages = ''
        paperid = ''
        url = ''
        impactFactor = ''
        cited = ''
        if allEntries[i]['ENTRYTYPE'] == 'toparticle':
            # keys = allEntries[i].keys()
            # 无法显示 hihoimage
            if 'hihoimage' in allEntries[i].keys():
                hiho = '''
                <div style="float:inherit; height:40px; width:500px;text-align: left;"><img
            src="./images/articlecover/ISIHighlycitedlogo.jpg" alt="" width="77" height="31">
                <a class="newlink" a href="./%s"
            target="_blank"><strong><em> %s</em></strong></a></div>
                ''' % (allEntries[i]['hiholink'], allEntries[i]['hihosubject'])
            if 'image' in allEntries[i].keys():
                image = '''<span style="float: left; width: 48px; height: 54px;"><img src="./images/articlecovers/%s" alt="" width="42" height="51"></span> ''' % (
                    allEntries[i]['image'])
            if 'formattedauthor' in allEntries[i].keys():
                formattedAuthor = allEntries[i]['formattedauthor']
            if 'formattedtitle' in allEntries[i].keys():
                formattedtTitle = ',&ldquo;<strong>%s</strong> &rdquo;' % allEntries[i]['formattedtitle']
            if 'journal' in allEntries[i].keys():
                journal = ',&nbsp;<em>%s</em>&nbsp;' % (
                    allEntries[i]['journal'])
            if 'year' in allEntries[i].keys():
                year = '<strong>%s</strong>,' % allEntries[i]['year']
            if 'volume' in allEntries[i].keys():
                if 'number' in allEntries[i].keys():
                    volume = '<em>%s(%s)</em>' % (
                        allEntries[i]['volume'], allEntries[i]['number'])
                else:
                    volume = '<em>%s</em>' % (allEntries[i]['volume'])
            elif 'number' in allEntries[i].keys():
                number = '<em>%s</em>' % (allEntries[i]['number'])
            if 'pages' in allEntries[i].keys():
                pages = ',' + allEntries[i]['pages']
            if 'cited' in allEntries[i].keys():
                if allEntries[i]['cited'] != '0':
                    cited = '<br><span class="cited">&nbsp;&nbsp;Cited: %s</span>' % allEntries[i]['cited']
                else:
                    cited = '<br><span class="cited" style="display:none">&nbsp;&nbsp;Cited: %s</span>' % allEntries[i]['cited']
            if 'impactfactor' in allEntries[i].keys():
                if 'impactfactoryear' not in allEntries[i].keys():
                    impactFactor = '<span class="infact">(<strong>IF 2019: %s</strong>)</span><br>' % allEntries[i]['impactfactor']
                else:
                    impactFactor = '<span class="infact">(<strong>IF %s %s</strong>)</span><br>' % (allEntries[i]['impactfactoryear'],allEntries[i]['impactfactor'])
            if 'url' in allEntries[i].keys():
                url = '''<a href="%s" target="_blank">%s</a>''' % (
                    allEntries[i]['url'], allEntries[i]['url'])

            tempHtml = hiho + image + formattedAuthor + formattedtTitle + \
                journal + year + volume + number + pages + cited + impactFactor + url
            tempHtml = '<li style="padding:5px 0px">' + tempHtml + '</li>'
            top15ArticleBody = top15ArticleBody + tempHtml
    top15ArticleBody = '<ol>%s</ol>' % top15ArticleBody
    Top15Article = Top15Article + top15ArticleBody
    return Top15Article


def generateAricleHtml(bibFilePath):
    # 生成Articles部分,返回HTML
    parser = BibTexParser(common_strings=False)
    parser.ignore_nonstandard_types = False

    with open(bibFilePath, encoding='utf8') as bibtexFile:
        ircreDatabase = bibtexparser.load(bibtexFile, parser)

    allEntries = ircreDatabase.entries.copy()
    (totalarticles, articaltotalcitations, hindex, i10index,
     citationperpaper, journalnumber, averageif, hihonumber) = getstatistics()
    # article的初始值为 artile部分的信息
    # 包括article整体资料与标题
    article = '''
        <div id="articlestatics" style="margin-top:20px;margin-bottom:20px;">
            <h3 class="title">
                <strong><a id="articles"></a>Articles</a></strong>
                <span class="listcountred">(<span id="totalarticles">'''+str(totalarticles)+'''</span>)</span>
            </h3>

                <div>
                    <span class="index">h-index = </span><span class="index_number"><span
                            id="hindex">'''+str(hindex)+'''</span></span><span class="index">, i10-index = </span><span
                        class="index_number"><span id="i10index">'''+str(i10index)+'''</span></span><span class="index">,
                        Citations/Paper = </span><span class="index_number"><span
                            id="citationperpaper">'''+str(citationperpaper)+'''</span></span><span class="index">, Journals =
                    </span><span class="index_number"><span id="numberjournals">'''+str(journalnumber)+'''</span></span><span
                        class="index">, Average IF = </span><span class="index_number"><span
                            id="averageif">'''+str(averageif)+'''</span></span><span class="index">, ESI Highly Cited =
                    </span><span class="index_number"><span id="numberesihighlycited">'''+str(hihonumber)+'''</span></span>
                    <br>
                    <span class="sorted">sorted by Impact Factor (2018 Journal Citation Reports®,
                        Clarivate Analytics), citations from Google Scholar, CrossRef, SciFinder,
                        Scopus...</span><br>
                </div>
            </div>'''
    articleBody = ''
    for i in range(len(allEntries)):
        tempHtml = ''
        hiho = ''
        image = ''
        formattedAuthor = ''
        formattedtTitle = ''
        journal = ''
        year = ''
        volume = ''
        number = ''
        pages = ''
        paperid = ''
        url = ''
        impactFactor = ''
        cited = ''
        if allEntries[i]['ENTRYTYPE'] == 'article':
            # keys = allEntries[i].keys()
            # 无法显示 hihoimage
            if 'hihoimage' in allEntries[i].keys():
                hiho = '''
                    <div style=" height:40px; width:500px;text-align: left;"><img
                src="./images/articlecover/ISIHighlycitedlogo.jpg" alt="" width="77" height="31">
                    <a class="hiholinka" a href="./%s"
                target="_blank"><strong><em> %s</em></strong></a></div>
                    ''' % (allEntries[i]['hiholink'], allEntries[i]['hihosubject'])
            if 'image' in allEntries[i].keys():
                if 'imagewidth' in allEntries[i].keys():
                    imagewidth = allEntries[i]['imagewidth']
                    if imagewidth == 'Beilstein Journal of Nanotechnology':
                        image = '''<span style="float: left; width: 190px;"><img class="bibtexVar" src="./images/articlecovers/%s" alt=""  width="184" height="22" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Nature Communications':
                        image = '''<span style="float: left; width: 108px;"><img class="bibtexVar" src="./images/articlecovers/%s" alt=""   width="102" height="32" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Physical Review B':
                        image = '''<span style="float: left; width: 102px;"><img class="bibtexVar" src="./images/articlecovers/%s" alt=""   width="96" height="32" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Scientific Reports':
                        image = '''<span style="float: left; width: 165px;"><img class="bibtexVar" src="./images/articlecovers/%s" alt=""   width="160" height="32" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'EcoMat':
                        image = '''<span style="float: left; width: 155px;"><img class="bibtexVar" src="./images/articlecovers/%s" alt=""   width="148" height="28" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                else:
                    image = '''<span style="float: left; width: 48px;"><img class="bibtexVar" src="./images/articlecovers/%s" alt=""   width="42" height="51" text-align="left"></span> ''' % (
                        allEntries[i]['image'])
            if 'formattedauthor' in allEntries[i].keys():
                formattedAuthor = allEntries[i]['formattedauthor']
            if 'formattedtitle' in allEntries[i].keys():
                formattedtTitle = ',&ldquo;<strong>%s</strong> &rdquo;' % allEntries[i]['formattedtitle']
            if 'journal' in allEntries[i].keys():
                journal = ',&nbsp;<em>%s</em>&nbsp;' % (
                    allEntries[i]['journal'])
            if 'year' in allEntries[i].keys():
                year = '<strong>%s</strong>,' % allEntries[i]['year']
            if 'volume' in allEntries[i].keys():
                if 'number' in allEntries[i].keys():
                    volume = '<em>%s(%s)</em>' % (
                        allEntries[i]['volume'], allEntries[i]['number'])
                else:
                    volume = '<em>%s</em>' % (allEntries[i]['volume'])
            elif 'number' in allEntries[i].keys():
                number = '<em>%s</em>' % (allEntries[i]['number'])
            if 'pages' in allEntries[i].keys():
                pages = ','+allEntries[i]['pages']
            if 'cited' in allEntries[i].keys():
                if allEntries[i]['cited'] != '0':
                    cited = '<br><span class="cited">&nbsp;&nbsp;Cited: %s</span>' % allEntries[i]['cited']
                else:
                    cited = '<br><span class="cited" style="display:none">&nbsp;&nbsp;Cited: %s</span>' % allEntries[i]['cited']
            if 'impactfactor' in allEntries[i].keys():
                if 'impactfactoryear' not in allEntries[i].keys():
                    impactFactor = '<span class="infact">(<strong>IF 2019: %s</strong>)</span><br>' % allEntries[i]['impactfactor']
                else:
                    impactFactor = '<span class="infact">(<strong>IF %s %s</strong>)</span><br>' % (allEntries[i]['impactfactoryear'],allEntries[i]['impactfactor'])
            if 'url' in allEntries[i].keys():
                url = '''<a href="%s" target="_blank" style="float: left">%s</a>''' % (
                    allEntries[i]['url'], allEntries[i]['url'])

            tempHtml = hiho + image + formattedAuthor + formattedtTitle + \
                journal + year + volume + number + pages + cited + impactFactor + url
            tempHtml = '<li style="float: left;padding:5px 0px">' + tempHtml + '</li>'
            articleBody = articleBody + tempHtml
    articleBody = '<ol style="margin-top: 0px;padding-top:0px">%s</ol>' % articleBody
    article = article + articleBody
    return article


def generateBookHtml(bibFilePath):
    # 生成Articles部分,返回HTML
    parser = BibTexParser(common_strings=False)
    parser.ignore_nonstandard_types = False

    with open(bibFilePath, encoding='utf8') as bibtexFile:
        ircreDatabase = bibtexparser.load(bibtexFile, parser)

    allEntries = ircreDatabase.entries.copy()
    (totalbooks, othertotalcitations, totalproceeds, totaleditors) = getsothers()
    # article的初始值为 artile部分的信息
    # 包括article整体资料与标题
    book = '''
        <div id="bookchapters" style="margin-top:20px;margin-bottom:20px;">
            <h3 class="title">
                <strong><a id="articles"></a>Book Chapters</a></strong>
                <span class="listcountred">(<span id="totalarticles">'''+str(totalbooks)+'''</span>)</span>
            </h3>
            </div>'''
    bookBody = ''
    for i in range(len(allEntries)):
        tempHtml = ''
        hiho = ''
        image = ''
        formattedAuthor = ''
        formattedtTitle = ''
        journal = ''
        year = ''
        volume = ''
        number = ''
        pages = ''
        paperid = ''
        url = ''
        impactFactor = ''
        cited = ''
        if allEntries[i]['ENTRYTYPE'] == 'inbook':
            # keys = allEntries[i].keys()
            # 无法显示 hihoimage
            if 'hihoimage' in allEntries[i].keys():
                hiho = '''
                    <div style=" height:40px; width:500px;text-align: left;"><img
                src="./images/articlecover/ISIHighlycitedlogo.jpg" alt="" width="77" height="31">
                    <a class="hiholinka" a href="./%s"
                target="_blank"><strong><em> %s</em></strong></a></div>
                    ''' % (allEntries[i]['hiholink'], allEntries[i]['hihosubject'])
            if 'image' in allEntries[i].keys():
                if 'imagewidth' in allEntries[i].keys():
                    imagewidth = allEntries[i]['imagewidth']
                    if imagewidth == 'Beilstein Journal of Nanotechnology':
                        image = '''<span style="float: left; width: 190px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""  width="184" height="22" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Nature Communications':
                        image = '''<span style="float: left; width: 108px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="102" height="32" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Physical Review B':
                        image = '''<span style="float: left; width: 102px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="96" height="32" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Scientific Reports':
                        image = '''<span style="float: left; width: 165px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="160" height="32" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                else:
                    image = '''<span style="float: left; width: 48px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="42" height="51" text-align="left"></span> ''' % (
                        allEntries[i]['image'])
            if 'formattedauthor' in allEntries[i].keys():
                formattedAuthor = allEntries[i]['formattedauthor']
            if 'formattedtitle' in allEntries[i].keys():
                formattedtTitle = ',&ldquo;<strong>%s</strong> &rdquo;' % allEntries[i]['formattedtitle']
            if 'journal' in allEntries[i].keys():
                journal = ',&nbsp;<em>%s</em>&nbsp;' % (
                    allEntries[i]['journal'])
            if 'year' in allEntries[i].keys():
                year = '<strong>%s</strong>,' % allEntries[i]['year']
            if 'volume' in allEntries[i].keys():
                if 'number' in allEntries[i].keys():
                    volume = '<em>%s(%s)</em>' % (
                        allEntries[i]['volume'], allEntries[i]['number'])
                else:
                    volume = '<em>%s</em>' % (allEntries[i]['volume'])
            elif 'number' in allEntries[i].keys():
                number = '<em>%s</em>' % (allEntries[i]['number'])
            if 'pages' in allEntries[i].keys():
                pages = ','+allEntries[i]['pages']
            if 'cited' in allEntries[i].keys():
                if allEntries[i]['cited'] != '0':
                    cited = '<br><span class="cited">&nbsp;&nbsp;Cited: %s</span>' % allEntries[i]['cited']
                else:
                    cited = '<br><span class="cited" style="display:none">&nbsp;&nbsp;Cited: %s</span>' % allEntries[i]['cited']
            if 'impactfactor' in allEntries[i].keys():
                if 'impactfactoryear' not in allEntries[i].keys():
                    impactFactor = '<span class="infact">(<strong>IF 2019: %s</strong>)</span><br>' % allEntries[i]['impactfactor']
                else:
                    impactFactor = '<span class="infact">(<strong>IF %s %s</strong>)</span><br>' % (allEntries[i]['impactfactoryear'],allEntries[i]['impactfactor'])
            if 'url' in allEntries[i].keys():
                url = '''<a href="%s" target="_blank" style="float: left">%s</a>''' % (
                    allEntries[i]['url'], allEntries[i]['url'])

            tempHtml = hiho + image + formattedAuthor + formattedtTitle + \
                journal + year + volume + number + pages + cited + impactFactor + url
            tempHtml = '<li style="float: left;padding:5px 0px">' + tempHtml + '</li>'
            bookBody = bookBody + tempHtml

    (totalarticles, articaltotalcitations, hindex, i10index,
     citationperpaper, journalnumber, averageif, hihonumber) = getstatistics()
    b = totalarticles+1
    bookBody = '<ol start=%s style="margin-top: 0px;padding-top:0px">%s</ol>' % (
        b, bookBody)
    book = book + bookBody
    return book


def generateProceedHtml(bibFilePath):
    # 生成Articles部分,返回HTML
    parser = BibTexParser(common_strings=False)
    parser.ignore_nonstandard_types = False

    with open(bibFilePath, encoding='utf8') as bibtexFile:
        ircreDatabase = bibtexparser.load(bibtexFile, parser)

    allEntries = ircreDatabase.entries.copy()
    (totalbooks, othertotalcitations, totalproceeds, totaleditors) = getsothers()
    # article的初始值为 artile部分的信息
    # 包括article整体资料与标题
    proceed = '''
        <div id="proceedings" style="margin-top:20px;margin-bottom:20px;">
            <h3 class="title">
                <strong><a id="articles"></a>Proceedings</a></strong>
                <span class="listcountred">(<span id="totalarticles">'''+str(totalproceeds)+'''</span>)</span>
            </h3>
            </div>'''
    proceedBody = ''
    for i in range(len(allEntries)):
        tempHtml = ''
        hiho = ''
        image = ''
        formattedAuthor = ''
        formattedtTitle = ''
        journal = ''
        year = ''
        volume = ''
        number = ''
        pages = ''
        paperid = ''
        url = ''
        impactFactor = ''
        cited = ''
        if allEntries[i]['ENTRYTYPE'] == 'inproceedings':
            # keys = allEntries[i].keys()
            # 无法显示 hihoimage
            if 'hihoimage' in allEntries[i].keys():
                hiho = '''
                    <div style=" height:40px; width:500px;text-align: left;"><img
                src="./images/articlecover/ISIHighlycitedlogo.jpg" alt="" width="77" height="31">
                    <a class="hiholinka" a href="./%s"
                target="_blank"><strong><em> %s</em></strong></a></div>
                    ''' % (allEntries[i]['hiholink'], allEntries[i]['hihosubject'])
            if 'image' in allEntries[i].keys():
                if 'imagewidth' in allEntries[i].keys():
                    imagewidth = allEntries[i]['imagewidth']
                    if imagewidth == 'MRS Proceedings':
                        image = '''<span style="float: left; width: 156px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""  width="148" height="31" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Proceedings of the American Chemical Society':
                        image = '''<span style="float: left; width: 155px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""  width="148" height="28" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Nature Communications':
                        image = '''<span style="float: left; width: 156px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="148" height="28" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Beilstein Journal of Nanotechnology':
                        image = '''<span style="float: left; width: 190px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""  width="184" height="22" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Nature Communications':
                        image = '''<span style="float: left; width: 108px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="102" height="32" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Physical Review B':
                        image = '''<span style="float: left; width: 102px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="96" height="32" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Scientific Reports':
                        image = '''<span style="float: left; width: 165px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="160" height="32" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                else:
                    image = '''<span style="float: left; width: 48px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="42" height="51" text-align="left"></span> ''' % (
                        allEntries[i]['image'])
            if 'formattedauthor' in allEntries[i].keys():
                formattedAuthor = allEntries[i]['formattedauthor']
            if 'formattedtitle' in allEntries[i].keys():
                formattedtTitle = ',&ldquo;<strong>%s</strong> &rdquo;' % allEntries[i]['formattedtitle']
            if 'journal' in allEntries[i].keys():
                journal = ',&nbsp;<em>%s</em>&nbsp;' % (
                    allEntries[i]['journal'])
            if 'year' in allEntries[i].keys():
                year = '<strong>%s</strong>,' % allEntries[i]['year']
            if 'volume' in allEntries[i].keys():
                if 'number' in allEntries[i].keys():
                    volume = '<em>%s(%s)</em>' % (
                        allEntries[i]['volume'], allEntries[i]['number'])
                else:
                    volume = '<em>%s</em>' % (allEntries[i]['volume'])
            elif 'number' in allEntries[i].keys():
                number = '<em>%s</em>' % (allEntries[i]['number'])
            if 'pages' in allEntries[i].keys():
                pages = ','+allEntries[i]['pages']
            if 'cited' in allEntries[i].keys():
                if allEntries[i]['cited'] != '0':
                    cited = '<br><span class="cited">&nbsp;&nbsp;Cited: %s</span>' % allEntries[i]['cited']
                else:
                    cited = '<br><span class="cited" style="display:none>&nbsp;&nbsp;Cited: %s</span>' % allEntries[i]['cited']
            if 'impactfactor' in allEntries[i].keys():
                if 'impactfactoryear' not in allEntries[i].keys():
                    impactFactor = '<span class="infact">(<strong>IF 2019: %s</strong>)</span><br>' % allEntries[i]['impactfactor']
                else:
                    impactFactor = '<span class="infact">(<strong>IF %s %s</strong>)</span><br>' % (allEntries[i]['impactfactoryear'],allEntries[i]['impactfactor'])
            if 'url' in allEntries[i].keys():
                url = '''<a href="%s" target="_blank" style="float: left">%s</a>''' % (
                    allEntries[i]['url'], allEntries[i]['url'])

            tempHtml = hiho + image + formattedAuthor + formattedtTitle + \
                journal + year + volume + number + pages + cited + impactFactor + url
            tempHtml = '<li style="float: left;padding:5px 0px">' + tempHtml + '</li>'
            proceedBody = proceedBody + tempHtml
    (totalarticles, articaltotalcitations, hindex, i10index,
     citationperpaper, journalnumber, averageif, hihonumber) = getstatistics()
    c = totalarticles+totalbooks+1
    proceedBody = '<ol start=%s style="margin-top: 0px;padding-top:0px">%s</ol>' % (
        c, proceedBody)
    proceed = proceed + proceedBody
    return proceed


def generateEditorialsHtml(bibFilePath):
    # 生成Articles部分,返回HTML
    parser = BibTexParser(common_strings=False)
    parser.ignore_nonstandard_types = False

    with open(bibFilePath, encoding='utf8') as bibtexFile:
        ircreDatabase = bibtexparser.load(bibtexFile, parser)

    allEntries = ircreDatabase.entries.copy()
    (totalbooks, othertotalcitations, totalproceeds, totaleditors) = getsothers()
    # article的初始值为 artile部分的信息
    # 包括article整体资料与标题
    editorials = '''
        <div id="editorials" style="margin-top:20px;margin-bottom:20px;">
            <h3 class="title">
                <strong><a id="articles"></a>Editorials</a></strong>
                <span class="listcountred">(<span id="totalarticles">'''+str(totaleditors)+'''</span>)</span>
            </h3>
            </div>'''
    editorialsBody = ''
    for i in range(len(allEntries)):
        tempHtml = ''
        hiho = ''
        image = ''
        formattedAuthor = ''
        formattedtTitle = ''
        journal = ''
        year = ''
        volume = ''
        number = ''
        pages = ''
        paperid = ''
        url = ''
        impactFactor = ''
        cited = ''
        if allEntries[i]['ENTRYTYPE'] == 'incollection':
            # keys = allEntries[i].keys()
            # 无法显示 hihoimage
            if 'hihoimage' in allEntries[i].keys():
                hiho = '''
                    <div style=" height:40px; width:500px;text-align: left;"><img
                src="./images/articlecover/ISIHighlycitedlogo.jpg" alt="" width="77" height="31">
                    <a class="hiholinka" a href="./%s"
                target="_blank"><strong><em> %s</em></strong></a></div>
                    ''' % (allEntries[i]['hiholink'], allEntries[i]['hihosubject'])
            if 'image' in allEntries[i].keys():
                if 'imagewidth' in allEntries[i].keys():
                    imagewidth = allEntries[i]['imagewidth']
                    if imagewidth == 'The Scientific World Journal':
                        image = '''<span style="float: left; width: 138px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""  width="132" height="50" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'MRS Proceedings':
                        image = '''<span style="float: left; width: 156px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""  width="148" height="31" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Nature Communications':
                        image = '''<span style="float: left; width: 156px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="148" height="28" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Beilstein Journal of Nanotechnology':
                        image = '''<span style="float: left; width: 190px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""  width="184" height="22" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Nature Communications':
                        image = '''<span style="float: left; width: 108px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="102" height="32" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Physical Review B':
                        image = '''<span style="float: left; width: 102px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="96" height="32" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                    if imagewidth == 'Scientific Reports':
                        image = '''<span style="float: left; width: 165px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="160" height="32" text-align="left"></span> ''' % (
                            allEntries[i]['image'])
                else:
                    image = '''<span style="float: left; width: 48px;"><img class="bibtexVar" src="./images/otherpublications/%s" alt=""   width="42" height="51" text-align="left"></span> ''' % (
                        allEntries[i]['image'])
            if 'formattedauthor' in allEntries[i].keys():
                formattedAuthor = allEntries[i]['formattedauthor']
            if 'formattedtitle' in allEntries[i].keys():
                formattedtTitle = ',&ldquo;<strong>%s</strong> &rdquo;' % allEntries[i]['formattedtitle']
            if 'journal' in allEntries[i].keys():
                journal = ',&nbsp;<em>%s</em>&nbsp;' % (
                    allEntries[i]['journal'])
            if 'year' in allEntries[i].keys():
                year = '<strong>%s</strong>,' % allEntries[i]['year']
            if 'volume' in allEntries[i].keys():
                if 'number' in allEntries[i].keys():
                    volume = '<em>%s(%s)</em>' % (
                        allEntries[i]['volume'], allEntries[i]['number'])
                else:
                    volume = '<em>%s</em>' % (allEntries[i]['volume'])
            elif 'number' in allEntries[i].keys():
                number = '<em>%s</em>' % (allEntries[i]['number'])
            if 'pages' in allEntries[i].keys():
                pages = ','+allEntries[i]['pages']
            if 'cited' in allEntries[i].keys():
                if allEntries[i]['cited'] != '0':
                    cited = '<br><span class="cited">&nbsp;&nbsp;Cited: %s</span>' % allEntries[i]['cited']
                else:
                    cited = '<br><span class="cited" style="display:none>&nbsp;&nbsp;Cited: %s</span>' % allEntries[i]['cited']
            if 'impactfactor' in allEntries[i].keys():
                if 'impactfactoryear' not in allEntries[i].keys():
                    impactFactor = '<span class="infact">(<strong>IF 2019: %s</strong>)</span><br>' % allEntries[i]['impactfactor']
                else:
                    impactFactor = '<span class="infact">(<strong>IF %s %s</strong>)</span><br>' % (allEntries[i]['impactfactoryear'],allEntries[i]['impactfactor'])
            if 'url' in allEntries[i].keys():
                url = '''<a href="%s" target="_blank" style="float: left">%s</a>''' % (
                    allEntries[i]['url'], allEntries[i]['url'])

            tempHtml = hiho + image + formattedAuthor + formattedtTitle + \
                journal + year + volume + number + pages + cited + impactFactor + url
            tempHtml = '<li style="float: left;padding:5px 0px">' + tempHtml + '</li>'
            editorialsBody = editorialsBody + tempHtml
    (totalarticles, articaltotalcitations, hindex, i10index,
     citationperpaper, journalnumber, averageif, hihonumber) = getstatistics()
    d = totalarticles+totalbooks+totalproceeds+1
    editorialsBody = '<ol start=%s style="margin-top: 0px;padding-top:0px">%s</ol>' % (
        d, editorialsBody)
    editorials = editorials + editorialsBody
    return editorials


def generatehtml():

    prebody = '''
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
        <script src="./js/jquery.min.js" type="text/javascript"></script>
        <script src="./js/moment.min.js" type="text/javascript"></script>
        <script src="./js/reverse_list.js" type="application/javascript"></script>
        <script async src="./js/popper.min.js" crossorigin="anonymous"></script>
        <script async src="./js/bootstrap.min.js" crossorigin="anonymous"></script>
        <script type="text/javascript" async src="./js/bibtex_js.js"></script>
        <style type="text/css">
            .cited {font-family: Arial, Helvetica, sans-serif;
                    font-weight: bold;
                    color: #00F;
                    float: right;
                }
        #bookchapters {width: 960px;
                }
        #bookchapters h3 {text-align: center;
                        margin-top: 21px;
                        margin-bottom: 0px;
                    }

        #proceedings {width: 960px;
                    }
        #proceedings h3 {text-align: center;
                        margin-top: 21px;
                        margin-bottom: 0px;
                    }
        #editorials {width: 960px;
                    }
        #editorials h3 {text-align: center;
                        margin-top: 21px;
                        margin-bottom: 0px;
                    }
        </style>
        <link rel="stylesheet" type="text/css" href="./css/ircre.css" media="all">
        <title>
            International Research Center for Renewable Energy
        </title>
    </head>

    <body>

        <div id="header-ban">
            <p>&nbsp;</p>
            <div id="logo"><img src="images/ircre-logo.jpg" width="360" height="153" alt=""></div>
            <ul>
                <li><a href="index.html"><span>home</span></a></li>
                <li><a href="people.html"><span>People</span></a></li>
                <li><a href="facility.html"><span>Facility</span></a></li>
                <li><a href="about.html"><span>About IRCRE</span></a></li>
                <li class="selected"><a href="research.html"><span>Research</span></a></li>
                <li><a href="press.html">PRESS</a></li>
                <li><a href="events.html"><span>EVENTS</span></a></li>
                <li><a href="contact.html"><span>contact us</span></a></li>
            </ul>
            <p>
        </div>
        <div id="body">
            <div class="products">
                <div id="second-header-ban">
                    <span style="float: left;">
                        <h2 class="second-header-ban-title">RESEARCH</h2>
                    </span>
                    <ul id="second-header-menu">
                        <li id="second-menu-articles"><a href="#articles"><span>ARTICLES</span></a></li>
                        <li id="second-menu-bookchapters"><a href="#bookchapters"><span>BOOK CHAPTERS</span></a></li>
                        <li id="second-menu-conferences"><a href="#conferences"><span>CONFERENCES</span></a></li>
                        <li id="second-menu-organizers"><a href="#organizers"><span>ORGANIZERS</span></a></li>
                        <li id="second-menu-proceedings"><a href="#proceedings"><span>PROCEEDINGS</span></a></li>
                        <li id="second-menu-editorials"><a href="#editorials"><span>EDITORIALS</span></a></li>
                        <li id="second-menu-seminars"><a href="#seminars"><span>SEMINARS</span></a></li>
                        <li id="second-menu-committee"><a href="#committee"><span>COMMITTEE</span></a></li>
                    </ul>
                </div>
        '''

    afterbody = '''
                    <div id="divconferences">
                    <h3><a id="conferences"></a><strong>International Conference /
                        Workshop Talks</strong> <span
                            class="listcount">(323)</span></h3>
                    <h4>
                        <strong>Plenary/keynote lecture</strong> <span class="invited">(<strong>62</strong>)</span>,
                        <strong>Invited
                            talk</strong> <span class="invited">(<strong>144</strong>)</span>, <strong>Oral
                        presentation</strong>
                        <span class="invited">(<strong>116</strong>)</span>, <strong>Panelist</strong> <span
                            class="invited">(<strong>1</strong>)</span>
                    </h4>

                    <h5 align="center" class="h5" style="margin-top:15px; margin-bottom:0px;">2019 (12)</h5>
                    <ol style="list-style-type:decimal; margin: 30px; padding:30px 10px;" reversed start="323">
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>Aqueous Chemical Design & Electronic Structure Engineering of Advanced
                            HeteroNanostructures for Efficient Solar Energy Conversion</strong>&rdquo;, 7th International
                            Forum
                            for Young Scholars, UESTC Fundamental & Frontier Sciences, Chengdu, China, December 2019
                        </li>


                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Opening Plenary</strong>)</span>,
                            &ldquo;<strong>A Place in the Sun for Artificial Photosynthesis</strong>&rdquo;, 2019 Fall
                            Meeting
                            of the Korean Ceramic Society, Seoul, South Korea, November 2019
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Plenary</strong>)</span>,
                            &ldquo;<strong>A Place in the Sun for Artificial Photosynthesis</strong>&rdquo;, 7th
                            International
                            Workshop on Nanotechnology & Applications, Phan Thiet City, Vietnam, November 2019
                        </li>
                        <li>

                            <strong>L. Vayssieres</strong> <span
                                class="invited">(<strong>Invited talk & Session Chairs</strong>)</span>,
                            &ldquo;<strong>On the Anisotropic Charge Separation and the Growth of Highly Ordered
                            Heteronanostructures for Efficient Photocatalytic Water Splitting</strong>&rdquo;, 236th
                            Electrochemical Society Meeting, Symposium I04 on Photocatalysts, Photoelectrochemical Cells,
                            and
                            Solar Fuels 10, Atlanta, GA, USA, October 2019
                        </li>
                        <li>

                            <strong>L. Vayssieres</strong> <span
                                class="invited">(<strong>Invited talk & Session Chair</strong>)</span>,
                            &ldquo;<strong>Sustainable Energy from Seawater</strong>&rdquo;, 10th International Conference
                            on
                            Materials for Advanced Technology (ICMAT), Symposium CC on Novel Solution Processing for
                            Advanced
                            Functional Materials for Energy, Environmental and Biomedical, Singapore, June 2019
                        </li>
                        <li>

                            <strong><u>S.H. Shen</u></strong> <span class="invited">(<strong>Invited</strong>)</span>, T.T.
                            Kong,
                            &ldquo;<strong>Structure Design of Graphitic Carbon Nitride for Photocatalytic Water
                            Splitting</strong>&rdquo;, E-MRS Spring Meeting, IUMRS-ICAM International Conference on Advanced
                            Materials, Symposium A on Latest Advances in Solar Fuels, Acropolis, Nice, France, May 2019
                        </li>
                        <li>

                            <u>J.S. Pap</u> <span class="invited">(<strong>Invited</strong>)</span>, D. Lukács, M. Németh,
                            Ł.
                            Szyrwiel, L. Illés, B. Pécz, <strong>S.H. Shen</strong>, <strong>L. Vayssieres</strong>,
                            &ldquo;<strong>Behavior of Cu-Peptides under Water Oxidation Conditions – Molecular
                            Electrocatalysts
                            or Precursors to Nanostructured CuO Films?</strong>&rdquo;, E-MRS Spring Meeting, IUMRS-ICAM
                            International Conference on Advanced Materials, Symposium A on Latest Advances in Solar Fuels,
                            Acropolis, Nice, France, May 2019
                        </li>
                        <li>

                            <strong><u>I. Rodríguez-Gutiérrez</u></strong> <span
                                class="invited">(<strong>Invited</strong>)</span>, J.Z. Su, G. Rodríguez-Gattorno, F.L. de
                            Souza, G. Oskam, &ldquo;<strong>Infuence of the thin film physical configuration on the charge
                            transfer and recombination dynamics of WO<sub>3</sub>-BiVO<sub>4</sub> multilayer systems for
                            photoelectrochemical and solar fuel applications</strong>&rdquo;, E-MRS Spring Meeting,
                            IUMRS-ICAM
                            International Conference on Advanced Materials, Symposium A on Latest Advances in Solar Fuels,
                            Acropolis, Nice, France, May 2019
                        </li>
                        <li>

                            <strong>L. Vayssieres</strong> <span
                                class="invited">(<strong>Plenary Lecture & Session Chair</strong>)</span>, &ldquo;<strong>Low-cost
                            Aqueous Design of Earth-abundant Nanostructures for Sustainable Energy from Seawater</strong>&rdquo;,
                            International Symposium on Nanoscience & Nanotechnology in the Environment, Xi'an, China, April
                            2019
                        </li>

                        <li>

                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>A Place in the Sun for Artificial Photosynthesis</strong>&rdquo;, 257th ACS
                            National
                            Meeting, Symposium on Photocatalytic and Electrochemical Processes: Fundamentals and
                            Applications in
                            Green Energy and Environmental Remediation”, Orlando, FL, USA, March-April 2019
                        </li>
                        <li>

                            <strong><u>M. Fronzi</u></strong>, Hussein Assadi, Dorian Hanaor, &ldquo;<strong>Theoretical
                            insights into the hydrophobicity of low index CeO<sub>2</sub> surfaces</strong>&rdquo;, American
                            Physical Society (APS) March Meeting, Boston, MA, USA, March 2019
                        </li>

                        <li>

                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>A Place in the Sun for Artificial Photosynthesis</strong>&rdquo;, SPIE Photonics
                            West, Symposium on Synthesis & Photonics of Nanoscale Materials XVI, Session on Synthesis &
                            Photonics of Nanomaterials, San Francisco, CA, USA, February 2019
                        </li>
                    </ol>

                    <h5 align="center" class="h5" style="margin-top:15px; margin-bottom:0px;">2018 (27)</h5>
                    <ol style="list-style-type:decimal; margin: 30px; padding:30px 10px;" reversed start="311">
                        <li>

                            <strong>M. Fronzi</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Reactivity
                            of metal oxide nanocluster modified rutile and anatase TiO<sub>2</sub>: Oxygen vacancy formation
                            and
                            CO<sub>2</sub> interaction</strong>&rdquo;, EMN Meeting on Titanium- Oxides, Auckland, New
                            Zealand,
                            December 2018
                        </li>
                        <li>

                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>A Place in the Sun for Artificial Photosynthesis</strong>&rdquo;, International
                            Symposium on Solar Energy Conversion, Nankai University, Tianjin, China, October 2018
                        </li>
                        <li>

                            <strong>L. Vayssieres</strong> <span
                                class="invited">(<strong>Keynote &amp; Session Chairs</strong>)</span>,
                            &ldquo;<strong>Clean & Sustainable Energy from Photocatalytic Seawater Splitting</strong>&rdquo;,
                            2018 AiMES ECS - SMEQ Joint Conference, Cancun, Mexico, October 2018
                        </li>
                        <li>

                            <strong><u>I. Rodríguez-Gutiérrez</u></strong>, R. García-Rodríguez, A. Vega-Poot, <strong>J.Z.
                            Su</strong>, G. Rodríguez-Gattorno, <strong>L. Vayssieres</strong>, G. Oskam, &ldquo;<strong>Analysis
                            of the Charge Transfer Dynamics in Oxide Based Photoelectrodes through Small Perturbations
                            Techniques</strong>&rdquo;, America International Meeting on Electrochemistry and Solid State
                            Science (AiMES 2018), Cancun, Mexico, October 2018
                        </li>
                        <li>

                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>A Place in the Sun for Artificial Photosynthesis?</strong>&rdquo;, Frontiers of
                            Photonics, 31st Annual Conference of the IEEE Photonics Society (IPC-2018), Reston, VA, USA,
                            September 2018
                        </li>
                        <li>

                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>Clean Sustainable Energy (& More) from Seawater</strong>&rdquo;, Symposium on
                            Photo-Electrochemical Energy Conversion in Honor of Prof. Jan Augustynski, 69th Annual Meeting
                            of
                            the International Society of Electrochemistry, Bologna, Italy, September 2018
                        </li>
                        <li>
                            <strong>S.H. Shen</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Structure
                            Engineering of Graphitic Carbon Nitride for Efficient Photocatalytic Water Splitting</strong>&rdquo;,
                            Taishan Forum for Advanced Interdisciplinary Research (FAIR), Jinan, China, September 2018
                        </li>
                        <li>

                            <strong><u>S.H. Shen</u></strong>, <strong>D.M. Zhao</strong> <span
                                class="invited">(<strong>Invited</strong>)</span>, &ldquo;<strong>Structure Engineering of
                            Graphitic Carbon Nitride for Efficient Photocatalytic Water Splitting</strong>&rdquo;,
                            International
                            Workshop on Water Splitting: Challenges and Opportunity, Xi'an, China, August 2018
                        </li>
                        <li>

                            <strong>S.H. Shen</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Surface
                            Engineering of α-Fe<sub>2</sub>O<sub>3</sub> and p-Si for Efficient Solar Water
                            Splitting</strong>&rdquo;,
                            22nd International Conference on Photochemical Conversion and Storage of Solar Energy, Hefei,
                            China,
                            July-August 2018
                        </li>
                        <li>

                            <strong><u>S.H. Shen</u></strong>, <strong>D.M. Zhao</strong> <span
                                class="invited">(<strong>Invited</strong>)</span>, &ldquo;<strong>Structure Engineering of
                            Graphitic Carbon Nitride for Efficient Photocatalytic Water Splitting</strong>&rdquo;,
                            International
                            Conference on Energy and Environmental Materials (ICEEM), Hefei, China, July-August 2018
                        </li>
                        <li>
                            <strong><u>I. Rodríguez-Gutiérrez</u></strong>, R. García-Rodríguez, A. Vega-Poot, <strong>J.Z.
                            Su</strong>, G. Rodríguez-Gattorno, <strong>L. Vayssieres</strong>, G. Oskam, &ldquo;<strong>Understanding
                            the Charge Carrier Dynamics in Oxide Based Photoelectrodes</strong>&rdquo;, 22<sup>nd</sup>
                            International Conference on Photochemical conversion and Storage of Solar Energy (IPS-22),
                            Hefei,
                            China, July 2018
                        </li>
                        <li>
                            <strong><u>M. Fronzi</u></strong>, S. Tawfik, C. Stampfl, M.J. Ford, &ldquo;<strong>Magnetic
                            character of stoichiometric and reduced Co<sub>9</sub>S<sub>8</sub></strong>&rdquo;, Australian
                            Symposium on Computationally Enhanced Materials Design, Sydney, Australia, July 2018
                        </li>
                        <li>
                            <strong><u>J.W. Shi</u></strong>, Y.Z. Zhang, L.J. Guo<span
                                class="invited"> (<strong>Invited</strong>)</span>, &ldquo;<strong>Hydrothermal growth of
                            CO<sub>3</sub>(OH)<sub>2</sub>(HPO<sub>4</sub>)<sub>2</sub>
                            nano-needles on LaTiO<sub>2</sub>N for enhanced photocatalytic O<sub>2</sub> evolution under
                            visible-light irradiation</strong>&rdquo;, 12th International Conference on Ceramic Materials
                            and
                            Components for Energy and Environmental Applications (CMCEE 2018), Singapore, July 2018
                        </li>
                        <li>
                            <strong><u>Y.B. Chen</u></strong>, Y. Liu <span
                                class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Switchable synthesis of copper-based chalcogenide films for photoelectrochemical
                            water splitting</strong>&rdquo;, 12th International Conference on Ceramic Materials and
                            Components
                            for Energy and Environmental Applications (CMCEE 2018), Singapore, July 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>On Seawater & Clean Energy Generation</strong>&rdquo;, 12th International
                            Conference
                            on Ceramic Materials and Components for Energy and Environmental Applications (CMCEE 2018),
                            Symposium T4S12 on Advanced Ceramics Materials for Photonics, Energy & Health, Singapore, July
                            2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>Latest Advances in Low-cost Solar Fuel Generation</strong>&rdquo;, 12th
                            International
                            Conference on Ceramic Materials and Components for Energy and Environmental Applications (CMCEE
                            2018), Symposium T1S3 on Emerging Materials & Techonologies for Solar Cells & Solar Fuels
                            Technologies, Singapore, July 2018

                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>Low-cost Fabrication of Advanced Heteronanostructures for Efficient Solar Energy
                            Conversion</strong>&rdquo;, 12th International Conference on Ceramic Materials and Components
                            for
                            Energy and Environmental Applications (CMCEE 2018), Symposium T1S5 on Innovative Processing of
                            Nanostructured & Hybrid Functional Materials for Energy & Sustaibability, Singapore, July 2018


                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Sustainable Clean Energy from Seawater</strong>&rdquo;, 12th International
                            Conference
                            on Ceramic Materials and Components for Energy and Environmental Applications (CMCEE 2018),
                            Symposium T3S1 on Photocatalysts for Energy & Environmental Applications, Singapore, July 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>Clean Energy from Seawater</strong>&rdquo;, 26th Annual International Conference
                            on
                            Composites/Nano Engineering (ICCE-26), Paris, France, July 2018
                        </li>
                        <li>
                            <strong>M. Fronzi</strong>, &ldquo;<strong>Native-defects-related magnetic character of cobalt
                            sulphide</strong>&rdquo;, International Workshop on Materials Theory and Computation, Xi’an
                            Jiaotong
                            University, Xi'an, China, June-July 2018
                        </li>
                        <li>
                            <strong>S.H. Shen</strong> <span
                                class="invited">(<strong>Invited talk &amp; International Advisory Board</strong>)</span>,
                            &ldquo;<strong>Engineering Hematite and Silicon for Efficient Photoelectrochemical Water
                            Splitting,
                            Symposium CE: Frontiers in Nanostructured, Nanocomposite and Hybrid Functional Materials for
                            Energy
                            and Sustainability</strong>&rdquo;, 14th International Ceramics Congress (CIMTEC 2018), Perugia,
                            Italy, June 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span
                                class="invited">(<strong>Invited talk &amp; Session Chair</strong>)</span>, &ldquo;<strong>Latest
                            Advances in Design, Performance, & Stability of Solar Seawater Splitting Materials</strong>&rdquo;,
                            233rd Electrochemical Society Meeting, Seattle, WA, USA, May 2018
                        </li>
                        <li>
                            <strong><u>M. Fronzi</u></strong>, J Bishop, M Toth, M Ford, &ldquo;<strong>Controlling Surface
                            Patterning of Diamond: The Origin of Anisotropy with Electron Beam Induced Etching</strong>&rdquo;,
                            American Physical Society Meeting, Los Angeles, California, USA, March 2018
                        </li>
                        <li>
                            <strong><u>M. Fronzi</u></strong>, O Mokhtari, Y Wang, H Nishikawa, &ldquo;<strong>Long-term
                            reliability of Pb-free solder joint between copper interconnect and silicon in photovoltaic
                            solar
                            cell</strong>&rdquo;, American Physical Society Meeting, Los Angeles, California, USA, March
                            2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>On The Stability & Performance of Low-Cost Devices for Solar Hydrogen
                            Generation</strong>&rdquo;, 3rd Fusion Conference on Molecules and Materials for Artificial
                            Photosynthesis, Cancun, Mexico, March 2018
                        </li>
                        <li>
                            <strong><u>M.C. Liu</u></strong>, L.J. Guo<span
                                class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>On Controlling of the Mass and Energy Flow for Efficient Photocatalytic Solar
                            H<sub>2</sub> Production</strong>&rdquo;, 2nd International Summit on Energy Science and
                            Technology,
                            Xi’an, China, January, 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Plenary</strong>)</span>,
                            &ldquo;<strong>On Solar Water Splitting</strong>&rdquo;, 8th IEEE International Nanoelectronics
                            Conference (INEC2018), Kuala Lumpur, Malaysia, January 2018
                        </li>
                    </ol>
                    <h5 align="center" class="h5" style="margin-top:15px; margin-bottom:0px;">2017 (43)</h5>
                    <ol style="list-style-type:decimal; margin: 30px; padding:30px 10px;" reversed start="284">
                        <li>
                            <strong><u>Y.K. Wei</u></strong>, Z.Q. Wang, <strong>J. Wang</strong>, <strong>J.Z. Su</strong>,
                            <strong>L.J. Guo</strong>, &ldquo;<strong>BiVO<sub>4</sub>-rGO-NiFe Nanoarrays Photoanode:
                            Oriented
                            Hierarchical Growth and Application for Photoelectrochemical Water Splitting</strong>&rdquo;,
                            15<sup>th</sup> International Conference on Clean Energy (ICCE 2017), Xi'an, China, December
                            2017
                        </li>
                        <li>
                            <strong><u>J. Wang</u></strong>, <strong>M.L. Wang</strong>, <strong>T. Zhang</strong>, <strong>J.Z,
                            Su</strong>, <strong>L.J. Guo</strong>, &ldquo;<strong>Facile Synthesis of Ultrafine Hematite
                            Nanowire Arrays for Efficient Charge Separation</strong>&rdquo;, 15<sup>th</sup> International
                            Conference on Clean Energy (ICCE 2017), Xi'an, China, December 2017
                        </li>
                        <li>
                            <strong><u>I.R. Gutiérrez</u></strong>, R.G. Rodriguez, M.R. Perez, A.V. Poot, G.R. Gattorno, G.
                            Oskam, &ldquo;<strong>Charge transfer dynamics at inkjet printed
                            <em>p</em>-CuBi<sub>2</sub>O<sub>4</sub> photocathodes for photoelectrochemical water
                            splitting</strong>&rdquo;, 15<sup>th</sup> International Conference on Clean Energy (ICCE 2017),
                            Xi'an, China, December 2017
                        </li>
                        <li>
                            <strong><u>W.L. Fu</u></strong>, <strong>F. Xue</strong>, <strong>M.C. Liu</strong>, <strong>L.J.
                            Guo</strong>, &ldquo;<strong>Kilogram-scale production of highly active chalcogenide
                            photocatalyst
                            for solar hydrogen generation</strong>&rdquo;, 15<sup>th</sup> International Conference on Clean
                            Energy (ICCE 2017), Xi'an, China, December 2017
                        </li>
                        <li>
                            <strong><u>Y.P. Yang</u></strong>, <strong>X. Zhang</strong>, <strong>L.J. Guo</strong>, H.T.
                            Liu,
                            &ldquo;<strong>Local Degradation Phenomena in Proton Exchange Membrane Fuel Cells with
                            Dead-ended
                            Anode</strong>&rdquo;, 15<sup>th</sup> International Conference on Clean Energy (ICCE 2017),
                            Xi'an,
                            China, December 2017
                        </li>
                        <li>
                            <strong><u>Z.D. Diao</u></strong>, <strong>D.M. Zhao</strong>, <strong>S.H. Shen</strong>,
                            &ldquo;<strong>Polycrystalline Titanium Dioxide Nanofibers for Superior Sodium Storage</strong>&rdquo;,
                            15<sup>th</sup> International Conference on Clean Energy (ICCE 2017), Xi'an, China, December
                            2017
                        </li>
                        <li>
                            <strong><u>F. Xue</u></strong>, <strong>W.L. Fu</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>NiS<sub>2</sub>
                            Nanodots Decorated g-C<sub>3</sub>N<sub>4</sub> Nanosheets: A High-efficiency, Low-cost, and
                            Long-term Photocatalyst for Improving Hydrogen Evolution</strong>&rdquo;, 15<sup>th</sup>
                            International Conference on Clean Energy (ICCE 2017), Xi'an, China, December 2017
                        </li>
                        <li>
                            <strong>M.T. Li</strong> <span class="invited">(<strong>Keynote</strong>)</span>, <strong>D.Y.
                            Liu</strong>, <strong>Y.C. Pu</strong>, &ldquo;<strong>Photo/Electrocatalysis: Mechanistic
                            Insight
                            and Catalyst Design from Density Functional Theory</strong>&rdquo;, 15<sup>th</sup>
                            International
                            Conference on Clean Energy (ICCE 2017), Xi'an, China, December 2017
                        </li>
                        <li>
                            <strong>J.Z. Su</strong> <span class="invited">(<strong>Keynote</strong>)</span>, <strong>J.L.
                            Zhou</strong>, <strong>C. Liu</strong>, &ldquo;<strong>Enhanced Charge Separation in
                            BiVO<sub>4</sub> Electrodes by Zn Surface Modification and Back Contact Cu Gradient Profile
                            Doping
                            for Photoelectrochemical Water Splitting</strong>&rdquo;, 15<sup>th</sup> International
                            Conference
                            on Clean Energy (ICCE 2017), Xi'an, China, December 2017
                        </li>
                        <li>
                            <strong>Y.B. Chen</strong> <span class="invited">(<strong>Keynote</strong>)</span>, <strong>Z.X.
                            Qin</strong>, <strong>M.L. Wang</strong>, <strong>R. Li</strong>, &ldquo;<strong>Rational Design
                            of
                            Noble-metal-free Catalysts for Hydrogen Evolution Reaction</strong>&rdquo;, 15<sup>th</sup>
                            International Conference on Clean Energy (ICCE 2017), Xi'an, China, December 2017
                        </li>
                        <li>
                            <strong>M.C. Liu</strong> <span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>Controlled
                            Photocatalytic Nanocrystal for Tunable Solar H<sub>2</sub> Production</strong>&rdquo;,
                            15<sup>th</sup> International Conference on Clean Energy (ICCE 2017), Xi'an, China, December
                            2017
                        </li>
                        <li>

                            <strong>M. Fronzi</strong> <span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>Origin
                            of Topological Anisotropic Patterns in Gas Mediated Electron Beam Induced Etching</strong>&rdquo;,
                            15<sup>th</sup> International Conference on Clean Energy (ICCE 2017), Xi'an, China, December
                            2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Plenary</strong>)</span>,
                            &ldquo;<strong>On Photocatalytic Solar Hydrogen Generation</strong>&rdquo;, 15<sup>th</sup>
                            International Conference on Clean Energy (ICCE 2017), Xi'an, China, December 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Latest advances & Challenges in Solar Water Splitting</strong>&rdquo;,
                            1<sup>st</sup>
                            Frontiers in Electroceramics Workshop, Massachusetts Institute of Technology, Cambridge, MA,
                            USA,
                            December 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Design, performance and stability of low-cost materials for photocatalytic solar
                            water splitting</strong>&rdquo;, 2017 MRS Fall Meeting, Symposium ES2: On the Way to Sustainable
                            Solar Fuels—New Concepts, Materials and System Integration, Boston, MA, USA, November 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Clean Energy from Seawater</strong>&rdquo;, International Summit of the MRS
                            University Chapters on Sustainability & Nanotechnology, Boston, MA, USA, November 2017
                        </li>
                        <li>
                            <strong><u>S.H. Shen</u></strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            <strong>Y.M.
                                Fu</strong>, <strong>W. Zhou</strong>, &ldquo;<strong>Engineering Surface Structures and
                            Energetics
                            of α-Fe<sub>2</sub>O<sub>3</sub> and Si for Photoelectrochemical Water Splitting</strong>&rdquo;,
                            18th International Conference of the Union of Materials Research Societies in Asia (IUMRS-ICA
                            2017),
                            Taipei, Taiwan, China, November 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Latest Advances in Water Splitting</strong>&rdquo;, 18th International Union of
                            Materials Research Societies International Conference in Asia (IUMRS-ICA 2017), Symposium B2.
                            Photocatalysis and Photosynthesis, Taipei, Taiwan, China, November 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span
                                class="invited">(<strong>Invited talk & Session chair</strong>)</span>,
                            &ldquo;<strong>On the low cost design, performance and stability of advanced electrodes for
                            photocatalytic (sea)water splitting</strong>&rdquo;, 232nd Electrochemical Society Meeting,
                            Symposium on Photocatalysts, Photoelectrochemical Cells, & Solar Fuels 8, National Harbor, MD,
                            USA,
                            October 2017
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Surface
                            Modified Hematite and Silicon for Photoelectrochemical Water Splitting</strong>&rdquo;,
                            International Conference on Functional Nanomaterials and Nanodevices, Budapest, Hungary,
                            September
                            2017
                        </li>
                        <li>
                            <strong>M.C. Liu</strong> <span class="invited">(<strong>Plenary</strong>)</span>,
                            &ldquo;<strong>Solar
                            Hydrogen Production via Photocatalysis: From Microscale Semiconductor Particle to Pilot Reaction
                            System</strong>&rdquo;, UK-China International Particle Technology Forum VI 2017, Yangzhou,
                            China,
                            September 2017
                        </li>
                        <li>
                            <strong>M.C. Liu</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Complex
                            Photocatalysis via Simple Twinned Nanostructure</strong>&rdquo;, 2017 China-UK Workshop on
                            Efficient
                            Energy Utilisation, Nanjing, China, August 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>On low-cost photocatalytic water splitting</strong>&rdquo;, XXVI International
                            Materials Research Congress, Symposium on Materials and Technologies for Energy Conversion,
                            Saving
                            and Storage (MATECSS), Cancun, Mexico, August 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>On the Design, Performance & Stability of Advanced Materials for Photocatalytic
                            Solar
                            Water Splitting</strong>&rdquo;, XXVI International Materials Research Congress, 3rd
                            Mexico-China
                            Workshop on Nano Materials/Science/Technology: Renewable Energy and Environment Remediation
                            (NANOMXCN), Cancun, Mexico, August 2017
                        </li>
                        <li>
                            <strong><u>A. Hassanpour</u></strong>, <strong>L. Vayssieres</strong>, P. Bianucci,
                            &ldquo;<strong>Optical
                            and Structural Properties of Arrays of Mg-doped ZnO Nanorods Prepared by a Low Temperature
                            Hydrothermal Method</strong>&rdquo;, 18th Canadian Semiconductor Science & Technology
                            Conference,
                            Waterloo, ON, Canada, August 2017
                        </li>
                        <li>
                            <strong>S.H. Shen</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Surface
                            Modified Hematite Nanorods for Photoelectrochemical Water Splitting</strong>&rdquo;, 7th
                            International Multidisciplinary Conference on Optofluidics, Singapore, July 2017
                        </li>
                        <li>
                            <strong>S.H. Shen</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Surface
                            Engineering of α-Fe<sub>2</sub>O<sub>3</sub> and p-Si for Efficient Solar Water
                            Splitting</strong>&rdquo;,
                            33rd International conference of the Society for Environmental Geochemistry and Health (SEGH
                            2017),
                            Guangzhou, China, July 2017
                        </li>
                        <li>
                            <strong>M.C. Liu </strong><span
                                class="invited">(<strong>Invited talk & Session chair</strong>)</span>, &ldquo;<strong>Nanotwin:
                            Simple Structure for Complex Photocatalysis</strong>&rdquo;, 8th International Conference on
                            Hydrogen Production (ICH2P 2017), Brisbane, Australia, July 2017
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Surface
                            Engineered Hematite Nanorods for Efficient Photoelectrochemical Water Splitting</strong>&rdquo;,
                            8th
                            International Conference on Hydrogen Production (ICH2P 2017), Brisbane, Australia, July 2017
                        </li>
                        <li>
                            <strong><u>J.W. Shi</u></strong>, <strong>Y.Z. Zhang</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>LaTiO<sub>2</sub>N-LaCrO<sub>3</sub>: Novel continuous solid solutions towards
                            enhanced photocatalytic H<sub>2</sub> evolution under visible-light irradiation</strong>&rdquo;,
                            8th
                            International Conference on Hydrogen Production (ICH2P 2017), Brisbane, Australia, July 2017
                        </li>
                        <li>
                            <strong>M.C. Liu</strong>, &ldquo;<strong>Seed-mediated Growth: A Versital Method for
                            Understanding
                            Crystal Habits</strong>&rdquo;, 9<sup>th</sup> World Congress on Materials Science and
                            Engineering,
                            Rome, Italy, June 2017
                        </li>
                        <li>
                            <strong><u>A. Hassanpour</u></strong>, <strong>L. Vayssieres</strong>, P. Bianucci,
                            &ldquo;<strong>Optical
                            and Structural Properties of Arrays of Ni-doped ZnO Nanorods Prepared by a Low Temperature
                            Hydrothermal Method</strong>&rdquo;, 12th International Conference On Optical Probes of Organic
                            and
                            Hybrid Semiconductors, Quebec city, QC, Canada, June 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>On Artificial Photosynthesis for Solar Water Splitting and Hydrogen
                            Generation</strong>&rdquo;, IEEE Summer School on Nanotechnology, Montreal, Quebec, Canada, June
                            2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Overview & Latest Advances in Aqueous Chemical Growth of Advanced
                            Hetero-Nanostructures</strong>&rdquo;, 9<sup>th</sup> International Conference on Materials for
                            Advanced Technology (ICMAT), Symposium L on Novel Solution Processes for Advanced Functional
                            Materials, Suntec, Singapore, June 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>On the Design, Performance & Stability of Advanced Heteronanostuctures for Solar
                            Water Splitting</strong>&rdquo;, 9<sup>th</sup> International Conference on Materials for
                            Advanced
                            Technology (ICMAT), Symposium F on Advanced Inorganic Materials and Thin Film Technology for
                            Solar
                            Energy Harvesting, Suntec, Singapore, June 2017
                        </li>
                        <li>
                            <strong>S.H. Shen</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Engineering
                            Surface Structures and Energetics of α-Fe<sub>2</sub>O<sub>3</sub> and p-Si for Efficient Solar
                            Water Splitting, Processes at the Semiconductor Solution Interface 7</strong>&rdquo;, 231st
                            Meeting
                            of The Electrochemical Society, New Orleans, LA, USA, May-June 2017
                        </li>
                        <li>
                            <strong><u>A. Hassanpour</u></strong>, <strong>L. Vayssieres</strong>, P. Bianucci,
                            &ldquo;<strong>Optical
                            and Structural Properties of Arrays of Mn-doped ZnO Nanorods Prepared by a Low Temperature
                            Hydrothermal Method</strong>&rdquo;, 2017 CAP-Canadian Association of Physicists Congress,
                            Kingston,
                            ON, Canada, May-June 2017
                        </li>
                        <li>
                            <strong>L.Vayssieres</strong> <span
                                class="invited">(<strong>Invited talk & Session chair</strong>)</span>,
                            &ldquo;<strong>On the design of advanced materials for efficient and cost-effective solar
                            (sea)water
                            splitting</strong>&rdquo;, 2017 Emerging Technologies Conference, Warsaw, Poland, May 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>On the Effects of Design, Interfacial Electronic Structure & Dimensions on the
                            Performance & Stability of Photoelectrodes for Solar Water Splitting</strong>&rdquo;,
                            12<sup>th</sup> Pacific Rim Conference on Ceramic and Glass Technology including Glass & Optical
                            Materials Division Meeting (PacRim12), Symposium 10 on Multifunctional Nanomaterials and Their
                            Heterostructures for Energy and Sensing Devices, Kona, HI, USA, May 2017
                        </li>
                        <li>
                            <u>M. Chowdhury</u>, <strong>X.J. Guan</strong>, A. Pant, X.H. Kong, M. G. Kibria, H. Guo, F.
                            Himpsel, <strong>L. Vayssieres</strong>, Z. Mi, &ldquo;<strong>High Efficiency and Highly Stable
                            Photocatalytic Overall Water Splitting on III-Nitride Nanowire Arrays</strong>&rdquo;, 2017
                            Spring
                            MRS Meeting, Phoenix, AZ, USA, April 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span
                                class="invited">(<strong>Invited talk & Session chair</strong>)</span>,
                            &ldquo;<strong>Dimensional, Interfacial, and Confinement Effects on the Performance and
                            Stability of
                            Low-Cost Photoelectrodes for Solar Water Splitting</strong>&rdquo;, 21<sup>st</sup> Topical
                            Meeting
                            of the International Society of Electrochemistry, Szeged, Hungary, April 2017
                        </li>
                        <li>
                            <strong>L.Vayssieres</strong> <span
                                class="invited">(<strong>Invited talk & Session chair</strong>)</span>,
                            &ldquo;<strong>Confinement effects in large bandgap oxide semiconductors</strong>&rdquo;,
                            International Conference on Energy Materials Nanotechnology (EMN-East), Siem Reap, Cambodia,
                            March
                            2017
                        </li>
                        <li>
                            <strong>S.H. Shen</strong> <span class="invited">(<strong>Invited talk</strong>)</span>,
                            &ldquo;<strong>Surface and Interface Engineered Heterostructures for Solar Hydrogen
                            Generation</strong>&rdquo;, Symposium 1- Materials for Solar Fuel Production and Applications in
                            Materials Challenges, Materials Challenges in Alternative and Renewable Energy 2017 (MCARE
                            2017),
                            Jeju, South Korea, February 2017
                        </li>
                    </ol>
                    <h5 align="center" class="h5" style="margin-top:15px; margin-bottom:0px;">2016 (43)</h5>
                    <ol style="list-style-type:decimal; margin: 30px; padding:30px 10px;" reversed start="241">

                        <li>
                            <strong><u>J.B. Huang</u></strong>, <strong>L. Wang</strong>, <strong>C. Zhu</strong>, <strong>H.
                            Jin</strong>, &ldquo;<strong>Catalytic Gasification of Guaiacol in Supercritical Water for
                            Hydrogen
                            Production</strong>&rdquo;, 8<sup>th</sup> International Symposium on Multiphase Flow, Heat &
                            Mass
                            Transfer and Energy Conversion (ISMF2016), Chengdu, China, December 2016
                        </li>
                        <li>
                            <strong><u>H.J. Jia</u></strong>, <strong>Y.P. Yang</strong>, <strong>H.T. Liu</strong>,
                            <strong>L.J.
                                Guo*</strong>,&ldquo;<strong>Systematic study on the effects of operation parameters on the
                            performance of open cathode PEM fuel cells</strong>&rdquo;, 8<sup>th</sup> International
                            Symposium
                            on Multiphase Flow, Heat & Mass Transfer and Energy Conversion (ISMF2016), Chengdu, China,
                            December
                            2016
                        </li>
                        <li>
                            <strong><u>J. Hu</u></strong>, X.Q. Wang, H.H. Yang, <strong>L.J. Guo*</strong>, &ldquo;<strong>Strong
                            pH Dependence of Hydrogen Production with Glucose in Rhodobacter sphaeroides</strong>&rdquo;,
                            8<sup>th</sup>
                            International Symposium on Multiphase Flow, Heat & Mass Transfer and Energy Conversion
                            (ISMF2016),
                            Chengdu, China, December 2016
                        </li>
                        <li>
                            <strong><u>S.Y. Ye</u></strong>, <strong>L.J. Guo*</strong>, <strong>Q. Xu</strong>, <strong>Y.S.
                            Chen</strong>, <strong>Q.Y. Chen</strong>, &ldquo;<strong>Investigation on Pressure Wave Induced
                            by
                            Supersonic Steam Jet Condensation in Water Flow in a Vertical Pipe</strong>&rdquo;,
                            8<sup>th</sup>
                            International Symposium on Multiphase Flow, Heat & Mass Transfer and Energy Conversion
                            (ISMF2016),
                            Chengdu, China, December 2016
                        </li>

                        <li>
                            <strong><u>R.Y. Wang</u></strong>, <strong>H. Jin</strong>, <strong>L.J. Guo*</strong>,
                            &ldquo;<strong>Thermodynamic analysis of supercritical water gasification and dechlorination of
                            o-chlorophenol</strong>&rdquo;, 8<sup>th</sup> International Symposium on Multiphase Flow, Heat
                            &
                            Mass Transfer and Energy Conversion (ISMF2016), Chengdu, China, December 2016
                        </li>
                        <li>
                            <strong><u>W. Zhou</u></strong>, <strong>L.Y. He</strong>, <strong>S.H. Shen*</strong>,
                            &ldquo;<strong>n-WO<sub>3</sub>/p-Si junctional photocathodes for efficient solar hydrogen
                            generation</strong>&rdquo;, 8<sup>th</sup> International Symposium on Multiphase Flow, Heat &
                            Mass
                            Transfer and Energy Conversion (ISMF2016), Chengdu, China, December 2016
                        </li>
                        <li>
                            <strong><u>W.L. Fu</u></strong>, <strong>M.C. Liu</strong>, <strong>F. Xue</strong>, <strong>L.J.
                            Guo*</strong>, &ldquo;<strong>Manipulating the Heterostructures of a Visible-Light-Driven
                            Composite
                            Photocatalyst by Controlling the Mass Transportation during Synthesis</strong>&rdquo;,
                            8<sup>th</sup> International Symposium on Multiphase Flow, Heat & Mass Transfer and Energy
                            Conversion (ISMF2016), Chengdu, China, December 2016
                        </li>
                        <li>
                            <strong>S.H. Shen</strong>, &ldquo;<strong>Noble-metal Free Artificial Photosynthesis Systems
                            for
                            Solar Hydrogen Generation</strong>&rdquo;, 8<sup>th</sup> International Symposium on Multiphase
                            Flow, Heat & Mass Transfer and Energy Conversion (ISMF2016), Chengdu, China, December 2016
                        </li>
                        <li>
                            <strong><u>J.F. Geng</u></strong>, <strong>Y.C. Wang</strong>, <strong>X.W. Hu</strong>,
                            <strong>D.W.
                                Jing*</strong>, &ldquo;<strong>Experimental and Theoretical Analysis of Particle Transient
                            Transport
                            Phenomenon in Flowing Suspension</strong>&rdquo;, 8<sup>th</sup> International Symposium on
                            Multiphase Flow, Heat & Mass Transfer and Energy Conversion (ISMF2016), Chengdu, China, December
                            2016
                        </li>
                        <li>
                            <strong><u>H. Jin</u></strong>, <strong>L.J. Guo</strong>, <strong>Z.Q. Wu</strong>, <strong>X.
                            Zhang</strong>, <strong>J. Chen</strong> <span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>Novel ABO<sub>3</sub>-based Materials: Tailored Components and Structures towards
                            Photocatalytic H<sub>2</sub> Evolution under Visible-light Irradiation</strong>&rdquo;,
                            8<sup>th</sup> International Symposium on Multiphase Flow, Heat & Mass Transfer and Energy
                            Conversion (ISMF2016), Chengdu, China, December 2016
                        </li>
                        <li>
                            <strong>J.W. Shi</strong> <span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>Novel
                            ABO<sub>3</sub>-based Materials: Tailored Components and Structures towards Photocatalytic
                            H<sub>2</sub> Evolution under Visible-light Irradiation</strong>&rdquo;, 8<sup>th</sup>
                            International Symposium on Multiphase Flow, Heat & Mass Transfer and Energy Conversion
                            (ISMF2016),
                            Chengdu, China, December 2016
                        </li>
                        <li>
                            <strong>M.C. Liu</strong> <span
                                class="invited">(<strong>Keynote &amp; Session chair</strong>)</span>, &ldquo;<strong>Controlling
                            Mass Transportation in Synthesizing Photocatalytic Nanocrystals for Solar H<sub>2</sub>
                            Production</strong>&rdquo;, 8<sup>th</sup> International Symposium on Multiphase Flow, Heat &
                            Mass
                            Transfer and Energy Conversion (ISMF2016), Chengdu, China, December 2016
                        </li>
                        <li>
                            <strong>M. Fronzi</strong> <span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>Nano
                            cluster modified TiO<sub>2</sub> anatase and rutile surfaces for photo-catalytic
                            processes</strong>&rdquo;,
                            8<sup>th</sup> International Symposium on Multiphase Flow, Heat & Mass Transfer and Energy
                            Conversion (ISMF2016), Chengdu, China, December 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Plenary</strong>)</span>,
                            &ldquo;<strong>Low Cost HeteroNanostructures for Solar Hydrogen Generation</strong>&rdquo;,
                            8<sup>th</sup> International Symposium on Multiphase Flow, Heat & Mass Transfer and Energy
                            Conversion (ISMF2016), Chengdu, China, December 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>Low Cost HeteroNanostructures for Solar Water Splitting</strong>&rdquo;,
                            2<sup>nd</sup> Mexico-China Workshop on Nano: Materials / Science / Technology (NANOMXCN-2016),
                            Hong
                            Kong, China, December 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Latest advances in low cost semiconductor heteronanostructures for water
                            splitting</strong>&rdquo;, 72<sup>nd</sup> American Chemical Society (ACS) Southwest Regional
                            Meeting, Symposium on Applications of Photonics in Energy and the Life Sciences, Galveston, TX,
                            USA,
                            November 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Plenary</strong>)</span>,
                            &ldquo;<strong>Low-cost HeteroNanostructures for Solar Water Splitting</strong>&rdquo;,
                            3<sup>rd </sup>International Workshop on Advanced Materials and Nanotechnology, Hanoi, Vietnam,
                            November 2016
                        </li>
                        <li>
                            <strong><u>F.J. Niu</u></strong>, <strong>Y. Yu</strong>, <strong>S.H. Shen*</strong>, <strong>L.J.
                            Guo</strong>, &ldquo;<strong>A Novel Hybrid Artificial Photosynthesis System with
                            MoS<sub>2</sub>
                            Embedded Carbon Nanofibers as Electron Relay and Hydrogen Evolution Catalyst</strong>&rdquo;,
                            17<sup>th </sup>IUMRS International Conference in Asia (IUMRS-ICA2016), Qingdao, China, October
                            2016
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Latest development in design strategies for efficient solar water splitting
                            photoelectrodes</strong>&rdquo;, 230<sup>th</sup> Electrochemical Society Meeting, Symposium
                            Photocatalysts, Photoelectrochemical Cells, and Solar Fuels 7, PRiME 2016, Honolulu, HI, USA,
                            October 2016
                        </li>
                        <li>
                            <strong><u>R. Song</u></strong>, <strong>B. Luo</strong>, <strong>D.W. Jing</strong>,
                            &ldquo;<strong>Efficient Photothermal Catalytic Hydrogen Production over Nonplasmonic Pt Metal
                            Supported on TiO<sub>2</sub></strong>&rdquo;, Solar Hydrogen and Nanotechnology XI, SPIE Optics
                            and
                            Photonics, San Diego, USA, August 2016
                        </li>
                        <li>
                            <strong><u>Y. Liu</u></strong><span class="invited"></span>, Y.H. Guo, J. Ager, <strong>M.T.
                            Li</strong>, &ldquo;<STRONG>Fabrication of CoOx Layer on Porous BiVO<sub>4</sub> Film for Water
                            Splitting</STRONG>&rdquo;, Solar Hydrogen and Nanotechnology XI, SPIE Optics and Photonics, San
                            Diego, USA, August 2016
                        </li>
                        <li>
                            <strong><u>Y. Liu</u></strong><span class="invited"></span>, <strong>S.H. Shen</strong> <span
                                class="invited">(<strong>Invited</strong>)</span>, &ldquo;<strong>Heterostructures for
                            Photoelectrochemical and Photocatalytic Hydrogen Generation</strong>&rdquo;, Solar Hydrogen and
                            Nanotechnology XI, SPIE Optics and Photonics, San Diego, USA, August 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>On the design of new low cost photocatalysts for efficient solar water
                            oxidation</strong>&rdquo;, 252<sup>nd</sup> ACS National Meeting, Symposium on Solar Fuels:
                            Power to
                            the People, Philadelphia, PA, August 2016
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Heterostructures
                            for Solar Hydrogen Generation</strong>&rdquo;, 3<sup>rd</sup> International Conference on
                            Electrochemical Energy Science and Technology (EEST2016), Kunming, China, August 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>On confinement, </strong><strong>surface </strong><strong>&amp; dimensionality
                            effects in oxide semiconductors for solar water oxidation</strong>&rdquo;, XXV International
                            Materials Research Congress, Symposium on Advances on Solar Fuels/Artificial Photosynthesis:
                            Materials and Devices, Cancun, Mexico, August 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Low cost advanced materials design strategies for efficient solar energy
                            conversion</strong>&rdquo;, XXV International Materials Research Congress, Symposium on
                            Materials
                            and Technologies for Energy Conversion, Saving and Storage (MATECSS), Cancun, Mexico, August
                            2016
                        </li>
                        <li>
                            <strong><u>D.M. Zhao</u></strong>, <strong>S.H. Shen*</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>ITO Electronic Pump Boosting Photocatalytic Hydrogen Evolution over Graphitic
                            Carbon
                            Nitride</strong>&rdquo;, 2<sup>nd</sup> International Conference on Nanoenergy and Nanosystems
                            2016
                            (NENS2016), Beijing, China, July 2016
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Engineering
                            One-Dimensional Hematite Photoanodes for Solar Water Splitting</strong>&rdquo;, 2<sup>nd</sup>
                            International Conference on Nanoenergy and Nanosystems 2016 (NENS2016), Beijing, China, July
                            2016
                        </li>
                        <li>
                            <strong>M.T. Li</strong> <span class="invited">(<strong>Invited</strong>)</span>, &ldquo;<span
                                lang="EN-GB"><strong>Photo/Electrocatalysis: Mechanistic Insight and Catalyst Design from Density Functional Theory</strong></span>&rdquo;,
                            Global Forum on Advanced Materials and Technologies for Sustainable Development, Symposium G2 on
                            Functional Nanomaterials for Sustainable Energy Technologies, Toronto, Canada, June 2016
                        </li>
                        <li>
                            <strong><u>X.J. Guan</u></strong>, F. Chowdhury, <strong>L. Vayssieres</strong>, <strong>L.J.
                            Guo</strong>, Z. Mi, &ldquo;<strong>Photocatalytic Seawater Splitting on Metal Nitride
                            Nanowires</strong>&rdquo;, Global Forum on Advanced Materials and Technologies for Sustainable
                            Development, Symposium G2 on Functional Nanomaterials for Sustainable Energy Technologies,
                            Toronto,
                            Canada, June 2016
                        </li>
                        <li>
                            <strong><u>Y.B. Chen</u></strong> <span
                                class="invited">(<strong>Invited</strong>)</span>,<strong>
                            Z.X. Qin</strong>, <strong>X.J. Guan</strong>, <strong>M.C. Liu</strong>, &ldquo;<strong>One-pot
                            Synthesis of Heterostructured Photocatalysts for Improved Solar-to-Hydrogen Conversion</strong>&rdquo;,
                            Global Forum on Advanced Materials and Technologies for Sustainable Development, Symposium G2 on
                            Functional Nanomaterials for Sustainable Energy Technologies, Toronto, Canada, June 2016
                        </li>
                        <li>
                            <strong><u>M.C. Liu</u></strong>, <strong>X.X. Wang</strong>, <strong>L.
                            Zhao</strong>,&ldquo;<strong>Shape-Controlled Metal/Semiconductor Nanocrystals in a
                            Well-Controlled
                            Kinetic Process and Their Application for Electrocatalysis or Photocatalysis</strong>&rdquo;,
                            Global
                            Forum on Advanced Materials and Technologies for Sustainable Development, Symposium G2 on
                            Functional
                            Nanomaterials for Sustainable Energy Technologies, Toronto, Canada, June 2016
                        </li>
                        <li>
                            <strong>M.C. Liu</strong>, &ldquo;<strong>Crystal-facets Dependent Solar Hydrogen Generation
                            from
                            Kinetic Growth Controlled Nanoparticles</strong>&rdquo;, 2<sup>nd</sup> International Symposium
                            on
                            Energy Conversion and Storage, Xiamen, China, June 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span
                                class="invited">(<strong>Invited talk & Session chair</strong>)</span>,
                            &ldquo;<span
                                lang="EN-GB"><strong>New Design Strategy for Advanced Photocatalysts</strong></span>&rdquo;,
                            Global Forum on Advanced Materials and Technologies for Sustainable Development, Symposium G2 on
                            Functional Nanomaterials for Sustainable Energy Technologies, Toronto, Canada, June 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>On the design of advanced photocatalysts for solar water splitting</strong>&rdquo;,
                            Emerging Technologies 2016 Conference, Session on Optoelectronics &amp; Photonics, Montreal, QC,
                            Canada, May 2016
                        </li>
                        <li>
                            <strong>S.H. Shen</strong>
                            <span class="invited">(<strong>Invited</strong>)</span>, &ldquo;<strong>1D metal oxides for
                            solar
                            water splitting</strong>&rdquo;, Workshop on Advanced Energy Materials &amp; X-ray Spectroscopy,
                            Tamkang University, Taipei, May 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Interfacial and confinement effects in oxide semiconductors</strong>&rdquo;,
                            Workshop
                            on Advanced Energy Materials &amp; X-ray Spectroscopy, Tamkang University, Taipei, May 2016
                        </li>
                        <li>
                            <strong>L.J. Guo</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Solar
                            hydrogen: Harvesting light and heat from Sun</strong>&rdquo;, Workshop on Advanced Energy
                            Materials
                            &amp; X-ray Spectroscopy, Tamkang University, Taipei, May 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Morphological, dimensional, and interfacial effects on oxide semiconductor
                            efficiency
                            for solar water splitting</strong>&rdquo;, American Ceramic Society Materials Challenges in
                            Alternative &amp; Renewable Energy 2016 Conference, Clearwater, FL, April 2016
                        </li>
                        <li>
                            <strong>L.Vayssieres</strong> <span
                                class="invited">(<strong>Invited talk & Session chair</strong>)</span>,
                            &ldquo;<strong>Latest Advances in Solar Water Splitting</strong>&rdquo;, 2016 Spring MRS
                            Meeting,
                            Symposium EE2: Advancements in Solar Fuels Generation: Materials, Devices and Systems, Phoenix,
                            AZ,
                            March 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span
                                class="invited">(<strong>Invited talk & Session chair</strong>)</span>,
                            &ldquo;<strong><span
                                lang="EN-GB">Latest Advances in Low Cost Solar Water Splitting</span></strong>&rdquo;,
                            2<sup>nd</sup> Fusion Conference on Molecules and Materials for Artificial Photosynthesis,
                            Cancun,
                            Mexico, February 2016
                        </li>
                        <li>
                            <strong>S.H. Shen</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Nanodesigned
                            Materials for Photoelectrochemical and Photocatalytic Solar Hydrogen Generation</strong>&rdquo;,
                            2<sup>nd</sup> Fusion Conference on Molecules and Materials for Artificial Photosynthesis
                            Conference, Cancun, Mexico, February 2016
                        </li>
                        <li>
                            <strong>S.H. Shen</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>One-dimensional
                            Metal Oxides for Solar Water Splitting</strong>&rdquo;, The 6<sup>th</sup> China-Australia Joint
                            Symposium on Energy and Biomedical Materials, Suzhou, China, January 2016
                        </li>
                    </ol>
                    <h5 align="center" class="h5" style="margin-top:15px; margin-bottom:0px;">2015 (50)</h5>
                    <ol style="list-style-type:decimal; margin: 30px; padding:30px 10px;" reversed start="198">
                        <li>
                            <strong><u>B. Wang</u></strong>, <strong>S.H. Shen*</strong>, <strong>L.J. Guo*</strong>,
                            “<strong>Hydrogenation
                            of {023} and {001} Facets Enclosed SrTIO<sub>3</sub> Single Crystals for Photocatalytic Hydrogen
                            Evolution</strong>”, 5<sup>th</sup> Asia-Pacific Forum on Renewable Energy, HF: Hydrogen &amp;
                            Fuel
                            Cell, Jeju, Korea, November 2015
                        </li>
                        <li>
                            <strong><u>X.X. Wang</u></strong>, <strong>M.C. Liu</strong>, <strong>Z.H. Zhou</strong>,
                            <strong>L.J.
                                Guo*</strong>, “<strong>Crystal-Facets Dependent Solar Hydrogen Generation from Kinetic
                            Growth
                            Controlled CdS Nanoparticles</strong>”, 5<sup>th</sup> Asia-Pacific Forum on Renewable Energy,
                            HF:
                            Hydrogen &amp; Fuel Cell, Jeju, Korea, November 2015
                        </li>
                        <li>
                            <strong><u>J. Wang</u></strong>, <strong>J.Z. Su</strong>, <strong>L. Vayssieres*</strong>,
                            <strong>L.J.
                                Guo*</strong>, “<strong>Controlled Synthesis of Porous Hematite Nanoplate Arrays for Solar
                            Water
                            Splitting: Towards Efficient Electron-Hole Separation</strong>”, 5<sup>th</sup> Asia-Pacific
                            Forum
                            on Renewable Energy, HF: Hydrogen &amp; Fuel Cell, Jeju, Korea, November 2015
                        </li>
                        <li>
                            <strong><u>X.K. Wan</u></strong>, <strong>F.J. Niu</strong>, <strong>J.Z. Su</strong>, <strong>L.J.
                            Guo*</strong>, “<strong>Reduced Graphene Oxide Modification and Tungsten Doping for Enhanced
                            Photoelectrochemical Water Oxidation of Bismuth Vanadate</strong>”, 5<sup>th</sup> Asia-Pacific
                            Forum on Renewable Energy, HF: Hydrogen &amp; Fuel Cell, Jeju, Korea, November 2015
                        </li>
                        <li>
                            <strong><u>G.Y. Chen</u></strong>, <strong>L.J. Guo*</strong>, <strong>H.T. Liu*</strong>,
                            “<strong>The
                            Relationship Between the Double Layer Capacitance and Water Content in the Cathode Catalyst
                            Layer</strong>”, 5<sup>th</sup> Asia-Pacific Forum on Renewable Energy, HF: Hydrogen &amp; Fuel
                            Cell, Jeju, Korea, November 2015
                        </li>
                        <li>
                            <strong><u>X.Q.&nbsp;Wang</u></strong>,&nbsp;<strong>H.H.&nbsp;Yang*</strong>,<strong>&nbsp;Y.&nbsp;Zhang</strong>,&nbsp;<strong>L.J.&nbsp;Guo*</strong>,
                            “<strong>Isolation enhanced hydrogen production of CBB deactivation Rhodobacter sphaeroides
                            mutant
                            by using transposon mutagenesis in the present of NH<sub>4</sub><sup>+</sup></strong>”,
                            5<sup>th</sup> Asia-Pacific Forum on Renewable Energy, HF: Hydrogen &amp; Fuel Cell, Jeju,
                            Korea,
                            November 2015
                        </li>
                        <li>
                            <strong><u>Y. Zhang</u></strong>, <strong>H.H. Yang</strong>, <strong>J.L. Feng</strong>,
                            <strong>L.J.&nbsp;Guo*</strong>,
                            &ldquo;<strong>Overexpression of F0 operon and F1 operon of ATPase in Rhodobacter sphaeroides
                            enhanced its photo-fermentative hydrogen production</strong>&rdquo;, 5<sup>th</sup> Asia-Pacific
                            Forum on Renewable Energy, HF: Hydrogen &amp; Fuel Cell, Jeju, Korea, November 2015
                        </li>
                        <li>
                            <strong><u>Y. Zhang</u></strong>, J. Hu, <strong>H.H. Yang</strong>,
                            <strong>L.J.&nbsp;Guo*</strong>,
                            &ldquo;<strong>Bio-hydrogen production by co-culture of Enterobacter cloacae YA012 and
                            Rhodobacter
                            sphaeroides HY01</strong>&rdquo;, 5<sup>th</sup> Asia-Pacific Forum on Renewable Energy, HF:
                            Hydrogen &amp; Fuel Cell, Jeju, Korea, November 2015
                        </li>
                        <li>
                            <strong>S.H. Shen</strong> <span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>One
                            Dimensional Metal Oxides for Solar Water Splitting</strong>&rdquo;, 3<sup>rd</sup> International
                            Workshop on Nanotechnology, Renewable Energy &amp; Sustainability, Xi'an, P. R. China,
                            September,
                            2015
                        </li>
                        <li>
                            <strong>M.C. Liu</strong>, “<strong>Facet-engineered chalcogenide photocatalyst for enhanced
                            solar
                            hydrogen production: charge separation and surface activation</strong>”, 14<sup>th</sup>
                            International Conference on Clean Energy (ICCE 2015), Saskatoon, Canada, September 2015
                        </li>
                        <li>
                            <strong><u>X.J. Guan</u></strong>, <strong>L.J. Guo</strong>, “<strong>Facet engineered bismuth
                            vanadate for highly efficient photocatalytic water oxidation</strong>”, 14<sup>th</sup>
                            International Conference on Clean Energy (ICCE 2015), Saskatoon, Canada, September 2015
                        </li>
                        <li>
                            <strong><u>Y.P. Yang</u></strong>, <strong>H.T. Liu*</strong>,<strong> L.J.&nbsp;Guo*</strong>,
                            &ldquo;<strong>Optimization of operating conditions in PEM fuel cells with dead-ended
                            anode</strong>”,
                            14<sup>th</sup> International Conference on Clean Energy (ICCE 2015), Saskatoon, Canada,
                            September
                            2015
                        </li>
                        <li>
                            <strong><u>X.Q.&nbsp;Wang</u></strong>,
                            <strong>H.H.&nbsp;Yang*</strong>,&nbsp;<strong>L.J.</strong>&nbsp;<strong>Guo*</strong>,
                            “<strong>Enhancement of hydrogen production performance by the double mutant from cbbR knochout
                            strain via transposon mutagenensis</strong>”, 14<sup>th</sup> International Conference on Clean
                            Energy (ICCE 2015), Saskatoon, Canada, September 2015
                        </li>
                        <li>
                            <strong><u>X. Zhang</u></strong>, <strong>L.J.&nbsp;Guo*</strong>, <strong>H.T.
                            Liu</strong><strong>*</strong>,
                            “<strong>Mass transport degradation caused by carbon corrosion in proton exchange membrane fuel
                            cells</strong>”, 14<sup>th</sup> International Conference on Clean Energy (ICCE 2015),
                            Saskatoon,
                            Canada, September 2015
                        </li>
                        <li style="padding-top:0px;">
                            <strong>L. Vayssieres </strong><span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>Advanced metal oxide arrays by aqueous chemical
                            growth</strong>&rdquo;, EUROMAT-<span
                                name="European Congress and Exhibition on Advanced Materials and Processes registration">European Congress and Exhibition on Advanced Materials and Processes</span>,
                            Symposium C3.2: Assembly-Mediated and Surface-Based Coatings, Warsaw, Poland, September 2015
                        </li>
                        <li>
                            <STRONG>L. Vayssieres </STRONG><span class="invited">(<STRONG>Invited</STRONG>)</span>,
                            &ldquo;<STRONG>Interfacial, Dimensionality, and Confinement effects in Oxide
                            Semiconductors</STRONG>&rdquo;,
                            International Exploratory Workshop on Photoelectrochemistry, Catalysis and X-ray
                            Spectroscopy, EMPA
                            - Swiss Federal Laboratories for Materials Science &amp; Technology, Dubendorf, Switzerland,
                            August
                            2015
                        </li>
                        <li>
                            <STRONG>L. Vayssieres </STRONG><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<STRONG></STRONG><STRONG>Latest advances in low-cost solar water splitting
                            nanodevices</STRONG><STRONG></STRONG>&rdquo;, SPIE Optics &amp; Photonics Nanoscience
                            Engineering,
                            Symposium on Low-Dimensional Materials and Devices, San Diego, CA, August 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span
                                class="invited">(<strong>Keynote &amp; Session Chairs</strong>)</span>,
                            &ldquo;<strong>On the surface, confinement and dimensionality effects of large bandgap oxide
                            semiconductors</strong>&rdquo;, SPIE Optics &amp; Photonics, Symposium on Solar Hydrogen &amp;
                            Nanotechnology X, San Diego, CA, August 2015
                        </li>
                        <li>
                            <strong>L.J. Guo </strong><span class="invited">(<strong>Keynote</strong></strong>)</span>,
                            <strong><u>S.H.
                                Shen</u></strong>, “<strong>Low-cost and high-efficiency solar hydrogen conversion: On
                            materials
                            design and pilot-scale demonstration</strong>”, SPIE Optics &amp; Photonics, Symposium on Solar
                            Hydrogen &amp; Nanotechnology X, San Diego, CA, August 2015
                        </li>
                        <li>
                            <strong>L.J. Guo</strong> <span class="invited">(<STRONG>Plenary</STRONG>)</span>, <strong><u>D.W.
                            Jing</u></strong>, “<strong>Solar hydrogen: harvesting light and heat from sun</strong>”, SPIE
                            Optics &amp; Photonics, Symposium on Solar Hydrogen &amp; Nanotechnology X, San Diego, CA,
                            August
                            2015
                        </li>
                        <li>
                            <strong>D.W. Jing </strong><span class="invited">(</span><span
                                class="invited"><strong>Invited</strong></span><span class="invited">)</span>, “<strong>Experimental
                            and numerical study on an annular fluidized-bed photocatalytic reactor</strong>”, SPIE Optics
                            &amp;
                            Photonics, Symposium on Solar Hydrogen &amp; Nanotechnology X, San Diego, CA, August 2015
                        </li>
                        <li>
                            X.J. Feng <strong> </strong><span class="invited">(</span><span
                                class="invited"><strong>Invited</strong></span><span class="invited">)</span>, <strong><u>J.Z.
                            Su</u></strong>, “<strong>Synthesis and assembly of 1D inorganic semiconductor for solar energy
                            conversion</strong>”, SPIE Optics &amp; Photonics, Symposium on Solar Hydrogen &amp;
                            Nanotechnology
                            X, San Diego, CA, August 2015
                        </li>
                        <li>
                            <u>F.J. Himpsel</u> <span class="invited">(<strong>Keynote</strong>)</span>, W.L. Yang, D.
                            Prendergast, C.X. Kronawitter, Z. Mi, <strong>L. Vayssieres</strong>, &ldquo;<strong>Synchrotron-based
                            spectroscopy for solar energy conversion</strong>&rdquo;, SPIE Optics &amp; Photonics, Symposium
                            on
                            Solar Hydrogen &amp; Nanotechnology X, San Diego, CA, August 2015
                        </li>
                        <li>
                            <strong>J.Z. Su</strong>, “<strong>High aspect ratio WO<sub>3</sub> nanorod arrays based
                            WO<sub>3</sub>/BiVO<sub>4</sub> Heterojunction for photoelectrochemical water splitting</strong>”,
                            SPIE Optics &amp; Photonics, Symposium on Solar Hydrogen &amp; Nanotechnology X, San Diego, CA,
                            August 2015
                        </li>
                        <li>
                            <strong><u>Y.B. Chen</u></strong>, <strong>Z.X. Qin</strong>, <strong>L.J. Guo</strong>,
                            “<strong>Electrophoretic
                            deposition of composition-tunable (Cu<sub>2</sub>Sn)xZn<sub>3(1-x)</sub>S<sub>3</sub>
                            nanocrystal
                            films as efficient photocathodes for photoelectrochemical water splitting</strong>”, SPIE Optics
                            &amp; Photonics, Symposium on Solar Hydrogen &amp; Nanotechnology X, San Diego, CA, August 2015
                        </li>
                        <li>
                            <U><strong>J.W. Shi</strong></u>, <strong>Y.Z. Zhang</strong>, <strong>L.J. Guo</strong>,
                            “<strong>NH<sub>3</sub>-treated
                            MoS<sub>2</sub> nanosheets for enhanced H<sub>2</sub> evolution under visible-light
                            irradiation</strong>”, SPIE Optics &amp; Photonics, Symposium on Solar Hydrogen &amp;
                            Nanotechnology
                            X, San Diego, CA, August 2015
                        </li>
                        <li>
                            <strong><u>L.J. Ma</u></strong>, <strong>L.J. Guo</strong>, “<strong>Photocatalytic hydrogen
                            production over CdS: Effects of reaction atmosphere studied by in situ Raman
                            spectroscopy</strong>”,
                            SPIE Optics &amp; Photonics, Symposium on Solar Hydrogen &amp; Nanotechnology X, San Diego, CA,
                            August 2015
                        </li>
                        <li>
                            <strong>S.H. Shen</strong> <span class="invited">(<strong>Invited</strong>)</span>, “<strong>Doping
                            and Surface Engineering to Metal Oxide Nanorods for Photoelectrochemical Water
                            Splitting</strong>”,
                            5<sup>th</sup> Young Scholars Symposium on Nano & New Energy Technology, Suzhou, China, August
                            2015
                        </li>
                        <li>
                            <strong><u>J.W. Shi</u> </strong><span class="invited">(</span><span
                                class="invited"><strong>Invited</strong></span><span class="invited">)</span>, <strong>Y.Z.
                            Zhang</strong>, <strong>L.J. Guo</strong>, “<strong>Molybdenum sulfide nanosheets: ammonia
                            post-treatment towards improved visible-light-driven hydrogen production</strong>”, Mexico-China
                            workshop on Nanomaterials, Nanoscience and Nanotechnology: Renewable energy and water
                            remediation,
                            XXIV International Materials Research Congress, Cancun, Mexico, August 2015
                        </li>
                        <li>
                            <strong>J.Z. Su</strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            “<strong>WO<sub>3</sub>/BIVO<sub>4</sub> Nanowire Heterojunction for Photoelectrochemical Water
                            Oxidation</strong>”, Mexico-China workshop on Nanomaterials, Nanoscience and Nanotechnology:
                            Renewable energy and water remediation, XXIV International Materials Research Congress, Cancun,
                            Mexico, August 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span
                                class="invited">(<strong>Invited talk &amp; Session chair</strong>)</span>, &ldquo;<strong>Quantum-confined
                            oxide arrays from aqueous solutions</strong>&rdquo;, 8<sup>th</sup> International Conference on
                            Materials for Advanced Technology (ICMAT), Symposium R on Novel solution processes for advanced
                            functional materials, Suntec, Singapore, June-July 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span
                                class="invited">(<strong>Invited talk &amp; Session chair</strong>)</span>, &ldquo;<strong>Aqueous
                            chemical growth of visible light-active oxide semiconductors</strong>&rdquo;, 98<sup>th</sup>
                            Canadian Chemistry Conference &amp; Exhibition, Division of Materials Chemistry, Symposium on
                            Nanostructured Materials for Solar Energy Conversion and Storage, Ottawa, Canada, June 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Low Cost Nanodevices for Solar Water Splitting</strong>&rdquo;, CMOS Emerging
                            Technologies Research Conference, Vancouver, BC, Canada, May 2015 
                        </li>
                        <li>
                            <STRONG>J.J. Wei </STRONG><span class="invited">(<STRONG>Invited</STRONG>)</span>,
                            &ldquo;<STRONG>Study
                            of concentrating solar photovoltaic-thermal hybrid system</STRONG>&rdquo;, 8<sup>th</sup> International
                            Conference on Energy Materials Nanotechnology (EMN East), Beijing, China, April 2015
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>1-D
                            metal oxide nanomaterials for efficient solar water splitting</strong>&rdquo;, 8<sup>th</sup>
                            International Conference on Energy Materials Nanotechnology (EMN East), Symposium on
                            Nanomaterials
                            &amp; Nanotechnology, Beijing, China, April 2015
                        </li>
                        <li>
                            <STRONG>L. Vayssieres </STRONG><span class="invited">(<STRONG>Plenary</STRONG>)</span>,
                            &ldquo;<strong>Confinement effects in large bandgap oxide semiconductors</strong>&rdquo;,
                            8<sup>th</sup> International Conference on Energy Materials Nanotechnology (EMN East), Beijing,
                            China, April 2015
                        </li>
                        <li>
                            <strong>M.C. Liu </strong><span class="invited">(</span><strong><span
                                class="invited">Invited</span></strong><span
                                class="invited">)</span>, “<strong>Twin-induced ordered homojunction for efficient solar
                            hydrogen production</strong>”, 8<sup>th</sup> International Conference on Energy Materials
                            Nanotechnology (EMN East), Beijing, China, April 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span
                                class="invited">(<strong>Invited</strong> <strong>talk &amp; Session chair</strong>)</span>,
                            &ldquo;<strong>Advanced growth control of oxide nanostructures in water</strong>&rdquo;, 2015
                            MRS
                            Spring Meeting, Symposium RR: Solution Syntheses of Inorganic Functional/Multifunctional
                            Materials,
                            San Francisco, CA, USA, April 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Interfacial engineering of large bandgap oxide nanostructures for solar energy
                            conversion</strong>&rdquo;, 2015 MRS Spring Meeting, Symposium FF: Defects in
                            Semiconductors-Relationship to Optoelectronic Properties, San Francisco, CA, USA, April 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>Advanced low cost energy materials from aqueous solutions</strong>&rdquo;, 2015
                            MRS
                            Spring Meeting, Symposium X: Frontiers of Materials Research, San Francisco, CA, USA, April 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Quantum size effects in Anatase
                            TiO</strong><strong><sub>2</sub> nanoparticles</strong>&rdquo;, 2015 MRS Spring Meeting,
                            Symposium
                            UU: Titanium Oxides-From Fundamental Understanding to Applications, San Francisco, CA, USA,
                            April
                            2015
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Metal oxide (hetero)nanostructures: Surface chemistry, interfacial electronic
                            structure, dimensionality effect and efficiency optimization</strong>&rdquo;, 2015 MRS Spring
                            Meeting, Symposium TT: Metal Oxides-From Advanced Fabrication and Interfaces to Energy and
                            Sensing
                            Applications, San Francisco, CA, USA, April 2015
                        </li>
                        <li>
                            <strong>S.H. Shen</strong> <span class="invited">(<strong>Invited</strong>)</span>, “<strong>Nanorod
                            structured hematite photoanodes: metal doping and surface engineering towards efficient solar
                            water
                            splitting</strong>”, 2015 MRS Spring Meeting &amp; Exhibit, Symposium J: Latest Advances in
                            Solar
                            Water Splitting, San Francisco, CA, USA, April 2015<BR>
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>On the effects of surface and dimensionality of oxide photocatalysts for water
                            splitting</strong>&rdquo;, 249<sup>th </sup>American Chemical Society National Meeting &amp;
                            Exposition, Symposium on Nanostructured Materials for Solar Energy Conversion and Storage,
                            Denver,
                            CO, USA, March 2015
                        </li>
                        <li>
                            <U><strong>Y. Hu</strong></U>, <strong>S.H. Shen</strong> <span
                                class="invited">(</span><strong><span class="invited">Invited</span></strong><span
                                class="invited">)</span>, <strong>M.C. Liu</strong>, &ldquo;<strong>1D nanostructures design
                            for
                            efficient solar water splitting</strong>&rdquo;, 249<sup>th</sup> American Chemical Society
                            National
                            Meeting &amp; Exposition, Symposium on Nanostructured Materials for Solar Energy Conversion and
                            Storage, Denver, CO, USA, March 2015<BR>
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Low cost quantum-confined oxide arrays for solar water splitting</strong>&rdquo;,
                            American Ceramic Society Materials Challenges in Alternative &amp; Renewable Energy
                            2015, Symposium on Hydrogen Energy: Water Splitting &amp; Energy Application, Jeju, South Korea,
                            February 2015
                        </li>
                        <li>
                            <strong>S.H. Shen</strong> <span class="invited">(<strong>Invited</strong>)</span>, “<strong>Metal
                            doping and surface engineering for efficient solar water splitting over hematite nanorod
                            photoanodes</strong>”, Materials Challenges in Alternative &amp; Renewable Energy (MCARE 2015),
                            Symposium 1: Hydrogen Energy-Water Splitting and Energy Application, Jeju, South Korea, February
                            2015
                        </li>
                        <li>
                            <strong><u>M.C. Liu</u></strong>,<strong> N.X. Li</strong>, <strong>Z.H. Zhou</strong>,<strong>
                            J.C.
                            Zhou</strong>,<strong> Y.M. Sun</strong>,<strong> L.J. Guo</strong>, “<strong>Using
                            photooxidative
                            etching as a new approach to the determination of charge separation in faceted chalcogenide
                            photocatalysts</strong>”, Materials Challenges in Alternative &amp; Renewable Energy (MCARE
                            2015),
                            Jeju, South Korea, February 2015
                        </li>
                        <li>
                            <strong><u>M. Wang</u></strong>, M. Pyeon, Y. Gönüllü, A. Kaouk,<strong> S. H.
                            Shen</strong>,<strong> S. Mathur</strong>, <strong>and L. J. Guo</strong>, “<strong>Double
                            Layered
                            TiO<sub>2</sub>@Fe<sub>2</sub>O<sub>3</sub> Photoelectrodes with “Z-Scheme” Structure for
                            Efficient
                            Photoelectrochemical (PEC) Water Splitting</strong>”, Materials Challenges in Alternative &amp;
                            Renewable Energy (MCARE 2015), Jeju, South Korea, February 2015
                        </li>
                        <li>
                            <strong>S.H. Shen</strong> <span class="invited">(<strong>Invited</strong>)</span>, “<strong>Surface
                            engineered doping of hematite nanorod arrays for efficient solar water splitting</strong>”,
                            39<sup>th</sup>
                            International Conference and Expo on Advanced Ceramics and Composites, Symposium 7:
                            9<sup>th</sup>
                            International Symposium on Nanostructured Materials: Innovative Synthesis and Processing of
                            Nanostructured, Nanocomposite and Hybrid Functional Materials for Energy, Health and
                            Sustainability,
                            Daytona Beach, Florida, USA, January 2015
                        </li>
                    </ol>
                    <h5 align="center" class="h5" style="margin-top:15px; margin-bottom:0px;">2014 (52)</h5>
                    <ol style="list-style-type:decimal; margin: 30px; padding:30px 10px;" reversed start="148">
                        <li>
                            <strong>L.J. Guo</strong>, Advanced Innovation and development Symposium of Energy and Chemical
                            Industry, Xi’an, Shaanxi, China, December 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span
                                class="invited">(<strong>Invited talk &amp; Session chair</strong>)</span>, &ldquo;<strong>Low
                            Cost Metal Oxides for Solar Water Splitting: Quantum Confinement Effects, Interfacial Electronic
                            Structure and Aqueous Surface Chemistry</strong>&rdquo;, 2014 MRS Fall Meeting, Symposium V:
                            Sustainable Solar-Energy Conversion Using Earth-Abundant Materials, Boston, MA, USA, November
                            2014 
                        </li>
                        <li>
                            <strong>L.J. Guo</strong> <span
                                class="invited">(<strong>Invited talk &amp; Session chair</strong>)</span>,
                            “<strong>The fundamental research of large-scale hydrogen production utilizing solar
                            energy</strong>”,
                            15<sup>th</sup> National Conference on Hydrogen Energy-7<sup>th</sup> Hydrogen Energy Seminar
                            for
                            the Chinese mainland, Hong Kong, Macao and Taiwan, Symposium A on Hydrogen Production Technology
                            and
                            Its Application like Using Renewable energy, Chemical technology and others, Shanghai, China,
                            November 2014
                        </li>
                        <li>
                            <strong><u>Z.W. Ge</u></strong> <span class="invited">(<strong>Invited</strong>)</span>,
                            <strong>L.J.
                                Guo*</strong>, <strong>X.M. Zhang</strong>, <strong>S.K. Liu</strong>, <strong>H.
                            Jin</strong>,
                            “<strong>Hydrogen production by coal gasification in supercritical water with a novel fluidized
                            bed
                            gasifier</strong>”, 15<sup>th</sup> National Conference on Hydrogen Energy-7<sup>th</sup>
                            Hydrogen
                            Energy Seminar for the Chinese mainland, Hong Kong, Macao and Taiwan, Shanghai, China, November
                            2014
                        </li>
                        <li>
                            <strong><u>X.J. Guan</u></strong>, <strong>L.J. Guo*</strong>, “<strong>Fabrication of
                            TiO<sub>2</sub>/Ag<sub>3</sub>PO<sub>4</sub> composite for enhanced water oxidation</strong>”,
                            15<sup>th</sup> National Conference on Hydrogen Energy-7<sup>th</sup> Hydrogen Energy Seminar
                            for
                            the Chinese mainland, Hong Kong, Macao and Taiwan, Shanghai, China, November 2014
                        </li>
                        <li>
                            <strong><u>L.J. Ma</u></strong>, <strong>M.C. Liu</strong>, <strong>L.J. Guo</strong>, “<strong>Photocatalytic
                            hydrogen production over CdS: Effects of reaction atmosphere studied by in situ Raman
                            spectroscopy</strong>”, 15<sup>th</sup> National Conference on Hydrogen Energy-7<sup>th</sup>
                            Hydrogen Energy Seminar for the Chinese mainland, Hong Kong, Macao and Taiwan, Shanghai, China,
                            November 2014
                        </li>
                        <li>
                            <strong><u>J.B. Huang</u></strong>, <strong>L.J. Guo</strong>,
                            “<strong>BaZr<sub>0.1</sub>Ce<sub>0.7</sub>Y<sub>0.2</sub>O<sub>3-δ </sub>mixed with alkali
                            carbonates for low temperature SOFC applications: insight into stability</strong>”,
                            15<sup>th</sup>
                            National Conference on Hydrogen Energy-7<sup>th</sup> Hydrogen Energy Seminar for the Chinese
                            mainland, Hong Kong, Macao and Taiwan, Shanghai, China, November 2014
                        </li>
                        <li>
                            <strong><u>H. Jin</u></strong>, <strong>L.J. Guo</strong>, <strong>S.K. Liu</strong>, “<strong>Experimental
                            investigation on the key intermediates in the coal gasification process in supercritical
                            water</strong>”, 15<sup>th</sup> National Conference on Hydrogen Energy-7<sup>th</sup> Hydrogen
                            Energy Seminar for the Chinese mainland, Hong Kong, Macao and Taiwan, Shanghai, China, November
                            2014
                        </li>
                        <li>
                            <strong><u>G.Y. Chen</u></strong>, <strong>L.J. Guo</strong>, <strong>H.T. Liu</strong>,
                            “<strong>Effect
                            studied of Microporous layers on water management of the proton exchange membrane fuel using
                            current
                            distribution method cell</strong>”, 15<sup>th</sup> National Conference on Hydrogen
                            Energy-7<sup>th</sup> Hydrogen Energy Seminar for the Chinese mainland, Hong Kong, Macao and
                            Taiwan,
                            Shanghai, China, November 2014<br>
                        </li>
                        <li>
                            <strong><u>B. Wang</u></strong>, <strong>M.C. Liu</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>All Surface Active Sites</strong><strong>：The Role of the Cocatalyst</strong>&rdquo;,
                            15<sup>th</sup> National Conference on Hydrogen Energy-7<sup>th</sup> Hydrogen Energy Seminar
                            for
                            the Chinese mainland, Hong Kong, Macao and Taiwan, Shang Hai, China, November 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Dimensionality effects in oxide semiconductors</strong>&rdquo;, 2<sup>nd</sup>
                            International Conference of Young Researchers on Advanced Materials (IUMRS-ICYRAM), Symposium on
                            Energy Conversion-Photocatalysis, Fuel Cells &amp; Solar Cells, Hainan International Convention
                            &amp; Exhibition Center, Haikou, Hainan Province, China, October 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Interfacial Engineering for Efficient Solar Water Splitting</strong>&rdquo;,
                            226<sup>th</sup> Electrochemical
                            Society (ECS) Fall Meeting, Symposium on Solar Fuels, Photocatalysts &amp; Photoelectrochemical
                            Cells, Cancun, Mexico, October 2014
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong>Keynote</strong>)</span>,
                            &ldquo;<strong>Functionalized
                            modification to g-C<sub>3</sub>N<sub>4</sub> for efficient photocatalytic hydrogen generation:
                            Enhanced optical absorption and promoted charge separation</strong>&rdquo;, IUPAC
                            10<sup>th</sup>
                            International Conference on Novel Materials and their Synthesis, Zhengzhou, China, October 2014
                        </li>
                        <li>
                            <strong><u>D.M. Zhao</u></strong>,<strong> J. Chen</strong>,<strong> S.H. Shen</strong>,
                            <strong>L.J.
                                Guo</strong>, &ldquo;<strong>Enhanced Photocatalytic Activity for Hydrogen Evolution over
                            g-C<sub>3</sub>N<sub>4</sub> Modified by Ti Activated MCM-41 Mesoporous Silica</strong>&rdquo;,
                            1<sup>st </sup>International Symposium on Catalytic Science and Technology in Sustainable Energy
                            and
                            Environment (EECAT-2014), Tianjin, China, October 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span
                                class="invited">(<strong>Keynote lecture &amp; Session chair</strong>)</span>,
                            &ldquo;<strong>Interfacial
                            electronic structure &amp; confinement effects for low-cost solar water splitting</strong>&rdquo;,
                            SPIE Optics &amp; Photonics, Symposium on Solar Hydrogen &amp; Nanotechnology IX, San Diego, CA,
                            August 2014
                        </li>
                        <li>
                            <u><strong>J.Z. Su</strong></u> <span class="invited">(<strong>Invited</strong>)</span>,<strong>
                            Y.K. Wei</strong>, <strong>L.J. Guo</strong>, &ldquo;<strong>A novel Co-Pi capped pyramidal
                            BiVO<sub>4</sub> nanorod arrays with enhanced solar water oxidation</strong>&rdquo;, SPIE Optics
                            &amp; Photonics, Symposium on Solar Hydrogen &amp; Nanotechnology IX, San Diego, CA, August 2014
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>N-doped
                            ZnO nanorod arrays with gradient band structure for photoelectrochemical water
                            splitting</strong>&rdquo;,
                            SPIE Solar Energy + Technology conference 2014, San Diego, CA, August 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong
                                class="invited_cited_blue">Keynote</strong>)</span>, &ldquo;<strong>Oxide
                            Heteronanostructures
                            for Solar Water-Splitting</strong>&rdquo;, 248<sup>th</sup> American Chemical Society National
                            Meeting &amp; Exposition, 1<sup>st</sup> USA-China Symposium on Energy, San Francisco, CA,
                            August
                            2014
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Engineered
                            doping to metal oxide nanorod arrays for improved photoelectrochemical water splitting
                            activity</strong>&rdquo;, 248<sup>th</sup> American Chemical Society National Meeting &amp;
                            Exposition, San Francisco, CA, August 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres&nbsp;</strong><span
                                class="invited">(<strong>Keynote lecture &amp; Session chair</strong>)</span>,
                            &ldquo;<strong>Recent Advances in Quantum-confined all-Oxide Heteronanostructures for Solar
                            Water-Splitting</strong>&rdquo;, 6<sup>th</sup> International Symposium on Functional Materials,
                            Singapore, August 2014
                        </li>
                        <li>
                            <strong><u>Z.H. Zhou</u></strong>, <strong>S.H. Shen</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>Electronic structure of Ti and Sn doped hematite
                            (Fe<sub>2</sub>O<sub>3</sub>)</strong>&rdquo;, 14<sup>th</sup> Solar Energy Photochemistry and
                            Photocatalysis Conference, Haerbin, China, August 2014
                        </li>
                        <li>
                            Y. Lei, B.W. Zhang, <strong>B.F. Bai</strong>, T.S. Zhao, &ldquo;<strong>An 1-D Model for
                            Species
                            Crossover Through the Membrane in All-Vanadium Redox Flow Batteries</strong>&rdquo;, The
                            15<sup>th</sup> International Heat Transfer Conference, Kyoto, Japan, August 2014
                        </li>
                        <li>
                            B.W. Zhang, Y. Lei, <strong>B.F. Bai</strong>, T.S. Zhao, &ldquo;<strong>Numerical Investigation
                            of
                            Thermal Management for Kilowatt Vanadium Redox Flow Batteries</strong>&rdquo;, The
                            15<sup>th</sup>
                            International Heat Transfer Conference, Kyoto, Japan, August 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong
                                class="invited_cited_blue">Keynote</strong>)</span>, &ldquo;<strong>Low cost water
                            splitting oxide heteronanostructures</strong>&rdquo;, 22<sup>nd</sup> International Conference
                            on
                            Composites &amp; Nano Engineering, Malta, July 2014
                        </li>
                        <li>
                            <strong>L.J. Guo</strong> <span
                                class="invited">(<strong>Keynote lecture &amp; Session chair</strong>)</span>, “<strong>Solar
                            hydrogen: On material design and pilot-scale demonstration</strong>”, The 5<sup>th</sup>
                            Australia-China Conference on Science, Technology and Education and The 5<sup>th</sup>
                            Australia-China Symposium for Materials Science, Wollongong, Australia, July 2014
                        </li>
                        <li>
                            <strong><u>C. Zhang</u></strong>, C. Wang, S.J. Zhang, <strong>L.J. Guo</strong>, “<strong>The
                            effects of hydration activity of calcined dolomite on the silicothermic reduction
                            process</strong>”,
                            The Second Australia-China Joint Symposia on Minerals and Metallurgy, Sydney, Australia, July
                            2014
                        </li>
                        <li>
                            <strong>L.J. Guo</strong> <span class="invited">(<strong>Keynote</strong>)</span>, “<strong>The
                            progress in theoretical and experimental investigation of </strong>“<strong>boiling coal in
                            supercritical water to H<sub>2</sub> and Pure CO<sub>2</sub></strong>”<strong>
                            technology</strong>”,
                            2014 International Symposium on Frontiers of Technology for the Future: Low Carbon Energy and
                            Life
                            (FoTEL 2014), Hsinchu, Taiwan, June 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres&nbsp;</strong><span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>,
                            &ldquo;<strong>Interfacial chemistry and electronic structure of quantum-confined oxide
                            heteronanostructures for solar water splitting</strong>&rdquo;, 3<sup>rd</sup> International
                            Conference on New Advances in Materials Research for Solar Fuels Production, Montreal, Canada,&nbsp;June
                            2014
                        </li>
                        <li>
                            <strong>S.H. Shen</strong>, &ldquo;<strong>N ion implanted ZnO nanorod arrays: engineered band
                            structure for improved photoanodic performances</strong>”, International Conference on Clean
                            Energy
                            (ICCE2014), Istanbul, Turkey, June 2014
                        </li>
                        <li>
                            <strong><u>J.W. Shi</u></strong>, <strong>L.J. Guo</strong>, &ldquo;<strong>Novel
                            ABO<sub>3</sub>-based
                            photocatalysts for water splitting under visible-light irradiation</strong>”, International
                            Conference on Clean Energy (ICCE2014), Istanbul, Turkey, June 2014
                        </li>
                        <li>
                            <strong><u>J.Z. Su</u></strong>, <strong>C. Liu</strong>,<strong> L.J. Guo</strong>,
                            &ldquo;<strong>Different
                            metal element doped hematites and their electronic characterizations for solar water splitting
                            application</strong>&rdquo;, International Conference on Clean Energy (ICCE2014), Istanbul,
                            Turkey,
                            June 2014
                        </li>
                        <li>
                            <strong><u>G.Y. Chen</u></strong>, <strong>H.T. Liu</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>Effects of micro-porous layer under wide operating conditions in proton exchange
                            membrane fuel cell</strong>&rdquo;, International Conference on Clean Energy (ICCE2014),
                            Istanbul,
                            Turkey, June 2014
                        </li>
                        <li>
                            <strong><u>X.Q. Wang</u></strong>, <strong>H.H. Yang</strong>, <strong>Z. Yang</strong>,
                            <strong>L.J.
                                Guo*</strong>, &ldquo;<strong>Remarkable enhancement on hydrogen production performance of
                            Rhodobacter sphaeroides by disruption of spbA and hupSL genes</strong>&rdquo;, International
                            Conference on Clean Energy (ICCE2014), Istanbul, Turkey, June 2014
                        </li>
                        <li>
                            <strong><u>F. Jia</u></strong>, <strong>F.F. Liu</strong>,<strong> L.J.
                            Guo</strong>,<strong> </strong>H.T. Liu, &ldquo;<strong>Reverse current during start-up in PEM
                            fuel-cells</strong>&rdquo;,<strong> </strong>International Conference on Clean Energy
                            (ICCE2014),
                            Istanbul, Turkey, June 2014
                        </li>
                        <li>
                            <strong><u>Z.W. Ge</u></strong>,<strong> H. Jin</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>Hydrogen
                            production by catalytic gasification of coal in supercritical water with alkaline catalysts:
                            Explore
                            the way to complete gasification of coal</strong>&rdquo;, International Conference on Clean
                            Energy
                            (ICCE2014), Istanbul, Turkey, June 2014
                        </li>
                        <li>
                            <strong><u>B. Wang</u></strong>, <strong>S.H. Shen</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>Facile synthesis of high-indexed SrTiO<sub>3</sub> single-crystal photocatalysts
                            for
                            photocatalytic H<sub>2</sub> and O<sub>2</sub> evolution</strong>&rdquo;, International
                            Conference
                            on Clean Energy (ICCE2014), Istanbul, Turkey, June 2014
                        </li>
                        <li>
                            <strong><u>X.J. Guan</u></strong>, <strong>L.J. Guo</strong>, &ldquo;<strong>Synthesis and
                            characterization of SrTiO<sub>3</sub>/Ag<sub>3</sub>PO<sub>4</sub> composite for efficient
                            photocatalytic O<sub>2</sub> evolution under visible-light irradiation</strong>&rdquo;,
                            International Conference on Clean Energy (ICCE2014), Istanbul, Turkey, June 2014
                        </li>
                        <li>
                            <strong><u>X.X. Wang</u></strong>, <strong>J. Chen</strong>, <strong>X.J. Guan</strong>,
                            <strong>L.J.
                                Guo</strong>, &ldquo;<strong>Enhanced efficiency and stability for visible light driven
                            water
                            splitting hydrogen production over
                            Cd<sub>0.5</sub>Zn<sub>0.5</sub>S/g-C<sub>3</sub>N<sub>4</sub>
                            composite photocatalyst</strong>&rdquo;, International Conference on Clean Energy (ICCE2014),
                            Istanbul, Turkey, June 2014
                        </li>
                        <li>
                            <strong><u>J. Chen</u></strong>, <strong>Y.C. Du</strong>, <strong>S.H. Shen</strong>, <strong>L.J.
                            Guo</strong>, &ldquo;<strong>Distance modulated plasmonic enhancement in visible light
                            photocatalytic activity for hydrogen evolution over Ag@SiO<sub>2</sub> modified
                            g-C<sub>3</sub>N<sub>4</sub></strong>&rdquo;, International Conference on Clean Energy
                            (ICCE2014),
                            Istanbul, Turkey, June 2014
                        </li>
                        <li>
                            <strong><u>J. Wang</u></strong>, <strong>N. Zhang</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>Facile synthesis of highly monodisperse α-Fe<sub>2</sub>O<sub>3</sub> quantum
                            dots
                            for Water Oxidation</strong>&rdquo;, International Conference on Clean Energy (ICCE2014),
                            Istanbul,
                            Turkey, June 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres&nbsp;</strong><span class="invited">(<strong class="invited_cited_blue">Invited talk &amp; Session chair</strong>)</span>,
                            &ldquo;<strong>Confinement effects for efficient&nbsp;solar water splitting</strong>&rdquo;,
                            7<sup>th</sup>
                            International Conference on Energy Materials Nanotechnology, Beijing, China, May 2014
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Engineered
                            Impurity Distribution in ZnO Nanorod Arrays for Photoanodic Water Oxidation</strong>&rdquo;,
                            2014
                            EMN East Meeting, Beijing, China, May 2014
                        </li>
                        <li><strong>L. Vayssieres </strong><span class="invited">(<strong class="invited_cited_blue">Invited talk &amp; Session chair</strong>)</span>,
                            &ldquo;<strong>Quantum-confined oxide heteronanostructures by aqueous design</strong>&rdquo;,
                            2014
                            MRS Spring Meeting, Symposium RR: Solution Synthesis of Inorganic Functional Materials, San
                            Francisco, CA, USA, April 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>, &ldquo;<strong>Low-cost oxide
                            heteronanostructures for solar water splitting</strong>&rdquo;, UNESCO International Workshop on
                            Materials &amp; Technologies for Energy Conversion, Saving &amp; Storage, Montreal, Quebec,
                            Canada,
                            April 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong><span class="invited">&nbsp;(<strong class="invited_cited_blue">Invited talk &amp; Session chair</strong>)</span>,
                            &ldquo;<strong>Low cost quantum-confined oxide heteronanostructures</strong>&rdquo;, Nano &amp;
                            Giga
                            Challenges in Electronics, Photonics and Renewable Energy: From Materials to Devices to System
                            Architecture, Phoenix, AZ, March 2014
                        </li>
                        <li>
                            <strong><u>S.H. Shen</u></strong><span class="invited"> (<strong
                                class="invited_cited_blue">Invited</strong>)</span>, <strong>M. Wang</strong>,
                            &ldquo;<strong>Doping
                            to metal oxide nanorod arrays: Engineered electronic property and band structure for improved
                            photoanodic performances</strong>&rdquo;, 247<sup>th</sup> ACS National Meeting &amp;
                            Exposition,
                            Symposium on Nanostructured Materials for Solar Energy Conversion and Storage, Dallas, USA,
                            March
                            2014
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            &ldquo;<strong>Doping
                            to ZnO nanorod arrays by ion implantation method: Engineered band structure and visible light
                            photoelectrochemical water splitting</strong>&rdquo;, 2014 EMN Spring Meeting, Las Vegas, NV,
                            February-March 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres&nbsp;</strong><span class="invited">(<strong class="invited_cited_blue">Invited talk &amp; Session chair</strong>)</span>,
                            &ldquo;<strong>Advances in quantum confinement effects and interfacial electronic structure for
                            solar water splitting</strong>&rdquo;, American Ceramic Society Materials Challenges in
                            Alternative
                            &amp; Renewable Energy 2014 Conference, Clearwater, FL, February 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres&nbsp;</strong><span
                                class="invited">(<strong>Plenary Lecture &amp; Session chair</strong>)</span>,
                            &ldquo;<strong>All-Oxide Heteronanostructures For Solar Hydrogen Generation</strong>&rdquo;,
                            Molecules and Materials for Artificial Photosynthesis Fusion Conference, Cancun, Mexico,
                            February
                            2014
                        </li>
                        <li>
                            <strong>L.J. Guo</strong> <span class="invited">(<strong>Invited</strong>)</span>, “<strong>The
                            progress in theoretical and experimental investigation of ‘boiling coal in supercritical water
                            to
                            H<sub>2</sub> and Pure CO<sub>2</sub>’ technology</strong>”, Asian Pacific Conference on Energy
                            and
                            Environmental Materials (APCEEM), Gold Coast, Queensland, Australia, February 2014
                        </li>
                        <li>
                            <strong><u>M.C. Liu</u> </strong><span class="invited">(<strong>Invited</strong>)</span>,
                            <strong>L.J.
                                Guo</strong>, “<strong>Solar hydrogen: harvesting light and heat from sun</strong>”, 6<sup>th</sup>
                            Sino-Thai Workshop on Renewable Energy, Guangzhou, China, January 27-30, 2014
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>, &ldquo;<strong>Doped and Core/shell
                            Structured Hematite Nanorods for Efficient Solar Water Splitting</strong>&rdquo;,
                            38<sup>th</sup>&nbsp;International
                            Conference and Exposition on Advanced Ceramics and Composites, Symposium 7: 8<sup>th</sup>&nbsp;International
                            Symposium on Nanostructured Materials and Nanocomposites, Daytona Beach, FL, USA, January 2014
                        </li>
                    </ol>
                    <h5 align="center" class="h5" style="margin-top:15px; margin-bottom:0px;">2013 (46)</h5>
                    <ol style="list-style-type:decimal; margin: 30px; padding:30px 10px;" reversed start="96">
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong class="blue_color">Invited
                            talk &amp; Session chair</strong>)</span>, &ldquo;<strong>Aqueous chemical growth of advanced
                            heteronanostructures</strong>&rdquo;, 12<sup>th</sup> International Conference
                            on Frontiers of Polymers &amp; Advanced Materials, Auckland, New Zealand, December
                            2013
                        </li>
                        <li>
                            <strong><u>S.H. Shen</u></strong> <span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>, <strong>L.J. Guo</strong>, S. S. Mao,
                            &ldquo;<strong>Solution-based hematite nanorods with ultrathin overlayer for efficient
                            photoelectrochemical water splitting</strong>&rdquo;, 2013 MRS Fall Meeting &amp; Exhibit,
                            Symposium
                            Z: Sustainable Solar-Energy Conversion Using Earth-Abundant Materials, Boston, USA, December
                            2013
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>,
                            &ldquo;<strong>Advanced Low cost Heteronanostructures for Solar Water Splitting</strong>&rdquo;,
                            Swedish-Chinese Workshop on Renewable Energy: From Fundamentals to Applications,
                            Uppsala University, Uppsala, Sweden, November 2013
                        </li>
                        <li>
                            <strong>L. Vayssieres&nbsp;</strong><span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>,&nbsp;&ldquo;<strong>All-oxide
                            quantum-confined heteronanostructures</strong>&rdquo;, 2<sup>nd</sup> General Meeting
                            of the European Cooperation in Science &amp; Technology, Chemistry and Molecular
                            Sciences and Technologies on&nbsp;Reducible Oxide Chemistry, Structure&nbsp;&amp;
                            Functions, Uppsala University, Angstrom Laboratory, Siegbahn Hall, Uppsala, Sweden,
                            November 2013
                        </li>
                        <li>
                            <strong><u>J.N. Chen</u></strong>,<strong> M. Wang</strong>,<strong> S.H. Shen</strong>,<strong>
                            L.J
                            Guo</strong>, &ldquo;<strong>Au@SiO<sub>2</sub> core/shell nanoparticles decorated
                            TiO<sub>2</sub>
                            nanorod arrays for enhanced photoelectrochemical water splitting</strong>&rdquo;, The
                            18<sup>th</sup> International Conference on Semiconductor Photocatalysis and Solar Energy
                            Conversion
                            (SPASEC-18), San Diego, California, USA , November 2013
                        </li>
                        <li>
                            <strong><u>S.H. Shen</u></strong>, <strong>J. Chen</strong>,<strong> X.X. Wang</strong>,<strong>
                            L.J. Guo</strong>, &ldquo;<strong>Visible Light Activation of MCM-41 Mesoporous Silica by
                            Transition-Metal Incorporation for Photocatalytic Hydrogen Production</strong>&rdquo;, The
                            18<sup>th</sup> International Conference on Semiconductor Photocatalysis and Solar Energy
                            Conversion
                            (SPASEC-18), San Diego, California, USA, November 2013
                        </li>
                        <li>
                            <strong><u>J.Z. Su</u></strong>, <strong>L. Wang</strong>,<strong> L.J. Guo</strong>,
                            &ldquo;<strong>Enhanced Photoelectrochemical Water Splitting Using
                            BiVO<sub>4</sub>/CeO<sub>2</sub>
                            Nanostructural Heterojunction</strong>&rdquo;, The 18<sup>th</sup> International Conference on
                            Semiconductor Photocatalysis And Solar Energy Conversion (SPASEC-18), San Diego, California,
                            USA,
                            November 2013
                        </li>
                        <li>
                            <strong><u>R. Xie</u></strong>, <strong>J.Z. Su</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>Optical,
                            Structural and Photoelectrochemical Properties of Ag<sub>2</sub>S Modified CdS Nanorods
                            Arrays</strong>&rdquo;, The 18<sup>th</sup> International Conference on Semiconductor
                            Photocatalysis
                            And Solar Energy Conversion (SPASEC-18), San Diego, California, USA, November 2013<br>
                        </li>
                        <li>
                            <strong><u>Y.M. Fu</u></strong>, <strong>S.H. Shen</strong>,<strong> L.J. Guo</strong>,
                            &ldquo;<strong>Enhanced Photoelectrochemical Performance of Nb-doped Hematite
                            (α-Fe<sub>2</sub>O<sub>3</sub>) Nanorods Photoanodes for Water Splitting</strong>&rdquo;, The
                            18<sup>th</sup> International Conference on Semiconductor Photocatalysis and Solar Energy
                            Conversion
                            (SPASEC-18), San Diego, California, USA, November 2013
                        </li>
                        <li>
                            <strong><u>Y. Liu</u></strong>, <strong>M. Wang</strong>, <strong>L.J. Guo</strong>, <strong>M.T.
                            Li</strong>, &ldquo;<strong>Preparation of CdSe/TiO<sub>2</sub> Nanfibers Films and Their
                            Photo-electrochemical Properties for Water Splitting Applicatio</strong>&rdquo;, The
                            18<sup>th</sup>
                            International Conference on Semiconductor Photocatalysis and Solar Energy Conversion
                            (SPASEC-18),
                            San Diego, California, USA, November 2013<br>
                        </li>
                        <li>
                            <u><strong>H. Liu</strong></u>,<strong> L.J. Guo</strong>, &ldquo;<strong>Novel Quantum Yield
                            Measurement System for Photocatalytic Reaction</strong>&rdquo;, The 18<sup>th</sup>
                            International
                            Conference on Semiconductor Photocatalysis and Solar Energy Conversion (SPASEC-18), San Diego,
                            California, USA, November 2013
                        </li>
                        <li>
                            <strong><u>L. Cai</u></strong>, <strong>S.H. Shen</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>Synthesis and Photoelectrochemical Properties of Ag@SiO<sub>2</sub>-ZnO Nanowire
                            Array Film</strong>&rdquo;, The 18<sup>th</sup> International Conference on Semiconductor
                            Photocatalysis and Solar Energy Conversion (SPASEC-18), San Diego, California, USA, November
                            2013
                        </li>
                        <li>
                            <strong><u>P.H. Guo</u></strong>, <strong>S.H. Shen</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>Doped ZnO Homojunction for Promoted Photoelectrochemical Water Splitting under
                            Visible Light</strong>&rdquo;, The 18<sup>th</sup> International Conference on Semiconductor
                            Photocatalysis and Solar Energy Conversion (SPASEC-18), San Diego, California, USA, November
                            2013
                        </li>
                        <li>
                            <strong><u>X.K. Wan</u></strong>, <strong>M. Wang</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>Heterojunction CdSe/BiVO<sub>4</sub> Films for Photoelectrochemical Water
                            Splitting</strong>&rdquo;, The 18<sup>th</sup> International Conference on Semiconductor
                            Photocatalysis and Solar Energy Conversion (SPASEC-18), San Diego, California, USA, November
                            2013
                        </li>
                        <li>
                            <strong><u>D.W. Jing</u></strong>, <strong>L.Z. Zhang</strong>, X.D Yao, <strong>L.J.
                            Guo</strong>,
                            &ldquo;<strong>In-Situ Photochemical Synthesis of Zn Doped Cu<sub>2</sub>O Hollow Nanocubes for
                            High
                            Efficient H<sub>2</sub> Production by Photocatalytic Reforming of Glucose under Visible
                            Light</strong>&rdquo;, The 18<sup>th</sup> International Conference on Semiconductor
                            Photocatalysis
                            and Solar Energy Conversion (SPASEC-18), San Diego, California, USA, November 2013
                        </li>
                        <li>
                            <strong><u>M.T. Li</u></strong>,<strong> L.J. Guo</strong>, &ldquo;<strong>A First Principles
                            Study
                            on Bi<sub>2</sub>Mo<sub>1-x</sub>W<sub>x</sub>O<sub>6</sub> for Photocatalytic Water Splitting
                            Application</strong>&rdquo;, The 18<sup>th</sup> International Conference on Semiconductor
                            Photocatalysis and Solar Energy Conversion (SPASEC-18), San Diego, California, USA, November
                            2013
                        </li>
                        <li>
                            <strong>L. Vayssieres<span class="invited">&nbsp;</span></strong><span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>,&ldquo;<strong>Visible light-active
                            quantum-confined
                            all-oxide heteronanostructures</strong>&rdquo;,2013 Materials Science &amp; Technology
                            Conference
                            (MS&amp;T), Symposium on Optical Nanomaterials for Photonics/Biophotonics, Montreal, Quebec,
                            Canada,
                            October 2013
                        </li>
                        <li>
                            <u><strong>J.W. Shi</strong></u>, <strong>L.J. Guo</strong>, &ldquo;<strong>Design and
                            structure-activity relationships of novel ABO<sub>3</sub> structure-based visible-light-driven
                            photocatalysts</strong>&rdquo;, Materials Science &amp; Technology 2013 Conference &amp;
                            Exhibition,
                            Montreal, Quebec, Canada, October 2013
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>, &ldquo;<strong>Metal Oxide or Metal
                            Nanodots Decorated g-C<sub>3</sub>N<sub>4</sub> for Efficient Photocatalytic Hydrogen
                            Production</strong>&rdquo;, Materials Science &amp; Technology 2013 Conference &amp; Exhibition,
                            Montreal, Quebec, Canada, October 2013
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong
                                class="invited_cited_blue">Keynote</strong>)</span>, &ldquo;<strong>Core/Shell Structured
                            Hematite Nanorod Arrays as Photoanodes for Efficient Solar Water Oxidation</strong>&rdquo;,
                            IUPAC
                            9th International Conference on Novel Materials and their Synthesis (NMS-IX) &amp; 23rd
                            International Symposium on Fine Chemistry and Functional Polymers (FCFP-XXIII), Shanghai, China,
                            October 2013
                        </li>
                        <li>
                            <strong>J.Z. Su </strong><span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>,
                            &ldquo;<strong>WO<sub>3</sub>-based nano-wire arrays  heterojunction and their
                            photoelectrochemical
                            hydrogen production performance</strong>&rdquo;, 14<sup>th</sup> National Youth Science and
                            Technology Materials Seminar, Shenyang, China, October 2013
                        </li>
                        <li>
                            <strong><u>M.C. Liu</u></strong> <span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>, <strong>D.W. Jing</strong>, <strong>Z.H.
                            Zhou</strong>, <strong>L.J. Guo</strong>, “<strong>Twin-induced homojunctions for efficient
                            solar
                            hydrogen generation</strong>”, 4<sup>th</sup> China-Australia Symposium for Materials Science,
                            Zhuhai, China, October 20-24, 2013
                        </li>
                        <li>
                            <strong>I. Zegkinoglou</strong>, &ldquo;<strong>New Materials for Solar Energy Conversion:
                            Interface
                            Studies with Soft X-Ray Spectroscopy</strong>&rdquo;, 2013 Advanced Light Source User Meeting,
                            Workshop on Soft X-Ray Spectroscopy of Heterogeneous Interface, Lawrence Berkeley National
                            Laboratory, Berkeley, CA, October 2013
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>,&ldquo;<strong>All-oxide Quantum-confined
                            Hetero-Nanostructures for Solar Hydrogen Generation by Water Splitting</strong>&rdquo;,
                            3<sup>rd </sup>Annual World Congress of Nano Science &amp; Technology, Symposium on
                            Nanotechnology
                            in Energy &amp; Environment, Qujiang International Conference Center, Xi'an, China, September
                            2013&nbsp;
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong class="blue_color">Keynote lecture &amp; Session chair</strong>)</span>,
                            &ldquo;<strong>Quantum-confined oxide heteronanostructures for solar hydrogen
                            generation</strong>&rdquo;,
                            1<sup>st</sup> International Workshop on Nanotechnology, Renewable Energy &amp; Sustainability
                            (NRES), Xi&rsquo;an, China, September 2013
                        </li>
                        <li>
                            <strong>Q.Y. Chen</strong>, &ldquo;<strong>Electricity and Hydrogen Co-production from A
                            Bio-Electrochemical Cell with Acetate Substrate</strong>&rdquo;, 3<sup>rd</sup> New Energy
                            Forum-2013 with the theme of &ldquo;From Green Dream to Reality&rdquo;, Xian, China, September
                            2013
                        </li>
                        <li>
                            <strong>D.W. Jing </strong><span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>, &ldquo;<strong>Experimental and
                            numerical
                            study on the solar photocatalytic hydrogen production reactor</strong>&rdquo;, 3<sup>rd</sup>
                            New
                            Energy Forum-2013, Xi&rsquo;an, China, September 2013
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>, &ldquo;<strong>Doped Hematite
                            Nanostructures for Solar Water Oxidation</strong>&rdquo;, Workshop on &ldquo;Alternative Energy
                            Solutions and Sustainable Growth&rdquo;, New Delhi, India, September 2013
                        </li>
                        <li>
                            <u><strong>Y.M. Fu</strong></u>,<strong> L. Zhao</strong>, <strong>S.H. Shen</strong>,
                            &ldquo;<strong>Enhancement of Photoelectrochemical Performance by Doping Tantalum Ions in
                            Hematite
                            (α-Fe<sub>2</sub>O<sub>3</sub>) Nanorod Photoanodes</strong>&rdquo;, International Conference on
                            Nanoscience &amp; Technology, Beijing, China, September 2013
                        </li>
                        <li>
                            <strong>L. Vayssieres&nbsp;</strong><span class="invited">(<strong class="blue_color">Keynote
                            lecture &amp; Session chair</strong>)</span>, &ldquo;<strong>Quantum-confined oxide
                            heteronanostructures
                            for solar hydrogen generation</strong>&rdquo;, 8<sup>th</sup> International
                            Conference on High Temperature Ceramic Matrix, Symposium S3 on Nanocomposite Materials
                            &amp; Systems, Xi'an, China, September 2013
                        </li>
                        <li>
                            <strong><u>J.W. Shi</u></strong>, <strong>L.J. Guo</strong>, &ldquo;<strong>Novel
                            ABO<sub>3</sub>-based
                            photocatalysts for visible-light-driven water splitting</strong>&rdquo;, 8<sup>th</sup>
                            International Conference on High Temperature Ceramic Matric Composites (HTCMC-8), Xi'an, China,
                            September 2013
                        </li>
                        <li>
                            <strong><u>J.Z. Su</u></strong>, <strong>L.J. Guo</strong>, &ldquo;<strong>Different Metal
                            Element
                            Doped Hematites and Their Electronic Characterizations for Solar Water Splitting
                            Application</strong>&rdquo;, 8<sup>th</sup> International Conference on High Temperature Ceramic
                            Matrix Composites (HTCMC-8), Xi'an, China, September 2013
                        </li>
                        <li>
                            <strong>S.H. Shen</strong>, &ldquo;<strong>Metal oxide QDs enabled efficient photocatalytic
                            hydrogen
                            generation over g-C<sub>3</sub>N<sub>4</sub> under visible light</strong>&rdquo;, 8<sup>th</sup>
                            International Conference on High Temperature Ceramic Matrix Composites (HTCMC-8), Xi'an, China,
                            September 2013
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong class="blue_color">Invited talk &amp; Session chair</strong>)</span>,
                            “<strong>On quantum confinement effects in large bandgap semiconductors</strong>”, SPIE Optics
                            &amp;
                            Photonics, Symposium on Solar Hydrogen &amp; Nanotechnology VIII, San Diego, CA, August 2013
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>, “<strong>Quantum-confined oxide
                            heteronanostructures for solar hydrogen generation</strong>”, 2013 CMOS Emerging Technologies
                            Research Symposium, Whistler, BC, Canada, July 2013
                        </li>
                        <li>
                            <strong>Q.Y. Chen</strong>, &ldquo;<strong>TiO<sub>2</sub> photocathode coupling with bio-anode
                            for
                            electricity and hydrogen co-production</strong>&rdquo;, 5<sup>th</sup> International Conference
                            on
                            Applied Energy, Pretoria, South Africa, July 2013
                        </li>
                        <li>
                            <strong>S.H. Shen</strong>, &ldquo;<strong>Zr-doped α-Fe<sub>2</sub>O<sub>3</sub> photoanodes
                            for
                            efficient solar water splitting</strong>&rdquo;, 11<sup>th</sup> International Conference on
                            Materials Chemistry (MC11), University of Warwick, UK, July 2013
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong> <span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>, “<strong>Quantum confinement and interfacial
                            electronic structure effects for efficient solar hydrogen generation</strong>”, 7<sup>th </sup>International
                            Conference on Materials for Advanced Technology (ICMAT), Symposium D on Nanostructure Materials
                            for
                            Solar Energy Conversion, Suntec, Singapore, June-July 2013
                        </li>
                        <li>
                            <strong>L. Vayssieres&nbsp;</strong><span class="invited">(<strong class="blue_color">Invited talk &amp; Session chair</strong>)</span>,
                            &ldquo;<strong>On quantum confinement effects and interfacial electronic structure engineering
                            for
                            efficient solar hydrogen generation</strong>&rdquo;,10<sup>th</sup>&nbsp;PACRIM conference on
                            Ceramic &amp; Glass Technology,<br>Symposium 7 on Multifunctional Metal Oxide Nanostructures and
                            Heteroarchitectures for Energy and Device Applications,&nbsp;San Diego, CA, USA, June 2013
                        </li>
                        <li>
                            <strong> <u>S.H. Shen</u></strong>, <strong>J. Chen</strong>, <strong>Z. Liu</strong>, <strong>L.J.
                            Guo</strong>, &ldquo;<strong>Creating active sites in mesostructure of MCM-41 for efficient
                            photocatalytic hydrogen generation under visible light</strong>&rdquo;, The 10<sup>th</sup>
                            Pacific
                            Rim Conference on Ceramic and Glass Technology including GOMD 2013 - Glass &amp; Optical
                            Materials
                            Division Annual Meeting, San Diego, CA, USA, June 2013
                        </li>
                        <li>
                            <strong>J.J. Wei</strong>, &ldquo;<strong>Selection of surface reflectivity for a solar cavity
                            receiver</strong>&rdquo;, The Asian Symposium on Computational Heat Transfer and Fluid
                            Flow-2013,
                            Hong Kong, June 2013
                        </li>
                        <li>
                            <u><strong>I. Zegkinoglou</strong></u>&nbsp;<span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>,
                            C. X. Kronawitter, X. Feng, J.H Guo, D. Wang, S. S. Mao, F. J.
                            Himpsel,&nbsp;<strong>L.Vayssieres</strong>, &ldquo;<strong>Electronic Structure of Hematite
                            Photoanodes for Efficient Solar Water Splitting: A Soft X-Ray Spectroscopy Study</strong>&rdquo;,
                            2013 Spring Meeting of the Materials Research Society (MRS), Symposium Z on Nanotechnology &amp;
                            Sustainability, San Francisco, CA, USA, April 2013
                        </li>
                        <li>
                            <strong><u>S.H. Shen</u></strong> <span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>, <strong>J.G. Jiang</strong>, Coleman X.
                            Kronawitter,<strong> P.H. Guo</strong>, <strong>L.J. Guo</strong>, S. S. Mao,
                            &ldquo;<strong>TiO<sub>2</sub><sub> </sub>Modified α-Fe<sub>2</sub>O<sub>3</sub> Nanorod Arrays
                            for
                            Efficient Solar Water Splitting</strong>&rdquo;, 2013 MRS Spring Meeting &amp; Exhibit, YY:
                            Titanium
                            Dioxide-Fundamentals and Applications Symposium, San Francisco, CA, USA, April 2013
                        </li>
                        <li>
                            <strong><u>S.H. Shen</u></strong>, <strong>J.G Jiang</strong>, <strong>P.H. Guo</strong>,
                            Coleman X.
                            Kronawitter, <strong>L.J. Guo</strong>, S. S. Mao, &ldquo;<strong>Aqueous solution growth of
                            Pt-doped hematite photoanodes for efficient water splitting</strong>&rdquo;, Colloids &amp;
                            Energy
                            Conference 2013, Xiamen, China, April 2013
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>, &ldquo;<strong>Doped Hematite Nanorod
                            Arrays for Enhanced Solar Water Splitting</strong>&rdquo;, NANOSMAT-Asia, Wuhan, China, March
                            2013
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong>Plenary</strong>)</span>,
                            “<strong>Quantum-confined
                            oxide heteronanostructures for solar hydrogen generation</strong>”, 6<sup>th </sup>International
                            Conference on Advanced Materials &amp; Nanotechnology, Auckland, New Zealand, February 2013
                        </li>
                    </ol>
                    <h5 align="center" class="h5" style="margin-top:15px; margin-bottom:0px;">2012 (43)</h5>
                    <ol style="list-style-type:decimal; margin: 30px; padding:30px 10px;" reversed start="50">
                        <li>
                            <strong>E. Traversa </strong><span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>, “<strong>Towards the Next Generation of Solid
                            Oxide
                            Fuel Cells Operating at 600°C with Chemically Stable Proton Conducting Electrolytes</strong>”,
                            Symposium on Advanced Materials for Applications in Energy, Health, Electronics and Photonics,
                            Varennes, Quebec, Canada, November 30, 2012
                        </li>
                        <li>
                            <strong>E. Traversa</strong> <span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>, “<strong>Ionic Conductivity of Oxide Thin Films
                            and
                            Superlattices</strong>&rdquo;, Materials Research Society Fall 2012 Meeting, Symposium F: Oxide
                            Thin
                            Films for Renewable Energy Applications/Symposium I: Functional Materials for Solid Oxide Fuel
                            Cells, Boston, MA, USA, November 25-30, 2012
                        </li>
                        <li>
                            <strong>B. Chen</strong> <span class="invited">(<strong
                                class="invited_cited_blue">Keynote</strong>)</span>,
                            &ldquo;<strong>Doped Particle Semi-implicit Method Based on Large Eddy Simulation</strong>&rdquo;,
                            The 4<sup>th</sup> International Conference on Computational Methods, Gold Coast, QLD,
                            Australia,
                            November 2012
                        </li>
                        <li>
                            <u>F. J. Himpsel</u>&nbsp;<span class="invited">(<strong>Invited</strong>)</span>, J. Guo, W.
                            Yang,
                            Z. Hussain,&nbsp;<strong>L. Vayssieres</strong>, &ldquo;<strong>Using Spectroscopy for Designing
                            New
                            Types of Solar Cells</strong>&rdquo;, 2012 X-ray Scattering Principal Investigators' Meeting,
                            Division of Materials Sciences &amp; Engineering, Office of Basic Energy Sciences, U.S.
                            Department
                            of Energy, Washingtonian Marriott, Gaithersburg, MD, November 2012
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong class="blue_color">Keynote lecture &amp; Session chair</strong>)</span>,
                            &ldquo;<strong>All-oxide heteronanostructures for solar hydrogen generation</strong>&rdquo;,
                            6<sup>th </sup>International
                            Workshop on Advanced Materials Science &amp; Nanotechnology, Halong Bay, Vietnam,
                            October-November
                            2012
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong
                                class="blue_color">Plenary</strong>)</span>,&ldquo;<strong>Low cost metal oxide
                            heteronanostructures for renewable energy</strong>&rdquo;, The 12<sup>th </sup>International
                            Conference on Clean Energy (ICCE-2012), Xi&rsquo;an, China, October 26-30, 2012
                        </li>
                        <li>
                            <strong> E. Traversa</strong> <span class="invited">(<strong
                                class="blue_color">Plenary</strong>)</span>,&ldquo;<strong>Towards the Next Generation of
                            Solid
                            Oxide Fuel Cells Operating at 600°C with Chemically Stable Proton Conducting
                            Electrolytes</strong>&rdquo;,
                            The 12<sup>th</sup>International Conference on Clean Energy (ICCE-2012), Xi&rsquo;an, China,
                            October
                            26-30, 2012
                        </li>
                        <li>
                            <strong>L.J. Guo </strong><span class="invited">(<strong
                                class="blue_color">Plenary</strong>)</span>,&ldquo;<strong>Boiling
                            Coal in Water</strong><strong>— H<sub>2</sub> production and power generation system with near
                            zero
                            CO<sub>2</sub> emission based coal and supercritical water gasification</strong>&rdquo;, The
                            12<sup>th</sup>
                            International Conference on Clean Energy (ICCE-2012), Xi&rsquo;an, China, October 26-30, 2012
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong
                                class="invited_cited_blue">Plenary</strong>)</span>, &ldquo;<strong>Facile Aqueous Growth of
                            Hematite Photoanodes for Solar Water Splitting</strong>&rdquo;, The 12<sup>th</sup>
                            International
                            Conference on Clean Energy (ICCE-2012), Xi&rsquo;an, China, October 26-30, 2012
                        </li>
                        <li>
                            <strong>Q.Y. Chen</strong>, &ldquo;<strong>Co-production of electricity and hydrogen from
                            microbial
                            fuel cell</strong>&rdquo;, The 12<sup>th</sup> International Conference on Clean Energy
                            (ICCE-2012),
                            Xi'an, China, October 26-30, 2012
                        </li>
                        <li>
                            <strong><u>J. Chen</u></strong>, <strong>S.H. Shen</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>Enhanced photocatalytic hydrogen evolution over Cu-doped
                            g-C<sub>3</sub>N<sub>4</sub>
                            under visible light irradiation [C]</strong>&rdquo;, The 12<sup>th</sup> International
                            Conference on
                            Clean Energy (ICCE-2012), Xi&rsquo;an, China, October 26-30, 2012
                        </li>
                        <li>
                            <strong><u>P. Wu</u></strong>, <strong>J. Chen</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>Effect
                            of Silicon on Graphitic Carbon Nitride for Visible-light-Driven Photocatalytic Hydrogen
                            Evolution</strong>&rdquo;, The 12<sup>th</sup> International Conference on Clean Energy
                            (ICCE-2012),
                            Xi&rsquo;an, China, October 26-30, 2012
                        </li>
                        <li>
                            <strong> L. Vayssieres </strong><span class="invited">(<strong
                                class="blue_color">Keynote</strong>)</span>,&ldquo;<strong>Aqueous
                            design of quantum-confined oxide heteronanostructures</strong>&rdquo;, 8<sup>th</sup> IUPAC
                            International Conference on New Materials &amp; their Synthesis, Xi&rsquo;an, China, October
                            14-19,
                            2012
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>,&ldquo;<strong>All-oxide quantum-confined hetero
                            nanostructures for solar hydrogen generation</strong>&rdquo;, 222<sup>nd</sup> ECS Fall Meeting,
                            Symposium B10: Renewable Fuels from Sunlight&amp; Electricity, Honolulu, October 2012
                        </li>
                        <li>
                            <strong>E. Traversa</strong> <span class="invited">(<strong
                                class="blue_color">Plenary</strong>)</span>,&ldquo;<strong>Towards the Next Generation of
                            Solid
                            Oxide Fuel Cells Operating at 600°C with Chemically Stable Proton Conducting
                            Electrolytes</strong>&rdquo;,
                            Euro-mediterranean Hydrogen Technologies Conference-EmHyTeC 2012, Hammamet, Tunisia, September
                            11-14, 2012
                        </li>
                        <li>
                            <strong>J.Z. Su</strong> <span class="invited">(<strong>Invited</strong>)</span>,&ldquo;<strong>Hydrogen
                            Production by Photocatalytic and Photoeletrochemical Methods</strong>&rdquo;, Sino-German
                            Workshop
                            on Energy Research, Xi'an China, September 2012
                        </li>
                        <li>
                            <strong>H. Jin </strong><span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>,
                            &ldquo;<strong>Hydrogen production by supercritical water gasification driven by concentrated
                            solar
                            energy</strong>&rdquo;, Sino-German Workshop on Energy Research, Xi'an, China, September 2012
                        </li>
                        <li>
                            <strong>X.W. Hu </strong><span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>,
                            &ldquo;<strong>Hydrogen Bubble during Photocatalysis</strong>&rdquo;, Sino-German Workshop on
                            Energy
                            Research, Xi'an, China, September 2012
                        </li>
                        <li>
                            <strong>H. Jin </strong><span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>,
                            &ldquo;<strong>Hydrogen production by supercritical water gasification</strong>&rdquo;,
                            Sino-German
                            Workshop on Energy Research, Xi'an, China, September 2012
                        </li>
                        <li>
                            <strong>E. Traversa </strong><span
                                class="invited">(<strong>Invited</strong>)</span>,&ldquo;<strong>Ionic
                            Conductivity of Oxide Thin Films and Superlattices</strong>&rdquo;, XI International Conference
                            on
                            Nanostructured Materials NANO 2012, Rhodes, Greece, August 26-31, 2012
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong class="blue_color">Invited talk &amp; Session chairs</strong>)</span>,
                            &ldquo;<strong>All-oxide hetero nanostructures for direct solar water splitting</strong>&rdquo;,
                            SPIE Optics &amp; Photonics, Symposium on Solar Hydrogen &amp; Nanotechnology VII, San Diego,
                            CA,
                            USA, August 11-16, 2012
                        </li>
                        <li>
                            <strong><u>J.Z. Su</u></strong>, <strong>L.J. Guo</strong>, &ldquo;<strong>1D metal oxide
                            nanowire
                            array synthesis and photoelectrochemical application</strong>&rdquo;, SPIE Optics &amp;
                            Photonics,
                            Symposium on Solar Hydrogen &amp; Nanotechnology VII, San Diego, CA, USA, August 11-16, 2012
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong
                                class="blue_color">Keynote</strong>)</span>,&ldquo;<strong>All-oxide hetero nanostructures
                            for
                            solar water splitting</strong>&rdquo;,244<sup>th</sup> American Chemical Society National
                            Meeting
                            &amp; Exposition, 4<sup>th</sup>International Symposium on Hydrogen from Renewable Sources and
                            Refinery Applications, Philadelphia, PA, USA, August 2012
                        </li>
                        <li>
                            <strong>D.W. Jing </strong><span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>,&ldquo;<strong>Photocatalytic Hydrogen
                            Production
                            under visible light over TiO<sub>2</sub> calcined in different Gas Atmospheres</strong>&rdquo;,
                            XXI
                            International Materials Research Congress, Cancun, Mexico, August 2012
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>,&ldquo;<strong>Enhanced Performance for Water
                            Splitting over Ti-doped Hematite Photoanodes</strong>&rdquo;, XXI International Materials
                            Research
                            Congress, Cancun, Mexico, August 2012
                        </li>
                        <li>
                            <strong><u>J.W. Shi</u></strong>, <strong>L.J. Guo</strong>, &ldquo;<strong>Tin(II) antimonates
                            with
                            adjustable compositions: Bandgap and nanostructure control for visible-light-driven
                            photocatalytic
                            H<sub>2</sub>
                            evolution</strong>&rdquo;, XXI International Materials Research Congress, Cancun, Mexico, August
                            2012
                        </li>
                        <li>
                            <strong><u>Y. Liu</u></strong>, <strong>J.G. Jiang</strong>, <strong>M.T. Li</strong>, <strong>L.J.
                            Guo</strong>, &ldquo;<strong>Photoelectrochemical performance of cds nanorods grafted on
                            vertically
                            aligned Tio<sub>2</sub> nanorods</strong>&rdquo;, XXI International Materials Research Congress,
                            Cancun, Mexico, August 2012
                        </li>
                        <li>
                            <strong>L.Vayssieres </strong><span class="invited">(<strong
                                class="blue_color">Keynote</strong>)</span>,&ldquo;<strong>Quantum-confined metal oxide
                            hetero-nanostructures for clean energy</strong>&rdquo;, 20<sup>th</sup> International Conference
                            on
                            Composites/Nano Engineering, Beijing, China, July 2012
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong
                                class="blue_color">Keynote</strong>)</span>,&ldquo;<strong>All oxide hetero-nanostructures
                            for
                            clean energy</strong>&rdquo;, 2<sup>nd</sup> International Defense Nanotechnology Application
                            Center
                            Symposium on Nanotechnology, Yonsei University, Seoul, Korea, July 2012
                        </li>
                        <li>
                            <strong> L. Vayssieres </strong><span class="invited">(<strong class="blue_color">Invited talk &amp; Session chair</strong>)</span>,
                            &ldquo;<strong>Aqueous design of quantum-confined metal oxide arrayed thin films</strong>&rdquo;,
                            6<sup>th</sup> International Conference on Technological Advances of Thin Films &amp; Surface
                            Coatings, Symposium on Oxide Thin Films &amp; Nanostructures, Singapore, July 2012
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong class="blue_color">Panel discussion Chair/Symposiarch</strong>)</span>,
                            International Union of Materials Research Societies, International Conference of Young
                            Researchers
                            on Advanced Materials, Symposium on Energy &amp; Environment, Session on Hydrogen generation
                            &amp;
                            Storage, Singapore, July 2012
                        </li>
                        <li>
                            <strong>Q.Y. Chen</strong>, &ldquo;<strong>Surfactant&rsquo;s Effect on the Photoactivity of
                            Fe-doped TiO<sub>2</sub></strong>&rdquo;, 2012 Chinese Materials Conference, Taiyuan, China,
                            July
                            2012
                        </li>
                        <li>
                            <strong>D.W. Jing</strong> <span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>, <strong>L.J. Guo</strong>, &ldquo;<strong>Photocatalytic
                            hydrogen production under direct solar light: materials preparation, system optimization and
                            pilot
                            demonstration</strong>&rdquo;, 4<sup>th</sup> Sino-Thai Workshop on Renewable Energy, Tianjin,
                            May
                            2012
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>,&ldquo;<strong>Aqueous design of
                            quantum-confined
                            metal oxide hetero-nanostructures</strong>&rdquo;, 2012 MRS Spring Meeting, Cluster on
                            Nanostructured materials and devices, Symposium BB: Solution Synthesis of Inorganic Films and
                            Nanostructured Materials, San Francisco, CA, USA, April 2012
                        </li>
                        <li>
                            <strong>L.J. Guo </strong><span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>,&ldquo;<strong>The
                            photocatalytic activity of Cd<sub>0.5</sub>Zn<sub>0.5</sub>S/TNTs (titanate nanotubes)
                            synthesized
                            by a two-step hydrothermal method</strong>&rdquo;, Working Group Meeting for Discussing Green
                            Innovation Initiatives Especially on Renewable Energy, Bonn, Germany, March 2012
                        </li>
                        <li>
                            <strong>Y.J. Lv </strong><span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>,
                            &ldquo;<strong>Solar hydrogen production by biomass gasification in supercritical water:
                            Hydrogen
                            production and hydrodynamics characteristics in supercritical water fluidized bed</strong>&rdquo;,
                            243<sup>rd</sup> ACS National Meeting &amp; Exposition, March 2012
                        </li>
                        <li>
                            <strong>L.J. Guo </strong><span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>,&ldquo;<strong>Nanostructure
                            and Nanoheterojuction for High-Efficiency Photocatalytic and Photoelectrochemical Water
                            Splitting</strong>&rdquo;, 36<sup>th</sup> International Conference and Exposition on Advanced
                            Ceramics and Composites, Daytona Beach, Florida, USA, January 22-27, 2012
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong
                                class="blue_color">Keynote</strong>)</span>,&ldquo;<strong>Surface doping of W<sup>6+</sup>
                            for
                            enhanced photoelectrochemical water splitting over α-Fe<sub>2</sub>O<sub>3</sub> nanorod
                            photoanodes</strong>&rdquo;,
                            36<sup>th</sup> International Conference and Exposition on Advanced Ceramics and Composites,
                            Daytona
                            Beach, Florida, USA, January 22-27, 2012
                        </li>
                        <li>
                            <strong>S.H. Shen</strong>, &ldquo;<strong>Enhanced charge separation for high efficiency
                            photocatalytic hydrogen production</strong>&rdquo;, 36<sup>th</sup> International Conference and
                            Exposition on Advanced Ceramics and Composites, Daytona Beach, Florida, USA, January 22-27, 2012
                        </li>
                        <li>
                            <strong><u>J.W. Shi</u></strong>, J.H. Ye, <strong>L.J. Ma</strong>, S.X. Ouyang, <strong>D.W.
                            Jing</strong>, <strong>L.J. Guo</strong>, &ldquo;<strong>Upconversion luminescent Er doped
                            SrTiO<sub>3</sub>: Site-selected substitution and visible-light-driven photocatalytic
                            H<sub>2</sub>
                            or O<sub>2</sub> evolution</strong>&rdquo;, 36<sup>th</sup> International Conference and
                            Exposition
                            on Advanced Ceramics and Composites, Daytona Beach, Florida, USA, January 22-27, 2012
                        </li>
                        <li>
                            <strong>L. Vayssieres </strong><span class="invited">(<strong
                                class="blue_color">Keynote</strong>)</span>,&ldquo;<strong>Low cost all-oxide
                            hetero-nanostructures for direct solar water splitting</strong>&rdquo;, 2012 US-Vietnam Workshop
                            on
                            Solar Energy Conversion, Ho Chi Minh City, Vietnam, January 2012
                        </li>
                        <li>
                            <strong>S.H. Shen </strong><span class="invited">(<strong
                                class="blue_color">Plenary</strong>)</span>,&ldquo;<strong>Facile Aqueous Growth of Hematite
                            Photoanodes for Solar Water Splitting</strong>&rdquo;, 12<sup>th</sup> International Conference
                            on
                            Clean Energy, Xi&rsquo;an, China, January 2012
                        </li>
                        <li>
                            <strong>Q.Y. Chen </strong><span class="invited">(<strong
                                class="invited_cited_blue">Keynote</strong>)</span>, &ldquo;<strong>Co-production of
                            electricity
                            and hydrogen from microbial fuel cell</strong>&rdquo;, 12<sup>th</sup> International Conference
                            on
                            Clean Energy, Xi&rsquo;an, China, January 2012
                        </li>
                    </ol>
                    <h5 align="center" class="h5" style="margin-top:15px; margin-bottom:0px;">2011 (7)</h5>
                    <ol style="list-style-type:decimal; margin: 30px; padding:30px 10px;" reversed start="7">
                        <li>
                            <strong>L.J. Guo </strong><span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>,&ldquo;<strong>Single-crystal
                            nanosheet-based hierarchical AgSbO<sub>3</sub> with exposed {001} facets: topotactic synthesis
                            and
                            enhanced photocatalytic activity</strong>&rdquo;, 3<sup>rd </sup>China-Australia Symposium for
                            Materials Science, Gold Coast, Queensland, Australia, November 2011
                        </li>
                        <li>
                            <strong><u>J.W. Shi</u></strong>, <strong>L.J. Ma</strong>, <strong>P. Wu</strong>, <strong>Z.H.
                            Zhou</strong>, <strong>P.H. Guo</strong>, <strong>S.H. Shen</strong>, <strong>L.J. Guo</strong>,
                            &ldquo;<strong>A Novel Sn<sub>2</sub>Sb<sub>2</sub>O<sub>7</sub> Nanophotocatalyst for
                            Visible-light-driven H<sub>2</sub> Evolution</strong>&rdquo;, 3<sup>rd</sup> China-Australia
                            Symposium for Materials Science, Gold Coast, Queensland, Australia, November 2011
                        </li>
                        <li>
                            <strong><u>P. Wu</u></strong>, <strong>Z.H. Zhou</strong>, <strong>J.W. Shi</strong>,
                            &ldquo;<strong>First-principles calculations of Cd<sub>1-x</sub>Zn<sub>x</sub>S doped with
                            alkaline
                            earth metals for photocatalytic hydrogen generation</strong>&rdquo;, 12<sup>th</sup> National
                            Hydrogen Energy Conference and 4<sup>th</sup> Hydrogen Seminar of the three geographic areas,
                            Wuhan,
                            China, October 2011
                        </li>
                        <li>
                            <strong>L.J. Guo </strong><span class="invited">(<strong
                                class="blue_color">Invited</strong>)</span>,&ldquo;<strong>High-Efficiency
                            Solar Driven Photocatalytic Water Splitting for Hydrogen Generation: on Design concepts
                            Catalytic
                            Materials and Pilot-Scale Demonstration</strong>&rdquo;, 9<sup>th</sup> International Meeting of
                            Pacific Rim Ceramic Societies, Cairns, North Queensland, Australia, July 2011
                        </li>
                        <li>
                            <strong><u>J.W. Shi</u></strong>, J.H. Ye, Q.Y. Li, <strong>P.H. Guo</strong>, G.C. Xi, <strong>L.J.
                            Guo</strong>, &ldquo;<strong>Self-templated synthesis of single-crystal AgSbO<sub>3</sub>
                            nanosheets
                            for visible-light-driven photocatalytic O<sub>2</sub> evolution</strong>&rdquo;, 9<sup>th</sup>
                            International Meeting of Pacific Rim Ceramic Societies, Cairns, North Queensland, Australia,
                            July
                            2011
                        </li>
                        <li>
                            <strong>L.J. Guo</strong> <span class="invited">(<strong
                                class="invited_cited_blue">Invited</strong>)</span>,
                            &ldquo;<strong>Solar to Hydrogen&rdquo;-From Concepts Design of Advanced</strong>&rdquo;,
                            2<sup>nd</sup> International Workshop on Renewable Energy, July 2011
                        </li>
                        <li>
                            <strong>S.H. Shen</strong>, &ldquo;<strong>Surface Modification of α-Fe<sub>2</sub>O<sub>3</sub>
                            Nanorod Array Photoanodes for Improved Light-Induced Water Splitting</strong>&rdquo;, 2011 MRS
                            Spring Meeting and Exhibit, Symposium F: Renewable Fuels and Nanotechnology, San Francisco, USA,
                            April 2011
                        </li>
                    </ol>
                </div>
                <div id="divseminars">
                    <h3 align="center">
                        <strong><a id="seminars"></a>Seminars</strong> <span class="listcount">(68)</span></h3>
                    <ol style="list-style-type:decimal; margin: 30px; padding:30px 10px;" reversed start="68">
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>McGill University</strong>, Department of Materials
                            Engineering, <strong>Host: Prof. K. H. Bevan</strong>, Montreal, Canada, May 15, 2020
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>CNRS-Lasers</strong>, <strong>Plasmas & Photonics
                            Processes
                            Laboratory (LP3)</strong>, <strong>Host: Prof. A. Kabashin</strong>, Marseille, France, January
                            22,
                            2020
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Institut d'Electronique, de Microelectronique et de
                            Nanotechnologie (IEMN)</strong>, <strong>Host: Prof. E. Dogheche</strong>, Villeneuve d'ascq,
                            France, January 14, 2020
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Northwestern Polytechnic University</strong>, Institute
                            for
                            Flexible Electronics, <strong>Host: Prof. I. Perepichka</strong>, Xi'an, China, December 3, 2019
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Seoul National University</strong>, Center for
                            Nanoparticle
                            Research, Institute for Basic Science, <strong>Host: Prof. T. Hyeon</strong>, Seoul, Korea,
                            November
                            15, 2019
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Emory University</strong>, Emory Renewable Energy
                            Research &
                            Education Consortium, Department of Chemistry, <strong>Host: Prof. T. Lian</strong>, Atlanta,
                            GA,
                            USA, October 18, 2019
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Chang’an University</strong>, Chemical Engineering &
                            Technology, School of Environmental Science & Engineering, HongXue Lecture Series, <strong>Host:
                            Prof. Z. Zhou</strong>, Xi'an, China, March 13, 2019
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Center for Research & Advanced Studies of the National
                            Polytechnic Institute (CINVESTAV)</strong>, Department of Applied Physics, <strong>Host: Prof.
                            G.
                            Oskam</strong>, Merida, Yucatan, Mexico, February 25, 2019
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Ecole Polytechnique Federale de Lausanne (EPFL)</strong>,
                            Laboratory of Renewable Energy Science & Engineering, <strong>Host: Prof. S. Haussener</strong>,
                            Lausanne, Switzerland, December 21, 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>University of California Santa Cruz</strong>, Department
                            of
                            Chemistry & Biochemistry, <strong>Host: Prof. Y. Li</strong>, Santa Cruz, CA, USA, October 31,
                            2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Shaanxi University of Science & Technology</strong>,
                            Frontier Institute of Science &amp; Technology, School of Environmental Science & Engineering,
                            <strong>Host: Prof. C. Y. Wang</strong>, Xi'an, China, October 18, 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>National University of Singapore</strong>, Department of
                            Mechanical Engineering, <strong>Host: Prof. L. Lu</strong>, Singapore, July 26, 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Yale University</strong>, School of Engineering &
                            Applied
                            Sciences, Department of Chemical & Environmental Engineering Seminar Series, <strong> Host:
                            Prof. S.
                            Hu</strong>, New Haven, CT, USA, April 25, 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Lawrence Berkeley National Laboratory</strong>, Energy
                            Storage & Distributed Resources Division, Energy Technologies Area, Berkeley Electrochemistry
                            Seminar Series, <strong> Host: Dr. R. Kostecki</strong>, Berkeley, CA, USA, April 16, 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>California Institute of Technology</strong>, Joint
                            Center
                            for Artificial Photosynthesis, JCAP Seminar Series,<strong> Host: Dr. C. X. Xiang</strong>,
                            Pasadena, CA, USA, March 27, 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>University of California Davis</strong>, College of
                            Engineering, <strong> Host: Prof. S. Islam</strong>, Kemper Hall, Davis, CA, USA, February 28,
                            2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>University of California Berkeley</strong>, Renewable
                            and
                            Appropriate Energy Lab (RAEL), Energy & Resources Group, <strong> Host: Dr. D. Best</strong>,
                            Barrows Hall, Berkeley, CA, USA, January 31, 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>National Taiwan University</strong>, Department of
                            Chemistry, <strong> Host: Prof. R. S. Liu</strong>, Taiwan, China, November 10, 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Tamkang University</strong>, Department of Physics,
                            <strong>
                                Host: Prof. C. L. Dong</strong>, Taipei, China, November 9, 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>University of Warsaw</strong>, Centre of New
                            Technologies,
                            <strong> Host: Dr. A. Jelinska</strong>, Warsaw, Poland, May 30, 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>University of Szeged</strong>, Department of Inorganic &
                            Analytical Chemistry, <strong> Host: Prof. K. Schrantz</strong>, Szeged, Hungary, April 26, 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Hungarian Academy of Sciences</strong>,<strong> Host:
                            Prof.
                            J. S. Pap</strong>, MTA Headquarters, Readings Hall, Budapest, Hungary, April 20, 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>ETS-Ecole de Technologie Superieure</strong>, <strong>
                            Host:
                            Prof. S. Cloutier</strong>, Montreal, QC, Canada, April 6, 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong> INRS-Institut National de la Recherche
                            Scientifique</strong>, <strong> Host: Prof. F. Vetrone</strong>, Varennes, QC, Canada, April 5,
                            2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>University of Electronic Science & Technology of
                            China</strong>, Institute of Fundamental and Frontier Sciences, <strong>Host: Prof. Z. M.
                            Wang</strong>, Chengdu, P.R. China, December 16, 2016
                        </li>
                        <li>
                            <strong>Y. Liu</strong>
                            , <strong>Lawrence Berkeley National Lab</strong>, Joint Center for Artificial
                            Photosynthesis-JCAP
                            T3 Meeting (video conference), <strong>Host: Dr. F. M. Toma</strong>, Berkeley, CA, USA,
                            December 7,
                            2016
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>University of Houston</strong>, Physics Colloquium,
                            <strong>Host:
                                Prof. O. K. Varghese</strong>, Houston, TX, USA, November 17, 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <STRONG>SABIC Technology Center</STRONG>, Nanotechnology,
                            Corporate
                            Research &amp; Development, <strong>Host: Dr. I. N. Odeh</strong>, Sugar Land, TX, USA, November
                            15,
                            2016
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Rice University</strong>, IEEE Photonics Society Houston
                            Chapter Seminar, <strong>Host: Prof. I. Thomann</strong>, Houston, TX, USA, November 14, 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Lawrence Berkeley National Laboratory</strong>, Joint
                            Center
                            for Artificial Photosynthesis-JCAP Seminar Series, Chu Hall, <strong>Host: Dr. I. Sharp</strong>,
                            Berkeley, CA, USA, July 20, 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>University of Toronto</strong>, IEEE Toronto section,
                            <strong>Host: Prof. N. P. Kherani</strong>, Toronto, ON, Canada, June 24, 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>University of South Florida</strong>, Department of
                            Physics,
                            <strong>Host: Prof. M. H. Phan</strong>, Tampa, FL, USA, April 21, 2016
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Princeton University</strong>, Princeton Institute for
                            the
                            Science and Technology of Materials and Princeton Center for Complex Materials PRISM/PCCM
                            seminar
                            series, <strong>Host: Prof. B. Koel</strong>, Bowen Hall Auditorium, Princeton, NJ, USA, April
                            15,
                            2016
                        </li>
                        <li>
                            <strong>S.H. Shen</strong>,<strong> University of Wisconsin Madison</strong>, Department of
                            Chemistry, <strong>Host: Prof. Song Jin</strong>, Madison, WI, USA, February 23, 2016
                        </li>
                        <li>
                            <strong>Y. Liu</strong>,<strong> Lawrence Berkeley National Laboratory</strong>, Materials
                            Science
                            Division, Joint Center for Artificial Photosynthesis, <strong>Host: Dr. J. Ager</strong>,
                            Berkeley,
                            CA, October 12, 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Warsaw University</strong>, Centre of New Technologies,
                            <strong>Host: Prof. J. Augustynski</strong>, Warsaw, Poland, Sep. 21, 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>EMPA-Swiss Federal Laboratories for Materials Science
                            &amp;
                            Technology</strong>, <strong>Host: Dr. A. Braun</strong>, Dubendorf, Switzerland, August 20,
                            2015
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <STRONG><SPAN
                                lang="EN-US">Concordia University</SPAN></STRONG><SPAN
                                lang="EN-US">,</SPAN> Department of Physics, <SPAN lang="EN-US"></SPAN><STRONG><SPAN
                                lang="EN-US"></SPAN>Host: Prof. P. Bianucci</STRONG>, Montreal, Canada, June 18, 2015
                        </li>
                        <li>
                            <STRONG>L. Vayssieres</STRONG>, <STRONG>Ecole Polytechnique de Montreal</STRONG><SPAN
                                lang="EN-US">,</SPAN> Departement de Genie Physique, <STRONG>Host: Prof. C. Santato</STRONG>,
                            Montreal, Canada, June 12, 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong><span
                                lang="EN-US">The University of British Columbia</span></strong><span
                                lang="EN-US">,</span> Clean Energy Research Centre<span lang="EN-US">,</span><strong><span
                                lang="EN-US"> </span>Host: Prof. W. Merida</strong>, Vancouver, Canada, May 19, 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong><span
                                lang="EN-US">Xi'an Jiaotong University</span></strong><span
                                lang="EN-US">,</span> Bioinspired Engineering and Biomechanics Center<span
                                lang="EN-US">,</span><strong><span
                                lang="EN-US"> </span>Host: Prof. T. J. Lu</strong>, Xi'an, China, April 30, 2015
                        </li>
                        <li>
                            <strong>L.J. Guo</strong>, <strong>Yangze University</strong>, Geophysics and Oil Resource
                            Institute, <strong>Host: Prof. Z.S. Zhang</strong>, Jingzhou, Hubei, China, December 23, 2014
                        </li>
                        <li>
                            <strong>L.J. Guo</strong>,<strong> Nanjing Technology University</strong>, College of Materials
                            Science and Engineering, <strong>Host: Prof. H. Zhang</strong>, Nanjing, JiangSu, China,
                            December 2,
                            2014
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>,<strong> Massachusetts Institute of Technology</strong>,
                            Department
                            of Materials Science and Engineering, <strong>Host: Prof. H.L. Tuller</strong>, Cambridge, MA,
                            November 25, 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>,<strong> University of California Merced</strong>, School of
                            Engineering,<strong> Host: Prof. J. Lu</strong>, Merced, CA, August 29, 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Lawrence Berkeley National Laboratory</strong>, Advanced
                            Light Source - Center for X-ray Optics Seminar Series, <strong>Host: Prof. T. Cuk</strong>,
                            Berkeley, CA, August 27, 2014 
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>,<strong> University of California Berkeley</strong>, Department
                            of
                            Chemistry,<strong> Host: Prof. T. Cuk</strong>, Berkeley, CA, August 26, 2014 
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong><span
                                lang="EN-US">Peking University</span></strong><span
                                lang="EN-US">,</span> <span lang="EN-US">School of Physics, Institute of Condensed matter &amp; Materials Physics, State Key Lab for Mesoscopic Physics,</span><strong><span
                                lang="EN-US"> </span>Host: Prof. Q. Zhao</strong>, Beijing, China, May 16, 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <span lang="EN-US"><strong>Chinese Academy of Sciences</strong>, Technical Institute of Physics &amp; Chemistry, </span><span
                                lang="EN-US">Key Laboratory of Photochemical Conversion &amp; Optoelectronic Materials,</span><strong><span
                                lang="EN-US"> </span>Host: Prof. T. Zhang</strong>, Beijing, China, May 12, 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>,<strong> University of California Berkeley</strong>, Department
                            of
                            Mechanical Engineering, <strong>Host: Prof. S.S. Mao</strong>, Berkeley, CA, April 28, 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>,<strong>&nbsp;McGill University</strong>, Department of
                            Electrical
                            &amp; Computer Engineering,<strong>&nbsp;Host: Prof. Z. Mi</strong>, Montreal, Canada, April 14,
                            2014
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>,<strong> Arizona State University</strong>, College of Technology
                            &amp; Innovation, Department of Engineering &amp; Computing Systems,<strong> Host: Prof. A. M.
                            Kannan</strong>, Polytechnic Campus, Mesa, AZ, USA, March 11, 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>,&nbsp;<strong>The University of Auckland</strong>,
                            School of Chemical Sciences,&nbsp;<strong>Host: Prof. J. Travas-Sejdic</strong>,
                            Auckland, New Zealand, December 6, 2013
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Uppsala</strong><strong> University</strong>, Inorganic
                            Chemistry Seminar, Angstrom Laboratory, <strong>Host: Prof. G. Westin</strong>, Uppsala, Sweden,
                            November 5, 2013
                        </li>
                        <li><strong>I. Zegkinoglou</strong>,&nbsp;<strong>Lawrence Berkeley National Laboratory</strong>,
                            Materials Sciences Division, Host:&nbsp;<strong>Dr. R. Schoenlein</strong>, Berkeley, CA,
                            October
                            31, 2013
                        </li>
                        <li><strong>L. Vayssieres</strong>,<strong>&nbsp;McGill University</strong>, Chemistry
                            Department,<strong>&nbsp;Host: Prof. D. Perepichka</strong>, Montreal, Canada, October 25, 2013&nbsp;
                        </li>
                        <li><strong>I. Zegkinoglou</strong>,&nbsp;<strong>Molecular Foundry</strong>, Theory of
                            Nanostructured
                            Materials Facility, U.S. Department of Energy Nanoscale Science Research Center, Lawrence
                            Berkeley
                            National Laboratory,&nbsp;<strong>Host: Dr. D. Prendergast</strong>, Berkeley, CA, July 31, 2013
                        </li>
                        <li><strong>L. Vayssieres</strong>,<strong> Lawrence Berkeley National Laboratory</strong>, Advanced
                            Light Source and Center for X-ray Optics,<strong>&nbsp;Host: Dr. J.-H. Guo</strong>, Berkeley,
                            CA,
                            June 26, 2013
                        </li>
                        <li><strong>L. Vayssieres</strong>,&nbsp;<strong>Stanford</strong><strong> University</strong>,
                            Center
                            on Nanostructuring for Efficient Energy Conversion, US DOE Energy Frontier Research
                            Center,&nbsp;<strong>Host: Prof. X.L. Zheng</strong>, Palo Alto, CA, June 24, 2013
                        </li>
                        <li><strong>L. Vayssieres</strong>,<strong> University of California Davis</strong>, Department of
                            Chemistry, <strong>Host: Prof. F. Osterloh</strong>, Davis, CA, May 16, 2013
                        </li>
                        <li><strong>L. Vayssieres</strong>, <strong>Vietnam Academy of Science and Technology</strong>,
                            Institute of Materials Science, <strong>Host: Prof. Nguyen Van Hieu</strong>, Hanoi, Vietnam,
                            November 5, 2012
                        </li>
                        <li><strong>L. Vayssieres</strong>, <strong>National University of Singapore</strong>, Department of
                            Materials Science &amp; Engineering,<strong> Host: Prof. Q. Wang</strong>, Singapore, July 11,
                            2012
                        </li>
                        <li><strong>L. Vayssieres</strong>, <strong> Nanyang Technological University</strong>, School of
                            Physical &amp; Mathematical Sciences, Department of Physics &amp; Applied Physics, <strong>Host:
                                Prof. H. J. Fan</strong>, Singapore, July 9, 2012
                        </li>
                        <li><strong>E. Traversa</strong>, <strong>Chalmers Institute of Technology</strong>, Goteborg,
                            Sweden,
                            June 16-17, 2012
                        </li>
                        <li><strong>L. Vayssieres</strong>, <strong>PARC Xerox Company</strong>,<strong> Host: Dr. B.
                            Hsieh</strong>, Palo Alto, CA, May 15, 2012
                        </li>
                        <li>
                            <u>C.X. Kronawitter</u>, <strong>L. Vayssieres</strong>, B.R. Antoun, S.S. Mao, <strong>Yale
                            University</strong>, Center for Interface Structures &amp; Phenomena, New Haven, CT, April 2,
                            2012
                        </li>
                        <li><strong>L. Vayssieres</strong>, <strong>Nikon &amp; Essilor International Joint Research Center
                            Co.</strong>, <strong>Ltd.</strong>, <strong>Host: Dr. R. Bosmans</strong>, Kawasaki (Kanagawa),
                            Japan, March 22, 2012
                        </li>
                        <li>
                            <u>C.X. Kronawitter</u>, <strong>L. Vayssieres</strong>, B.R. Antoun, S.S. Mao, <strong>Brookhaven
                            National Laboratory</strong>, Photon Sciences Directorate, Upton, NY, February 19, 2012
                        </li>
                    </ol>
                </div>
                <div id="divorganizers">
                    <h3 align="center">
                        <strong><a id="organizers"></a>International Conference / Symposium / Workshop Chairman &amp;
                            Organizer</strong> <span class="listcount">(19)</span></h3>
                    <ol style="list-style-type:decimal; margin: 30px; padding:30px 10px;" reversed start="19">
                        <li>
                            <strong>L. Vayssieres</strong>, Co-organizer and Session Chairman, <strong>Symposium on Energy
                            Conversion</strong>, International Conference on Electroceramics (ICE), Ecole Polytechnique
                            Federale
                            de Lausanne (EPFL), Switzerland, July 14-19, 2019
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, lead-Organizer and Chairman, <strong>Symposium on Latest
                            Advances in
                            Solar Fuels</strong>, European MRS, Nice, France, May 21-31, 2019
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, Co-organizer and Chairman, <strong>6<sup>th</sup> International
                            Workshop on Nanotechnology, Renewable Energy &amp; Sustainability</strong>, Xi'an, P. R. China,
                            September 17, 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, Co-organizer, <strong>XXVII International Materials Research
                            Congress (IMRC 2018)</strong>, Symposium C3 on Solar Hydrogen Production, Cancun, Mexico, August
                            19-24, 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, Co-organizer and Chairman, <strong>5<sup>th</sup> International
                            Workshop on Nanotechnology, Renewable Energy &amp; Sustainability</strong>, Xi'an, P. R. China,
                            September 25, 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, Co-organizer and Chairman, <strong>4<sup>th</sup> International
                            Workshop on Nanotechnology, Renewable Energy &amp; Sustainability</strong>, Xi'an, P. R. China,
                            September 19, 2016
                        </li>
                        <li>
                            <STRONG>L. Vayssieres</STRONG>, Co-organizer and Co-chairman, <strong>9<sup>th</sup>
                            International
                            Conference on High Temperature Ceramic Matrix Composites &amp; </strong><strong>Global Forum on
                            Advanced Materials and Technologies for Sustainable Development</strong>, Symposium G2 on
                            Functional
                            Nanomaterials for Sustainable Energy Technologies, Toronto, Canada, June 26-30, 2016
                        </li>
                        <li>
                            <STRONG>L. Vayssieres</STRONG>, Co-Organizer and Chairman, <STRONG>3<sup>rd</sup> International
                            Workshop on Nanotechnology, Renewable Energy &amp; Sustainability</STRONG>, Xi'an, P. R. China,
                            September 28, 2015<BR>
                        </li>
                        <li>
                            <strong>S.H. Shen</strong>, Lead organizer and Chairman, <strong>Symposium on Solar Hydrogen and
                            Nanotechnology X</strong>, SPIE Optics &amp; Photonics, San Diego, CA, USA, August 9-13, 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, Co-organizer and
                            Co-chairman, <strong>Symposium J: </strong><strong>Latest
                            Advances in Solar Water Splitting</strong>, 2015 Spring Meeting of the Materials Research
                            Society
                            (MRS), San Francisco, USA, April 6-10, 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, Organizer and Co-chairman, <strong>2<sup>nd</sup> International
                            Workshop on Nanotechnology, Renewable Energy &amp; Sustainability</strong>, Xi'an, P. R. China,
                            September 19, 2014
                        </li>
                        <li><strong>L. Vayssieres</strong>,&nbsp;Co-organizer and Co-chair,&nbsp;<strong>Symposium on Solar
                            Fuels</strong>, American Ceramic Society Materials Challenges in Alternative&amp; Renewable
                            Energy
                            (MCARE 2014), Hilton Clearwater Hotel, Clearwater, FL, USA, February 16-20, 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, Chairman and&nbsp;Co-organizer,&nbsp;<strong>1<sup>st</sup>
                            International Workshop on Nanotechnology</strong>,<strong> Renewable Energy &amp;
                            Sustainability</strong>, Xi'an, P. R. China, September 25, 2013
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, Co-organizer, <strong>Symposium S19 on Advances in
                            Photocatalytic
                            Materials for Energy and Environmental Applications</strong>, 10<sup>th </sup>PACRIM meeting,
                            San
                            Diego, CA, USA, June 2-7, 2013
                        </li>
                        <li><strong>L. Vayssieres</strong>, Lead organizer and Chairman, <strong>Symposium Z on</strong>
                            <strong>Nanotechnology &amp; Sustainability</strong>, 2013 Spring Meeting of the Materials
                            Research
                            Society (MRS), San Francisco, USA, April 1-5, 2013
                        </li>
                        <li>
                            <strong>E. Traversa</strong>, Co-organizer,<strong> Symposium on</strong> <strong>Materials as
                            Tools
                            for Sustainability</strong>, 2012 Fall Meeting of the Materials Research Society, Boston,
                            November
                            26-30, 2012
                        </li>
                        <li>
                            <strong>E. Traversa</strong>, Co-organizer, <strong>Symposium on</strong> <strong>Solid State
                            Ionic
                            Devices 9-Ion Conducting Thin Films and Multilayers</strong>, Pacific Rim Meeting on
                            Electrochemical
                            and Solid-State Science PriME 2012, Joint International Meeting: 222<sup>nd </sup>Meeting of the
                            Electrochemical Society and 2012 Fall Meeting of the Electrochemical Society of Japan, Honolulu,
                            October 7-12, 2012
                        </li>
                        <li>
                            <strong>L.J. Guo</strong>,&nbsp;Chairman,&nbsp;<strong>Sino-German Workshop on Energy
                            Research</strong>,<strong>&nbsp;</strong>Xi'an, P. R. China, September 5-8, 2012
                        </li>
                        <li><strong>L. Vayssieres</strong>, Lead organizer and Chairman, <strong>Symposium on Solar Hydrogen
                            and
                            Nanotechnology VII</strong>, SPIE Optics &amp; Photonics meeting, San Diego, CA, USA, August
                            12-16,
                            2012
                        </li>
                    </ol>
                </div>
                <div id="divcommittee">
                    <h3>
                        <strong><a id="committee">International Advisory, Program, Executive or Steering Committee Member
                        </a></strong><span class="listcount">(29)</span>
                    </h3>
                    <ol style="list-style-type:decimal; margin: 30px; padding:30px 10px;" reversed start="29">

                        <li>
                            <strong>L. Vayssieres</strong>,&nbsp;<strong>The American Ceramic Society Global Ambassador
                            Program </strong> (2016-)
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>International Conference on Energy, Materials &
                            Photonics</strong>, Montreal, QC, Canada, July 8-11, 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>,&nbsp;<strong>UNESCO Africa Chair in Nanoscience
                            &amp;Nanotechnology </strong>(2013-)
                        </li>
                        <li>
                            <strong>L. Vayssieres, Indian Association of Nanoscience &amp; Nanotechnology (IANN)</strong>
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, SPIE Optics &amp; Photonics, <strong>Low Dimensional Materials &
                            Devices 2018</strong>, San Diego, CA, USA, August 19-23, 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <Strong>3<sup>rd</sup> International Symposium on Energy and
                            Environmental Photocatalytic Materials(EEPM3)</Strong>, Kraków, Poland, May 2018
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, SPIE Optics &amp; Photonics, <strong>Low Dimensional Materials &
                            Devices 2017</strong>, San Diego, CA, USA, August 6-10, 2017
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, SPIE Optics &amp; Photonics, <strong>Low Dimensional Materials &
                            Devices 2016</strong>, San Diego, CA, USA, August 28-September 1, 2016
                        </li>
                        <li>
                            <strong>S.H. Shen</strong>,
                            <strong>Energy Materials Nanotechnology (EMN) Meeting on Ultrafast Research</strong>, Las Vegas,
                            NV,
                            USA, November 16-19, 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>5</strong><strong><sup>th</sup></strong><strong>
                            International Workshop on Nanotechnology &amp; Application</strong>, Vung Tau, Vietnam, November
                            11-14, 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, SPIE Optics &amp; Photonics, <strong>Low Dimensional Materials &
                            Devices</strong>, San Diego, CA, USA, August 9-13, 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, SPIE Optics &amp; Photonics, <strong>Solar Hydrogen and
                            Nanotechnology X</strong>, San Diego, CA, USA, August 9-13, 2015
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>International Conference on Engineering and Scientific
                            Innovations</strong>, Mar Ephraem College of Engineering &amp; Technology, Elavuvilai,
                            Tamilnadu,
                            India, March 20-21, 2015<BR>
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>Regional African Materials Research Society (AMRS)
                            Workshop</strong>, iThemba LABS, Somerset West, South Africa, December 3-4, 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>African Laser Centre Annual Workshop</strong>, Rabat,
                            Morocco, November 3-5, 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, SPIE Optics &amp; Photonics,&nbsp;<strong>Solar Hydrogen and
                            Nanotechnology IX</strong>, San Diego, CA, USA, August 17-21, 2014
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, SPIE Optics &amp; Photonics,&nbsp;<strong>Nanoepitaxy: Materials
                            &amp; Devices VI</strong>, San Diego, CA, USA, August 17-21, 2014
                        </li>
                        <li><strong>L.J. Guo</strong>,<strong> 13<sup>th</sup>&nbsp;International Conference on Clean Energy
                            (ICCE2014)</strong>, Istanbul, Turkey, June 8-12, 2014
                        </li>
                        <li>
                            <strong>L.J. Guo</strong>,<strong>&nbsp;6<sup>th</sup>&nbsp;International Conference on Applied
                            Energy (ICAE2014)</strong>, Taipei, Taiwan, May 30-June 2, 2014
                        </li>
                        <li><strong>L. Vayssieres</strong>, <strong>Nano &amp; Giga Challenges in
                            Electronics</strong>,<strong>
                            Photonics and Renewable Energy: From Materials to Devices to System Architecture</strong>,
                            Symposium
                            and Spring School, Phoenix, Arizona, March 10-14, 2014
                        </li>
                        <li><strong>L. Vayssieres</strong>, SPIE Optics &amp; Photonics, <strong>Solar Hydrogen and
                            Nanotechnology VIII</strong>, San Diego, CA, USA, August 25-29, 2013
                        </li>
                        <li><strong>L. Vayssieres</strong>, SPIE Optics &amp; Photonics, <strong>Nanoepitaxy: Materials
                            &amp;
                            Devices V</strong>, San Diego, CA, USA, August 25-29, 2013
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>International Conference on</strong> <strong>Nanoscience
                            and
                            Nanotechnology: Lessons from Nature and Emerging Technologies</strong>, Ansal University,
                            Gurgaon,
                            India, July 25-26, 2013
                        </li>
                        <li>
                            <strong>L.J. Guo</strong>,&nbsp;<strong>1<sup>st</sup>&nbsp;Australia-China Joint Symposium on
                            Minerals</strong>,<strong> Metallurgy &amp; Materials</strong>, Beijing, China,&nbsp;June 9-12,
                            2013
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>12<sup>th </sup>International Conference of Clean Energy
                            (ICCE 2012)</strong>, Xi'an, China, October 26-30, 2012
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>1<sup>st</sup> International Conference on Emerging
                            Advanced
                            Nanomaterials</strong>, Brisbane, Australia, October 22-25, 2012
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>4<sup>th </sup>International Symposium on Transparent
                            Conductive Materials</strong>, Hersonissos, Crete, Greece, October 21-26,
                            2012
                        </li>
                        <li>
                            <strong> L. Vayssieres</strong>, SPIE Optics &amp; Photonics, <strong>Nanoepitaxy: Materials
                            &amp;
                            Devices IV</strong>, San Diego, CA, USA, August 12-16, 2012
                        </li>
                        <li>
                            <strong>L. Vayssieres</strong>, <strong>20<sup>th</sup> International Conference on Composites
                            nano
                            or metals Engineering</strong>, Beijing, China, July 22-28, 2012
                        </li>
                    </ol>

                </div>
            </div>
            <div id="backtothetop">
                <a href="#top"><img src="images/buttons/5.jpg" width="105" height="28" class="button"></a>
            </div>
        </div>
    </div>
    <div id="footer">
        <div id="footeraddress">
            <h3>International Research Center for Renewable Energy(IRCRE)</h3>
            <ul>
                <li>Tel: +86-29-82664664 Email: wangge2017@xjtu.edu.cn</li>
                <li>No.28,Xianning West road,Xi'an,Shaanxi,710049 CHINA</li>
            </ul>
        </div>
        <div id="copyright">
            <p>Copyright 2019. All rights reserved</p>
        </div>
    </div>

    <script src="./js/script.js"></script>
    <script src="./js/statistics.js"></script>
    </body>
    </html>

    '''
    # 要解析的bib文件的路径
    top15ArticleHtml = generateTop15ArtitleHtml(top15_bib_path)

    articleHtml = generateAricleHtml(sorted_articles_bib_path)

    bookHtml = generateBookHtml(others_bib_path)

    proceedHtml = generateProceedHtml(others_bib_path)

    editorialsHtml = generateEditorialsHtml(others_bib_path)

    with open(researchnew_html_path, 'w', encoding='utf8') as htmlfile:
        htmlfile.write(prebody + top15ArticleHtml +
                       articleHtml+bookHtml+proceedHtml+editorialsHtml + afterbody)


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