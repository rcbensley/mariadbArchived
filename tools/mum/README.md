Once upon a time I made a simple user manager for MySQL and MariaDB, long before I had started using MariaDB roles.

It works by applying changes using statement based replication. It was handy for when for whatever reason remote access was not working, e.g. a node has run out of disk space preventing new SSH sessions.

I may, one day, update these functions and stored procedures for use with MariaDB 10+ and Roles.

