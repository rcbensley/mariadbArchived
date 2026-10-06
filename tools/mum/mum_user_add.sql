/*
    create user with basic grants and defaults and expiration time.
*/

DELIMITER $$

DROP PROCEDURE IF EXISTS mum_user_add $$
CREATE DEFINER=`root`@`localhost`
PROCEDURE mum_user_add(
        IN mum_username CHAR(16), -- login_status.login_name
        IN mum_password VARCHAR(16),
        IN mum_login_type CHAR(3), -- login_status.login_type
        IN mum_expiry_hours INT(3))

LANGUAGE SQL
NOT DETERMINISTIC
MODIFIES SQL DATA
SQL SECURITY DEFINER
COMMENT 'Create a DB user with default privileges and expiration time'

mum_add_sp:BEGIN

DECLARE mum_expiry DATETIME;
DECLARE mysql_user_exists TINYINT(1) DEFAULT 0;
DECLARE mum_hostname CHAR(60) DEFAULT '%';
SET @mysql_host = mum_hostname;
SET @mum_now = NOW();
SET mum_expiry = DATE_ADD(@mum_now, INTERVAL mum_expiry_hours HOUR);

-- Check user does NOT already exist
IF mysql_user_exists(mum_username) = 1 THEN
    SET mysql_user_exists = 1;
END IF; 

IF mum_user_exists(mum_username) = 1 THEN
    LEAVE mum_add_sp;
END IF; 

-- Create Grant string
SET @mysql_user = mum_username;
SET @mysql_password = mum_password;

IF mysql_user_exists = 0 THEN
    SET @mysql_create_user = CONCAT("CREATE USER ", @mysql_user, "@'", @mysql_host,"' ", "IDENTIFIED BY '", @mysql_password, "';");
    PREPARE create_statement FROM @mysql_create_user;
    EXECUTE create_statement;
END IF;

-- Add user to MUM
SELECT mum_expiry;
INSERT INTO mum.login_users
    (login_name, login_type, created, updated, expiry_time)
    VALUES (mum_username, mum_login_type, @mum_now, @mum_now, mum_expiry);

-- Add Default permissions
CALL mum_permissions(@mysql_user, @mysql_host);

-- Is this a DEV server? Create and grant access to a database in their own name.
/* Not enabling this yet
IF mum_server_environment(@@hostname) || mum_login_type = 'DEV' THEN
    SELECT 'Adding premissions to user database ...';
    CALL mum_user_dev(@mysql_user, @@hostname);
    SELECT '... done!';
END IF;
*/

-- Check user was created
IF user_exists(mum_username) != 1 THEN
    SELECT 'User not added successfully, something went wrong. Rolling back ...';
    CALL mum_user_drop(@mysql_user);
    LEAVE mum_add_sp;
END IF; 

END $$

DELIMITER ;

