Mysql_CodeGen为一个Python2.7的MySQ版的代码生成器，在Windows下编码完成并测试，需要安装MySQL-python-1.2.5。

1： 下载MySQL-python-1.2.5
2： 安装MySQL-python-1.2.5
解压缩MySQL-python-1.2.5
打开cmd并cd到MySQL-python-1.2.5的文件夹下。
运行cmd命令如下：
d:/python27/python setup build

如果发生如下错误，则说明VC++SDK未安装，需要安装，当前（2016-02-28）路径
（https://www.microsoft.com/en-us/download/confirmation.aspx?id=44266）

building '_mysql' extension
error: Microsoft Visual C++ 9.0 is required (Unable to find vcvarsall.bat). Get it from http://aka.ms/vcpython27

4： 运行Mysql_CodeGen.py
