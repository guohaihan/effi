#数据库用户名
user="guozhi"
#数据库密码
passwd="guozhi"
#备份文件存放目录
backupdir="/data/backup/sqlbackup"
#备份数据库名
#dbname="guozhi_tenant_1"
#备份表名

dbname=$(mysql -u$user -p$passwd -h 172.16.0.65 -ss -e "show databases;")

#当前时间
date=$(date +%Y%m%d%H%M)

#过期时间
outtime=20
#判断备份目录是否存在
if [ ! -d $backupdir/$date ];then
mkdir -p $backupdir/$date
fi
cd $backupdir/$date
for databasename in $dbname

do
#判断是否为系统表
if [ $databasename != "mysql" ] && [ $databasename != "information_schema" ] && [ $databasename != "release_connection" ]\
&& [ $databasename != "performance_schema" ] && [ $databasename != "sys" ] && [ $databasename != "log" ] && [ $databasename != "test" ];then
#备份出来的文件名
backfile=$databasename.sql
mysqldump -u$user -p$passwd -h 172.16.0.65 $databasename --single-transaction > $backupdir/$date/$backfile
fi
done
cd $backupdir
file=$date".tar.gz"
tar -zcvf $file $date/*
rm -rf $date

#delete before 20
#find $backupdir -name *.tar.bz2 -mtime +$outtime |xargs rm -rf
find $backupdir -name *.tar.gz -mtime +$outtime -exec rm -f {} \;
