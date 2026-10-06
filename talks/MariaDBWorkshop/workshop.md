## Environment

Run the VM:

    $ cd path/to/MariaDBWorkshop/vm
    $ vagrant up

Login to the VM:

    $ vagrant ssh

Login to the database:

    $ mysql

Login to the database as root:

    $ sudo mysql

## Configuration and Logs

Where is our error log?

    $ sudo systemctl mariadb.service

Where and what is in our config files?

    $ cat /etc/my.cnf

Where is our data?

    $ ls -aslh /var/lib/mysql

## Explore MariaDB Server

Login to our database:

    $ mysql

Login as root, using socket authentication:

    $ sudo mysql

Who am i?

    SQL> SELECT user();

What can I do?

    SQL> show grants;

## Built in databases, tables and functions

    SQL> SHOW DATABASES;
    SQL> SHOW SCHEMAS;
    SQL> USE information_schema;
    SQL> SHOW TABLES;
    SQL> USE mysql;

Select some from system tables, using both tabular and vertical output.

    SQL> SELECT ... ;
    SQL> SELECT ... \G

The processlist:

    $ mysql -NBe "select sleep(100);" &
    SQL> SHOW PROCESSLIST;

## Setup Replication

Create a new user for replication on both the master and the slave:

    SQL> grant replication slave on *.* to 'repl'@'%' identified by 'repl123'; 

What position is our master at?

    SQL> show master status;

Setup replication on our slave:

    SQL> change master to master_host='172.10.10.10',master_log_file='my_bin_log.X',master_log_pos=Y,master_user='repl',master_password='repl123';

Did it work?

    SQL> SHOW SLAVE STATUS\G

## Creating Data

Let's make a new database and use it, on the master (db1):

    SQL> CREATE DATABASE shop;
    SQL> USE shop;

Now create a table in this new database:

    SQL> source /vagrant/table.sql;

Does this new database and table exist on the slave (db2)?:

    SQL> SHOW CREATE TABLE shop.orders.sql;

Insert some data:

    SQL> INSERT INTO TABLE shop.orders (customer_id, product_id, invoice_id) VALUES (1, 2, 3);

Select some data, from db2 as well:

    SQL> SELECT COUNT(*) FROM shop.orders;
    SQL> SELECT * FROM shop.orders;
    SQL> SELECT * FROM shop.orders WHERE order_id = LAST_INSERT_ID();
    SQL> select o.customer_id, COUNT(o.product_id), p.product_name FROM orders o JOIN products p on o.product_id = p.product_id group by o.customer_id, o.product_id;

Add another column to our table:

    SQL> ALTER TABLE shop.orders ADD COLUMN order_notes TEXT DEFAULT NULL;

## Backup and Restore

Logical VS Binary backups.

Create a backup user on db1, db2 and db3:

    SQL> GRANT ALL PRIVILEGES ON *.* TO 'backup'@'%' IDENTIFIED BY 'backup123';

## Provision db3 from a backup

On db3, create users we need:

    SQL> grant replication slave on *.* to 'repl'@'%' identified by 'repl123'; 
    SQL> GRANT ALL PRIVILEGES ON *.* TO 'backup'@'%' IDENTIFIED BY 'backup123';

Create a logical backup to provision db3 with:

    $ mysqldump -ubackup -pbackup123 --all-databases --routines --triggers --events --single-transaction --quick --master-data=2 > /tmp/db1_bkp.sql

Restore the backup to db3 from db1:

    $ mysql -h 172.10.10.10 -ubackup -pbackup123 < /tmp/db1_bkp.sql

Get the master position from the backup file:

    $ grep "^\-\-\ CHANGE\ MASTER\ TO" /tmp/db1_bkp.sql
    or
    $ less /tmp/db1_bkp.sql

Start and monitor replication on db3:

    SQL> change master to master_host='172.10.10.10',master_log_file='my_bin_log.X',master_log_pos=Y,master_user='repl',master_password='repl123';
    SQL> START SLAVE;
    SQL> SHOW SLAVE STATUS\G

## Taking a look at the binlogs

Let's take a look at what binlogs we have:

    SQL> show binary logs;

When do they expire?

    SQL> SELECT @@expire_logs_days;
    SQL> SELECT @@max_binlog_size;

What do they contain?

    SQL> show binlog events in 'my_bin_log.X' limit 10;

Using mysqlbinlog:

    mysqlbinlog --base64-output=decode-rows --verbose /var/lib/mysql/my_bin_log.X | less

## End

Wrap up and Q&A.