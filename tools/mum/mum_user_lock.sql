/*
    Lock a user from specified host.
*/



DELIMITER $$

DROP PROCEDURE IF EXISTS mum_user_lock $$
CREATE DEFINER=`DBO`@`localhost`
PROCEDURE mum_user_lock(IN mum_username CHAR(16),
                        IN mum_hostname VARCHAR(64))

LANGUAGE SQL
NOT DETERMINISTIC
MODIFIES SQL DATA
SQL SECURITY DEFINER
COMMENT 'Lock a user on a specific host.'

mum_lock_sp:BEGIN

DECLARE user_mysql_exists INT DEFAULT 0;
DECLARE user_mum_exists INT DEFAULT 0;
SET @mum_status = 'LOCKED';
SET @mysql_user = mum_username;
SET @mysql_host = mum_hostname;
SET @lock_status=(SELECT Status
		FROM v_user_status
		WHERE Username=@mysql_user
		AND Hostname=@mysql_host);

-- Check user exists
IF mysql_user_exists(@mysql_user) = 0 THEN
    SELECT 'User does not exist in mysql.user';
    LEAVE mum_lock_sp;
END IF; 

IF mum_user_exists(@mysql_user) = 0 THEN
    SELECT 'User does not exist in mum.login_users';
    LEAVE mum_lock_sp;
END IF; 

-- Check host exists
IF mum_host_exists(@mysql_host) = 0 THEN
    SELECT 'Hostname does not exist in mum.login_hosts';
    LEAVE mum_lock_sp;
ELSE
    SET @mum_host_id = (SELECT login_host_id FROM mum.login_hosts WHERE login_hostname = mum_hostname);
END IF;

-- Check user not already locked
IF @lock_status = 'LOCKED' THEN
    SELECT CONCAT("User locked on ", @mysql_host, " ", @@port);
    LEAVE mum_lock_sp;
END IF;
	
-- OK, now lock user.
IF mum_lock_status(@mysql_user, @mysql_host) = 1 THEN
    SET @mum_lock_user = CONCAT("UPDATE mum.login_status SET login_status='", @mum_status, "' WHERE login_name='", @mysql_user, "' AND login_host_id=", @mum_host_id, ";");
    PREPARE lock_statement FROM @mum_lock_user;
    EXECUTE lock_statement;
ELSE
    SET @mum_lock_user = CONCAT("INSERT INTO mum.login_status VALUES ('", @mysql_user,"',", @mum_host_id, ",'", @mum_status, "');");
    PREPARE lock_statement FROM @mum_lock_user;
    EXECUTE lock_statement;
END IF;


-- Check lock applied
IF mum_lock_status(@mysql_user, @mysql_host) = 1 THEN
	SET @lock_status=(SELECT Status FROM v_user_status
		WHERE Username=@mysql_user AND Hostname=@mysql_host);

	IF @lock_status != 'LOCKED' THEN
	    SELECT CONCAT('User lock failed for ', @mysql_user, ' ON ', @mysql_host);
	ELSE
	    SELECT CONCAT('User lock successful for ', @mysql_user, ' ON ', @mysql_host);
	END IF;
ELSE
	    SELECT CONCAT('User lock failed for ', @mysql_user, ' ON ', @mysql_host);
END IF;

END $$

DELIMITER ;
