DROP TABLE IF EXISTS login_users;
CREATE TABLE IF NOT EXISTS login_users (
    login_name CHAR(16) NOT NULL PRIMARY KEY,
    login_type ENUM('SRV','DEV','MON') NOT NULL,
    created DATETIME NOT NULL,
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    expiry_time DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;

DROP TABLE IF EXISTS login_hosts;
CREATE TABLE IF NOT EXISTS login_hosts (
    login_host_id INT(4) NOT NULL AUTO_INCREMENT,
    login_hostname VARCHAR(64) NOT NULL,
UNIQUE INDEX idx_hostname (login_host_id, login_hostname)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;

DROP TABLE IF EXISTS login_status;
CREATE TABLE IF NOT EXISTS login_status (
    login_name CHAR(16) NOT NULL,
    login_host_id INT(4) NOT NULL,
    login_status ENUM('ACCESS','LOCKED') NOT NULL,
UNIQUE INDEX idx_status (login_name, login_host_id, login_status),
FOREIGN KEY (login_name) REFERENCES login_users(login_name) ON DELETE CASCADE,
FOREIGN KEY (login_host_id) REFERENCES login_hosts(login_host_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;

DROP VIEW IF EXISTS v_user_status;
CREATE VIEW v_user_status AS
    SELECT
        lu.login_name 'Username'
        , lh.login_hostname AS 'Hostname'
        , ls.login_status AS 'Status'
        , lu.login_type AS 'Type'
        , lu.created AS 'Created'
        , lu.updated AS 'Updated'
        , lu.expiry_time AS 'Expires'
    FROM login_status ls
    JOIN login_users lu ON ls.login_name = lu.login_name
    JOIN login_hosts lh ON ls.login_host_id = lh.login_host_id
    ORDER BY 1;
