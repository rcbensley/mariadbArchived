DELIMITER $$

-- Get environment
DROP FUNCTION IF EXISTS mum_server_environment $$
CREATE DEFINER=`DBO`@`localhost`
FUNCTION mum_server_environment(hostname VARCHAR(64)) RETURNS VARCHAR(32)

LANGUAGE SQL
DETERMINISTIC
SQL SECURITY DEFINER
READS SQL DATA
COMMENT 'Returns the environment of the server i.e. UATDEV'

BEGIN
DECLARE mysql_environment VARCHAR(32);
SET mysql_environment=UCASE(SUBSTRING_INDEX(SUBSTRING_INDEX(hostname, '.', 2), '.', -1));
RETURN mysql_environment;
END $$


-- Check MySQL/MariaDB user exists
DROP FUNCTION IF EXISTS mysql_user_exists $$
CREATE DEFINER=`DBO`@`localhost`
FUNCTION mysql_user_exists(username CHAR(16)) RETURNS TINYINT(1)

LANGUAGE SQL
DETERMINISTIC
SQL SECURITY DEFINER
READS SQL DATA
COMMENT 'Returns true (1) if user exists in mysql.user'

BEGIN
DECLARE user_exists INT DEFAULT 0;
SELECT DISTINCT 1 FROM mysql.user WHERE user=username INTO user_exists;
RETURN user_exists;
END $$


-- Check MUM User exists (in mum.login_users)
DROP FUNCTION IF EXISTS mum_user_exists $$
CREATE DEFINER=`DBO`@`localhost`
FUNCTION mum_user_exists(username CHAR(16)) RETURNS TINYINT(1)

LANGUAGE SQL
DETERMINISTIC
SQL SECURITY DEFINER
READS SQL DATA
COMMENT 'Returns true (1) if user exists in mum.login_users'

BEGIN
DECLARE user_exists INT DEFAULT 0;
SELECT 1 FROM mum.login_users WHERE login_name=username INTO user_exists;
RETURN user_exists;
END $$

-- Check User exists in MySQL AND MUM.
DROP FUNCTION IF EXISTS user_exists $$
CREATE DEFINER=`DBO`@`localhost`
FUNCTION user_exists(username CHAR(16)) RETURNS TINYINT(1)

LANGUAGE SQL
DETERMINISTIC
SQL SECURITY DEFINER
READS SQL DATA
COMMENT 'Returns true (1) if user exists'

BEGIN
DECLARE user_exists_status INT DEFAULT 0;
SET @user_count = (SELECT SUM(mum_user_exists(username) + mysql_user_exists(username)));


IF @user_count = 2 THEN
    SET user_exists_status = 1;
ELSEIF @user_count = 1 THEN
    SET user_exists_status = 0;
ELSE
    SET user_exists_status = 0;
END IF;

RETURN user_exists_status;
END $$

-- Check MUM Hostname exists (in mum.login_hosts)
DROP FUNCTION IF EXISTS mum_host_exists $$
CREATE DEFINER=`DBO`@`localhost`
FUNCTION mum_host_exists(hostname VARCHAR(64)) RETURNS TINYINT(1)

LANGUAGE SQL
DETERMINISTIC
SQL SECURITY DEFINER
READS SQL DATA
COMMENT 'Returns true (1) if host exists in mum.login_hosts'

BEGIN
DECLARE host_exists INT DEFAULT 0;
SELECT 1 FROM mum.login_hosts WHERE login_hostname=hostname INTO host_exists;
RETURN host_exists;
END $$

-- Check MUM user lock status
DROP FUNCTION IF EXISTS mum_lock_status $$
CREATE DEFINER=`DBO`@`localhost`
FUNCTION mum_lock_status(username CHAR(16),
                        hostname VARCHAR(64)) RETURNS TINYINT(1)

LANGUAGE SQL
DETERMINISTIC
SQL SECURITY DEFINER
READS SQL DATA
COMMENT 'Returns the users login status'

BEGIN
DECLARE user_status INT DEFAULT 0;
SET @mysql_user = username;
SET @mysql_host = hostname;

SELECT 1 FROM login_status s
JOIN login_hosts h ON h.login_host_id=s.login_host_id
WHERE h.login_hostname=@mysql_host
AND s.login_name=@mysql_user
AND s.login_status IN ('ACCESS', 'LOCKED') INTO user_status;

RETURN user_status;

END $$

-- Check MUM user type
DROP FUNCTION IF EXISTS mum_user_type $$
CREATE DEFINER=`DBO`@`localhost`
FUNCTION mum_user_type(username CHAR(16)) RETURNS CHAR(3)

LANGUAGE SQL
DETERMINISTIC
SQL SECURITY DEFINER
READS SQL DATA
COMMENT 'Returns the users login type'

BEGIN
DECLARE user_type CHAR(3);
SELECT Type FROM mum.v_user_status WHERE Username=username INTO user_type;
RETURN user_type;
END $$

DELIMITER ;

DELIMITER ;
