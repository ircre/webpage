# ircre-bibtex
scientific outputs from ircre in bibtex format

这是自动更新http://ircre.xjtu.edu.cn/research.html所用到的工具和实现。

本自动更新脚本使用到的工具有bibcure (https://github.com/bibcure/bibcure)
bibtexparser (https://github.com/sciunto-org/python-bibtexparser) bibtex-js(https://github.com/pcooksey/bibtex-js)
scholar.py (https://github.com/ckreibich/scholar.py)。

首先安装bibcure

pip install bibcure

我们可以使用doi2bib 获得bibtex的文献信息，
添加到ircre.bib中去。

然后根据这个到googlescholar上查询其clusterid，添加字段
根据clusterid查询引用，增加字段。

自动化的脚本根据ircre.bib定期去然后根据这个到googlescholar上查询引用次数的变化，进行排序。



