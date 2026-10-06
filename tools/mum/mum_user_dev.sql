/DELIMITER $$

DROP PROCEDURE IF EXISTS mum_user_dev $$
CREATE DEFINER=`root`@`localhost`
PROCEDURE mum_user_dev(IN mum_username CHAR(16),
                        IN mum_hostname VARCHAR(64))

LANGUAGE SQL
NOT DETERMINISTIC
MODIFIES SQL DATA
SQL SECURITY DEFINER
COMMENT 'Create a DB user with default privileges and expiration time'

mum_dev_sp:BEGIN
DECLARE mum_login_type CHAR(3);

-- Check user Exists
IF user_exists(mum_username) != 1 THEN
    SELECT 'User not found';
    LEAVE mum_dev_sp;
END IF; 

-- Is this a DEV server?
IF mum_server_environment(mum_hostname) != 'DEV' THEN
    SELECT 'This is not dev environment!';
    LEAVE mum_dev_sp;
END IF;

-- Is this a DEV user?
IF mum_login_type != 'DEV' THEN
    Select 'This is not a DEV user!';
    LEAVE mum_dev_sp;
END IF;


-- OK, grant.
SELECT 'Granting permissions to users own DEV database.';
SET @mysql_user = mum_username;
SET @mysql_grant_dev = CONCAT("GRANT ALL PRIVILEGES ON ", @mysql_user, ".* TO ", @mysql_user, ";");
PREPARE dev_grant_statement FROM @mysql_grant_dev;
EXECUTE dev_grant_statement;

-- Create the database
SET @mum_create_db = CONCAT("CREATE DATABASE IF NOT EXISTS ", @mysql_user, ";");
PREPARE mum_create_db_statement FROM @mum_create_db;
EXECUTE mum_create_db_statement;

END $$

DELIMITER ;
