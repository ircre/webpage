# ircre-bibtex
 scientific outputs from ircre in bibtex format

这 是自动更新https://ircre.org/research.html 所用到的工具和实现。

我们使用python代码从bib生成research.html文件。

代码见code目录。bib文件见bib7image目录。生成的html文件见www目录。

在生成research.html文件的同时也生成一个research4googlecheck.html文件，便于检查引用次数。查得引用次数之后手动修改ircre.bib文件。

工作流程：通过浏览器打开research.html和research4googlecheck.html文件，检查每篇文章的引用次数，修改ircre.bib文件，提交。

web服务器系统会每天检查更新，调用code目录的生成工具，从ircre.bib生成research.html和research4googlecheck.html文件。代码会更新相关统计数据，排序，把对应的image拷贝到合适的地方。

添加新记录的流程：打开bib文件，添加一条记录，设置好记录的key，把对应的杂志的封面命名为$key.jpg, 放到bib7image目录下的articlecovers或者otherpublications下。提交整个修改，包括bib文件和对应的image。







