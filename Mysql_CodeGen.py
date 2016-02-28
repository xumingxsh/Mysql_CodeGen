# 徐敏荣
# 2014-04-18
# 整理，重新编写
# 该代码主要实现从MySQL中读取数据库表结构，并自动生成某些有规律的代码
import MySQLdb
from StringIO import StringIO
from string import Template

#表结构
class TableInfo:
    # 构造函数
    def __init__(self):       
        self.table_Name = ""        # 数据表英文名称
        self.table_Comment = ""     # 数据表中文名称或相关注释
        self.nameLower = ""         # 所属用户

# 扩展表结构
class TableEx:
    def __init__(self):
        self.base = None            # 表结构
        self.columns = []           # 表的列集合
        self.keys = []              # 表的主键集合

# 列结构
class ColumnInfo:
    # 构造函数
    def __init__(self):
        self.table_Name = ""        # 所属表名称
        self.column_Name = ""       # 列名称
        self.data_Type = ""         # 数据类型
        self.column_Default = ""    # 默认值
        self.is_Nullable = ""       # 是否允许为空
        self.column_Comment = ""    # 列中文名称或注释
        self.charLen = None         # 是否允许为空
        self.len = None             # 数据长度
        self.isKey = 0              # 是否主键
        self.extra = ""             # 是否是自增字段
        self.precision=None         # 双精度
        self.scale=None             #


# 表结构的SQL辅助类，主要用于生成SQL语句
class TableExForSQL:  
    def __init__(self, tb):
        self.tb = tb                # 使用的表

    # 打印表结构信息
    def show(self):
        print '%s\t%s' % (self.tb.base.table_Name, self.tb.base.table_Comment)
        print "---------------------------------------"
        for i in self.tb.columns:
            nullStr = "\t not null "
            if i.is_Nullable.lower() != 'no':
                nullStr = ""
            print '%s\t%s%s\t%s\t%s' % (i.column_Name, i.data_Type,self.getColumnLen(i),nullStr, i.column_Comment)
            
    # 打印列结构信息
    # i-列结构
    def columnSQL(self, column):
        nullStr = "\t not null "    # 是否允许为空
        if column.is_Nullable.lower() != 'no':
            nullStr = " "
        defStr = "\t default "      # 默认值
        if column.column_Default == '' or\
            column.column_Default == None or \
            column.column_Default == '0000-00-00 00:00:00':
            defStr = ""
        else:
            defStr += " " + column.column_Default + " "
        comStr = ""                 # 注释信息
        if column.column_Comment != '' and column.column_Comment != None:
            comStr = "\t comment '" + column.column_Comment + "'"
        autoCreat = ""              # 是否是自增字段
        if column.extra == "auto_increment":
            autoCreat = "\t auto_increment "
        return '\t' + column.column_Name + '\t' + column.data_Type + self.getColumnLen(column) + nullStr + autoCreat + defStr +  comStr

    # 数据库表创建语句
    def createSQL(self):
        print "/*%s\t%s*/" % (self.tb.base.table_Name, self.tb.base.table_Comment)  # 注释信息
        print "create table %s\n(" % self.tb.base.table_Name
        # 打印列语句
        for column in self.tb.columns:
            print self.columnSQL(column) +  ','

        # 打印主键语句
        key = ''
        for i in self.tb.keys:
            if key !=  '':
                key += ','
            key += i.column_Name
        key = '\tprimary key (' + key + ')'
        print key + "\n);\n"

        # 打印注释信息
        if self.tb.base.table_Comment != '' and self.tb.base.table_Comment != None:
            print "alter table %s comment '%s';" % (self.tb.base.table_Name, self.tb.base.table_Comment)

    # 表移除SQL
    def dropSQL(self):
        print "drop table if exists %s;" % (self.tb.base.table_Name)
        
    # 单条记录查询
    def getSQL(self):
        cls = ""
        for i in self.tb.columns:
            if cls != "\t":
                cls += "\n\t,"
            cls += i.column_Name.lower()
        print  "\tSelect " + cls + " From " + self.tb.base.table_Name
        
    # 添加列
    def addColumns(self):
        for i in self.tb.columns:
            print "alter   table %s add %d " % (self.tb.base.table_Name, self.column(i))

    # 获得列长度
    def getColumnLen(self, i):
        if i.data_Type == "decimal"\
            or i.data_Type == "double" \
            or i.data_Type == "float":
            if i.scale is None:
                return "(%d)"%(i.precision)
            else:
                return "(%d,%d)"%(i.precision, i.scale)
        if i.data_Type == "text":
            return ''
        if i.charLen != None and i.charLen != "":
            return '(%d)'%i.charLen
        return ''
    
# 获得列数据类型
def getParamType_Java_MyBatis(self, i):
    if i.data_Type == "int"\
       or i.data_Type == "decimal"\
       or i.data_Type == "double" \
       or i.data_Type == "smallint" \
       or i.data_Type == "tinyint" \
       or i.data_Type == "float":
        return "NUMERIC"
    if i.data_Type == "timestamp":
        return "TIME"
    return "VARCHAR"

