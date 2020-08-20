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


def openproxy():
    try:
        sshid = os.popen('''ps aux | grep 9524| grep ssh''').read().strip().split()[1]
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
        '''cp ''' + ircrebibwebsitefile + ''' ''' + currentdir + '''/ -f ; cp ircre.bib ircre'''
        + str(dt.year) + str(dt.month) + str(dt.day) + '''.bib;''')
    os.system(
        '''cd ''' + currentdir + ''';''' +
        '''cp ''' + ircrestatwebsitefile + ''' ''' + currentdir + '''/ -f ; cp statistics.js statistics'''
        + str(dt.year) + str(dt.month) + str(dt.day) + '''.js;''')
    return 0


def bibtexclassify():
    parser = BibTexParser(common_strings=False)
    parser.ignore_nonstandard_types = False
    currentdir = os.path.dirname(os.path.abspath(__file__))
    ircre_bib_path = currentdir+r'/../bib7image/ircre.bib'

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
    with open(currentdir+r'/../bib7image/articles.bib', 'w', encoding='utf8') as article_file:
        bibtexparser.dump(article_database, article_file, writer=writer)

    otherentries= []
    for i in range(len(allentries)):
        if allentries[i]['ENTRYTYPE'] == 'inbook' or allentries[i]['ENTRYTYPE'] == 'inproceedings' or allentries[i]['ENTRYTYPE'] == 'incollection':
            otherentries.append(allentries[i].copy())

    other_database = BibDatabase()
    other_database.entries = otherentries

    writer2 = BibTexWriter()
    writer2.indent = '    '
    writer2.order_entries_by = ('order',)
    with open('../bib7image/others.bib', 'w', encoding='utf8') as others_file:
        bibtexparser.dump(other_database, others_file, writer=writer2)


    return 0


def articlessort():
    parser = BibTexParser(common_strings=False)
    parser.ignore_nonstandard_types = False

    with open('../bib7image/articles.bib', encoding='utf8') as articlesfile:
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

    sorted_by_journalif_cited = sorted(articles, key=lambda x: (x['sortkey1'], x['journal'], x['sortkey2'], x['year']),
                                       reverse=True)

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
    with open('../bib7image/sorted-articles.bib', 'w', encoding='utf8') as sortedarticlesfile:
        bibtexparser.dump(sortedarticlesdatabase, sortedarticlesfile, writer=writer)

    return 0


def getop15articles():
    parser = BibTexParser(common_strings=False)
    parser.ignore_nonstandard_types = False

    with open('../bib7image/articles.bib', encoding='utf8') as article_file:
        article_database = bibtexparser.load(article_file, parser)

    article_entries = article_database.entries.copy()

    for i in range(len(article_entries)):
        try:
            article_entries[i]['sortkey1'] = int(article_entries[i]['cited'])
        except:
            article_entries[i]['sortkey1'] = int(0)

    articles_sorted_by_cited = sorted(article_entries, key=lambda x: (x['sortkey1']), reverse=True)

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

    with open('../bib7image/top15.bib', 'w', encoding='utf8') as top15_file:
        bibtexparser.dump(top15_database, top15_file, writer=writer)
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


def ircrebibmerge():
    articlesparser = BibTexParser(common_strings=False)
    articlesparser.ignore_nonstandard_types = False

    with open('../bib7image/sorted-articles.bib', encoding='utf8') as sortedarticle_file:
        sortedarticle_database = bibtexparser.load(sortedarticle_file, articlesparser)

    sortedarticles = sortedarticle_database.entries.copy()

    top15parser = BibTexParser(common_strings=False)
    top15parser.ignore_nonstandard_types = False

    with open('../bib7image/top15.bib', encoding='utf8') as top15_file:
        top15_database = bibtexparser.load(top15_file, top15parser)

    top15articles = top15_database.entries.copy()


    othersparser = BibTexParser(common_strings = False)
    othersparser.ignore_nonstandard_types = False

    with open('../bib7image/others.bib', encoding='utf8') as others_file:
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

    with open('../bib7image/newircre.bib', 'w', encoding='utf8') as newircrebibfile:
        bibtexparser.dump(alldb, newircrebibfile, writer=writer)

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

        os.popen("cp /home/limingtao/ircre-bibtex/ircreupdate/cited-add-articles.bib tempcited-add-articles.bib")

    os.popen("cp /home/limingtao/ircre-bibtex/ircreupdate/articles.bib /home/limingtao/ircre-bibtex/ircreupdate/oldarticles.bib")
    with open('/home/limingtao/ircre-bibtex/ircreupdate/articles.bib', 'w', encoding='utf8') as newarticlefile:
        bibtexparser.dump(articles_database, newarticlefile, writer=writer)

    return 0


def entryadd(doi):
    pass


def updatestatistics():
    articlesparser = BibTexParser(common_strings=False)
    articlesparser.ignore_nonstandard_types = False
    with open('../bib7image/articles.bib', encoding='utf8') as articlesfile:
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
    # print(totalcitations)
    # print(hindex)
    # print(i10index)
    # print(citationperpaper)
    # print(journalnumber)
    # print(averageif)
    # print(hihonumber)
    # print(totalpublications)

    with open('/home/limingtao/ircre-bibtex/ircreupdate/newstatistics.js', 'w', encoding='utf8') as statisticsjsfile:
        statisticsjsfile.write('totalpublications = "%d";\n' % totalpublications)
        statisticsjsfile.write('totalarticles = "%d";\n' % totalarticles)
        statisticsjsfile.write('totalcitations = "%d";\n' % totalcitations)
        statisticsjsfile.write('hindex = "%d";\n' % hindex)
        statisticsjsfile.write('i10index = "%d";\n' % i10index)
        statisticsjsfile.write('numberjournals = "%d";\n' % journalnumber)
        statisticsjsfile.write('numberesihighlycited = "%d";\n' % hihonumber)
        statisticsjsfile.write('citationperpaper = "%.2f";\n' % citationperpaper)
        statisticsjsfile.write('averageif = "%.3f";\n' % averageif)
    return 0


def Hindex(citationlist):
    indexSet = sorted(list(set(citationlist)), reverse=True)
    for index in indexSet:
        clist = [i for i in citationlist if i >= index]
        if index <= len(clist):
            break
    return index


def I10index(citationlist):
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
    return 0


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


if __name__ == '__main__':
    sys.exit(main())
