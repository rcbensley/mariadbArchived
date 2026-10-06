/*
    unlock a user from specified host.
*/



DELIMITER $$

DROP PROCEDURE IF EXISTS mum_user_unlock $$
CREATE DEFINER=`DBO`@`localhost`
PROCEDURE mum_user_unlock(IN mum_username CHAR(16),
                        IN mum_hostname VARCHAR(64))

LANGUAGE SQL
NOT DETERMINISTIC
MODIFIES SQL DATA
SQL SECURITY DEFINER
COMMENT 'Unlock a user on a specific host.'

mum_unlock_sp:BEGIN

DECLARE user_mysql_exists INT DEFAULT 0;
DECLARE user_mum_exists INT DEFAULT 0;
SET @mum_status = 'ACCESS';
SET @mysql_user = mum_username;
SET @mysql_host = mum_hostname;
SET @lock_status=(SELECT Status
		FROM v_user_status
		WHERE Username=@mysql_user
		AND Hostname=@mysql_host);

-- Check user exists
IF mysql_user_exists(@mysql_user) = 0 THEN
    SELECT 'User does not exist in mysql.user';
    LEAVE mum_unlock_sp;
END IF; 

IF mum_user_exists(@mysql_user) = 0 THEN
    SELECT 'User does not exist in mum.login_users';
    LEAVE mum_unlock_sp;
END IF; 

-- Check host exists
IF mum_host_exists(@mysql_host) = 0 THEN
    SELECT 'Hostname does not exist in mum.login_hosts';
    LEAVE mum_unlock_sp;
ELSE
    SET @mum_host_id = (SELECT login_host_id FROM mum.login_hosts WHERE login_hostname = mum_hostname);
END IF;

-- Check user not already unlocked
IF @lock_status = @mum_status THEN
    SELECT CONCAT("User locked on ", @mysql_host, " ", @@port);
    LEAVE mum_unlock_sp;
END IF;


-- OK, now unlock user.
IF mum_lock_status(@mysql_user, @mysql_host) = 1 THEN
    SET @mum_unlock_user = CONCAT("UPDATE mum.login_status SET login_status='", @mum_status, "' WHERE login_name='", @mysql_user, "' AND login_host_id=", @mum_host_id, ";");
    SELECT @mum_unlock_user;
    PREPARE unlock_statement FROM @mum_unlock_user;
    EXECUTE unlock_statement;
ELSE
    SET @mum_unlock_user = CONCAT("INSERT INTO mum.login_status VALUES ('", @mysql_user,"',", @mum_host_id, ",'", @mum_status, "');");
    PREPARE unlock_statement FROM @mum_unlock_user;
    EXECUTE unlock_statement;
END IF;


-- Check unlock applied
IF mum_lock_status(@mysql_user, @mysql_host) = 1 THEN
	SET @lock_status=(SELECT Status FROM v_user_status
		WHERE Username=@mysql_user AND Hostname=@mysql_host);

	IF @lock_status != @mum_status THEN
	    SELECT CONCAT('User unlock failed for ', @mysql_user, ' ON ', @mysql_host);
	ELSE
	    SELECT CONCAT('User unlock successful for ', @mysql_user, ' ON ', @mysql_host);
	END IF;
ELSE
	    SELECT CONCAT('User unlock failed for ', @mysql_user, ' ON ', @mysql_host);
END IF;

END $$

DELIMITER ;