# 添加记录SQL(适用于mybatis)
def insertSQL_Java_MyBatis(self):
    params = ""
    values = ""
    for i in self.tb.columns:
        if i.extra == "auto_increment" or\
           i.column_Comment == "CURRENT_TIMESTAMP      comment":
            continue
        if params != "":
            params += "\t, "
        else:
            params += "\t"
        params += i.column_Name.lower() + "\n"
        if values != "":
            values += "\t, "
        else:
            values += "\t"
        t = Template('#{${name},jdbcType=${type}}\n')
        values += t.substitute(name=i.column_Name.lower(), type=self.getParamType_Java_MyBatis(i))
    print "\tInsert Into %s(\n%s\t) Values (\n%s\t)" % (self.tb.base.table_Name,params,values)  

# 编辑记录SQL(适用于mybatis)
def updateSQL_Java_MyBatis(self):
    params = ""
    for i in self.tb.columns:
        if i.extra == "auto_increment" or i.column_Comment == "CURRENT_TIMESTAMP      comment":
            continue
        if params != "":
            params += "\t, "
        else:
            params += "\t"
        t = Template('${name} = #{${name},jdbcType=${type}}\n')
        params += t.substitute(name=i.column_Name.lower(), type=self.getParamType_Java_MyBatis(i))
    values = ""
    for i in self.tb.keys:
        if values != "":
            values += "\t, "
        else:
            values += "\t"
        t = Template('${name} = #{${name},jdbcType=${type}}\n')
        values += t.substitute(name=i.column_Name.lower(), type=self.getParamType(i))
    print "\tUpdate %s SET \n%s\t Where %s " % (self.tb.base.table_Name, params, values)

TableExForSQL.insertSQL = insertSQL_Java_MyBatis
TableExForSQL.updateSQL = updateSQL_Java_MyBatis
TableExForSQL.getParamType_Java_MyBatis = getParamType_Java_MyBatis
 
class TableExForMapper:  
    def __init__(self, tb):
        self.tb = tb
        self.sql = TableExForSQL(tb)
    def insert(self):
        print '<insert id="add" parameterType="' + self.tb.base.table_Name.capitalize() + 'PO">'
        self.sql.insertSQL()
        print '</insert>'
    def update(self):
        print '<update id="update" parameterType="' + self.tb.base.table_Name.capitalize() + 'PO">'
        self.sql.updateSQL()
        print '</update>'
    def selectList(self):
        print '<select id="getList" parameterType="' + self.tb.base.table_Name.capitalize() + \
              'QO" resultType="' + self.tb.base.table_Name.capitalize() + 'VO">'
        self.sql.getSQL()
        print "\t LIMIT #{recordStart, jdbcType=NUMERIC},#{rows, jdbcType=NUMERIC}"
        print '</select>'
 
class TableExForJava:
    def __init__(self, tb):
        self.tb = tb     
    def createPO(self):
        propertys = ""
        for i in self.tb.columns:
            typ = "String"
            if i.data_Type == "int":
                typ = "int"
            if i.data_Type == "timestamp":
                typ = "Date"
            if i.column_Comment != '' and i.column_Comment != None:
                print "\t/**"
                print "\t*" + i.column_Comment
                print "\t*/"
            print "\tprivate " + typ + " " + i.column_Name.lower() + ";"
            t = Template("\tpublic ${type} get ${nameU}() {\n"
                         "\t\treturn this.${name};\n"\
                         "\t}\n\n"\
                         "\tpublic void set ${nameU}(${type} ${name}) {\n"\
                         "\t\tthis.${name} = ${name};\n"\
                         "\t}\n\n")
            #propertys += "\tpublic " + typ + " get" + i.column_Name.lower().capitalize() + "() {\n"
            #propertys += "\t\treturn this." + i.column_Name.lower() + ";\n"
            #propertys += "\t}\n\n"
            #propertys += "\tpublic void set" + i.column_Name.lower().capitalize() + "(" + typ + " " + i.column_Name.lower() + " ) {\n"
            #propertys += "\t\tthis." + i.column_Name.lower() + " = " + i.column_Name.lower() + ";\n"
            #propertys += "\t}\n\n"
            propertys = t.ssubstitute(type=typ, nameU=i.column_Name.lower().capitalize(), name=i.column_Name.lower())
            print ""
            if i.data_Type != "timestamp":
                continue
            print "\tprivate String " + i.column_Name.lower() + "Str;"
            propertys += "\tpublic String get" + i.column_Name.lower().capitalize() + "Str() {\n"
            propertys += "\t\treturn TypeCommon.ConvertToString(this." + i.column_Name.lower() + ");\n"
            propertys += "\t}\n\n"
        print propertys
    def dataGridColums(self):
        for i in self.tb.columns:
            comment = i.column_Name
            if i.column_Comment != '' and i.column_Comment != None:
                comment = i.column_Comment
            print  '\t\t <th field="' + i.column_Name.lower() + '" width="100px">' + comment + '</th>'
 
