DELIMITER $$

DROP PROCEDURE IF EXISTS mum_user_drop $$
CREATE DEFINER=`root`@`localhost`
PROCEDURE mum_user_drop(IN mum_username CHAR(16))

LANGUAGE SQL
NOT DETERMINISTIC
MODIFIES SQL DATA
SQL SECURITY DEFINER
COMMENT 'Delete and existing user from MySQL and MUM'

mum_drop_sp:BEGIN

SET @mysql_user = mum_username;

-- Check user exists
IF mysql_user_exists(mum_username) = 1 THEN
    SELECT 'User exists in mysql.user';
    SET @mysql_drop_user = CONCAT("DROP USER ", @mysql_user, ";");
    PREPARE drop_mysql_statement FROM @mysql_drop_user;
    EXECUTE drop_mysql_statement;
ELSE
    SELECT 'User does not exist in mysql.user';
END IF; 

IF mum_user_exists(mum_username) = 1 THEN
    SELECT 'User exists in mum.login_users';
    SET @mum_drop_user = CONCAT("DELETE FROM mum.login_users WHERE login_name='", @mysql_user, "';");
    PREPARE drop_mum_statement FROM @mum_drop_user;
    EXECUTE drop_mum_statement;
ELSE
    SELECT 'User not found in mum.login_users';
END IF; 

-- Confirm
IF user_exists(mum_username) = 0 THEN
    SELECT 'User dropped successfully';
ELSE
    SELECT 'Something went wrong, user not dropped properly?';
END IF;

END $$

DELIMITER ;
