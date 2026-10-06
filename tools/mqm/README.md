# Multi-Query-MariaDB
Run multiple SQL queries against multiple MariaDB instances.

```mqm --hosts=127.0.0.1,localhost:3307,my-db.net:3306,10.0.0.2:3308 "select @@version; select 1"```

By default, mqm uses the ```[client]``` section in ```~/.my.cnf```.

The output is tab separated, which can easily be formatted:

```
$ ./mqm --hosts=127.0.0.1,127.0.0.1:3306,localhost "show status like 'threads%';" | column -t
127.0.0.1:3306
Variable_name      Value
Threads_cached     0
Threads_connected  3
Threads_created    39
Threads_running    1
127.0.0.1:3306
Variable_name      Value
Threads_cached     0
Threads_connected  3
Threads_created    39
Threads_running    1
localhost:3306
Variable_name      Value
Threads_cached     2
Threads_connected  1
Threads_created    39
Threads_running    1
```

```
$ ./mqm --hosts=127.0.0.1,127.0.0.1:3306,localhost "show status like 'threads%';" | tr "\t" ","
127.0.0.1:3306
Variable_name,Value
Threads_cached,0
Threads_connected,3
Threads_created,39
Threads_running,1

127.0.0.1:3306
Variable_name,Value
Threads_cached,0
Threads_connected,3
Threads_created,39
Threads_running,1

localhost:3306
Variable_name,Value
Threads_cached,2
Threads_connected,1
Threads_created,39
Threads_running,1```
