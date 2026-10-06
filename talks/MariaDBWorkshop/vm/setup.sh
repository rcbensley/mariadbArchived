sudo cp /vagrant/${HOSTNAME}.cnf /etc/my.cnf
sudo cp /vagrant/MariaDB.repo /etc/yum.repos.d/MariaDB.repo

sudo dnf update -y
sudo dnf upgrade -y
sudo dnf install -y python3-PyMySQL vim tmux
sudo dnf install -y MariaDB-server MariaDB-backup
sudo systemctl enable mariadb
sudo systemctl start mariadb

sudo mysql -NBe "GRANT ALL PRIVILEGES ON *.* TO 'vagrant'@'localhost' IDENTIFIED VIA unix_socket;"
sudo mysql -NBe "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP ON *.* TO 'shop_user'@'%' identified by 'shop123';"
sudo mysql -NBe "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP ON *.* TO 'shop_user'@'localhost' identified by 'shop123';"
sudo mysql -NBe "GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' identified by 'admin123' WITH GRANT OPTION;"
sudo mysql -NBe "GRANT ALL PRIVILEGES ON *.* TO 'admin'@'localhost' identified by 'admin123' WITH GRANT OPTION;"