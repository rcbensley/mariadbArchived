DELIMITER $$

DROP PROCEDURE IF EXISTS mum_user_expire $$
CREATE DEFINER=`DBO`@`localhost`
PROCEDURE mum_user_expire(IN mum_username CHAR(16))

LANGUAGE SQL
NOT DETERMINISTIC
MODIFIES SQL DATA
SQL SECURITY DEFINER
COMMENT 'Expire an existing users access'

mum_expire_sp:BEGIN
SET @mysql_user = mum_username;
SET @mum_expiry = DATE_SUB(NOW(), INTERVAL 1 MINUTE);

-- Check user exists
IF user_exists(mum_username) = 1 THEN
    SET @mysql_expire_user = CONCAT("UPDATE mum.login_users SET expiry_time='", @mum_expiry, "' WHERE login_name='", @mysql_user, "';");
ELSE
    SELECT CONCAT("User not found on ", @@hostname, " ", @@port);
    LEAVE mum_expire_sp;
END IF;

-- Set Expiry
PREPARE expire_statement FROM @mysql_expire_user;
EXECUTE expire_statement;

-- Run Audit to lock
CALL mum_expiry_audit();

-- Confirm
SELECT CONCAT('Expired user ', login_name)
    FROM login_users WHERE login_name = mum_username;

END $$

DELIMITER ;