class DBGencode:
    def __init__(self, host, port, db, user, pwd):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.db = db
        self.con = MySQLdb.connect(host=self.host,port=self.port,\
                                   db='information_schema',user=self.user,passwd=self.pwd,\
                                   charset="gbk")
        cur = self.con.cursor()
        cur.execute("select table_Name, table_Comment from tables where TABLE_SCHEMA='" + self.db + "'")
        self.tables=[]
        self.tableExs=[]
        self.columns=[]
        for i in cur.fetchall():
            t = TableInfo()
            t.table_Name = i[0]
            t.nameLower = t.table_Name.lower()
            arr = i[1].split(";")
            if len(arr) > 1:
                t.table_Comment = arr[0]
            else:
                t.table_Comment = ""
            self.tables.append(t)
        cur.execute("select Table_Name, Column_Name," \
                    + "Data_Type,Column_Default,Is_Nullable,Column_Comment,"\
                    "CHARACTER_MAXIMUM_LENGTH, COLUMN_KEY, extra,NUMERIC_PRECISION,NUMERIC_SCALE from COLUMNS where TABLE_SCHEMA='"\
                    + self.db + "' ")
        for i in cur.fetchall():
            c = ColumnInfo()
            c.table_Name = i[0]
            c.column_Name = i[1]
            c.data_Type = i[2]
            c.column_Default = i[3]
            c.is_Nullable = i[4]
            c.column_Comment = i[5]
            c.charLen = i[6]
            if i[7] == 'PRI':
                c.isKey = 1
            c.extra = i[8]
            c.precision = i[9]
            c.scale = i[10]
            self.columns.append(c)
        for i in self.tables:
            tb = TableEx()
            tb.base = i
            for it in self.columns:
                if it.table_Name.lower() != i.table_Name.lower():
                    continue
                tb.columns.append(it)
                if it.isKey == 1:
                    tb.keys.append(it)
            self.tableExs.append(tb)
    def showTables(self):
        for i in self.tables:
            #print str(i)
            print '%s\t%s' % (i.table_Name, i.table_Comment)
            #print i.table_Comment
    def showColumns(self):
        for i in self.columns:
            print '%s\t%s\t%s' % (i.column_Name, i.data_Type,i.column_Comment)
    def getTable(self, name):
        nameLw = name.lower()
        for i in self.tableExs:
            if i.base.nameLower == nameLw:
                return i
        return None
    def showTable(self, name):
        tb = self.getTable(name)
        if tb == None:
            print u"没有查找到数据库表：" + name
            return
        sql = TableExForSQL(tb)
        sql.show()
    def showDataBase(self):
        for i in self.tableExs:
            sql = TableExForSQL(i)
            sql.show()
            print ""
            print ""
    def showCreateSQLs(self):
        for i in self.tableExs:
            sql = TableExForSQL(i)
            sql.createSQL()
            print ""
            print ""
    def dropSQLs(self):
        for i in self.tableExs:
            sql = TableExForSQL(i)
            sql.dropSQL()
    def insertSQLs(self):
        for i in self.tableExs:
            sql = TableExForSQL(i)
            print ""
            print ""
            sql.insertSQL()
    def updateSQLs(self):
        for i in self.tableExs:
            sql = TableExForSQL(i)
            print ""
            print ""
            sql.updateSQL()
    def sqls(self):
        for i in self.tableExs:
            sql = TableExForSQL(i)
            print ""
            print i.base.table_Name
            print "----------------------------"
            print u"添加语句"
            sql.insertSQL()
            print ""
            print u"更新语句"
            sql.updateSQL()
            print ""
            print u"查询语句"
            sql.getSQL()
            print ""
            print u"添加列"
            sql.addColumns()
    def insertXMLs(self):
        for i in self.tableExs:
            mapper = TableExForMapper(i)
            print ""
            print ""
            mapper.insert()
    def updateXMLs(self):
        for i in self.tableExs:
            mapper = TableExForMapper(i)
            print ""
            print ""
            mapper.update()
    def XMLs(self):
        for i in self.tableExs:
            mapper = TableExForMapper(i)
            print ""
            print i.base.table_Name
            print "----------------------------"
            print u"添加语句"
            mapper.insert()
            print ""
            print u"更新语句"
            mapper.update()
            print ""
            print u"查询语句"
            mapper.selectList()
    def javas(self):
        for i in self.tableExs:
            jv = TableExForJava(i)
            print ""
            print i.base.table_Name
            print "----------------------------"
            print u"PO属性"
            jv.createPO()
            print ""
            print u"列表列"
            jv.dataGridColums()           
    def createSQLs(self):
        for i in seinsertSQLslf.tableExs:
            sql = TableExForSQL(i)
            mylookup = TemplateLookup(directories=['docs'],\
                module_directory='tmp/mako_modules', collection_size=500, output_encoding='utf-8', encoding_errors='replace')
            mytemplate = mylookup.get_template('createSQL.sql')
            print mytemplate.render(table=i, tb=i.base, sql=sql)

code=DBGencode("127.0.0.1", 3306, "ivsm", "root", "root")

code.insertSQLs()
code.showCreateSQLs()
