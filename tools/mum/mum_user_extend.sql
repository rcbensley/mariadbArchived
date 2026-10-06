DELIMITER $$

DROP PROCEDURE IF EXISTS mum_user_extend $$
CREATE DEFINER=`DBO`@`localhost`
PROCEDURE mum_user_extend(
        IN mum_username CHAR(16),
        IN mum_expiry_hours INT(3))

LANGUAGE SQL
NOT DETERMINISTIC
MODIFIES SQL DATA
SQL SECURITY DEFINER
COMMENT 'Extend an existing users access, does not unlock.'

mum_extend_sp:BEGIN
SET @mysql_user = mum_username;
SET @mum_expiry = DATE_ADD(NOW(), INTERVAL mum_expiry_hours HOUR);

-- Check user exists
IF user_exists(mum_username) = 1 THEN
    SET @mysql_extend_user = CONCAT("UPDATE mum.login_users SET expiry_time='", @mum_expiry, "' WHERE login_name='", @mysql_user, "';");
ELSE
    SELECT CONCAT("User not found on ", @@hostname, " ", @@port);
    LEAVE mum_extend_sp;
END IF;

-- Extend
PREPARE extend_statement FROM @mysql_extend_user;
EXECUTE extend_statement;

-- Confirm
SELECT CONCAT('Access for ', login_name, ' extended to ', expiry_time)
    FROM login_users WHERE login_name = mum_username;

END $$

DELIMITER ;
