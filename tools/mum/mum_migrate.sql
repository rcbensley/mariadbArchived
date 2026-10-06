USE mum;

DELIMITER $$

DROP PROCEDURE IF EXISTS mum_migrate $$
CREATE DEFINER=`root`@`localhost`
PROCEDURE mum_migrate()
LANGUAGE SQL
NOT DETERMINISTIC
MODIFIES SQL DATA
SQL SECURITY DEFINER
COMMENT 'Copy existing mysql.user users into MUM'

mum_migrate_sp:BEGIN

DECLARE mum_username CHAR(16);
DECLARE mum_expiry_time INT DEFAULT 24;
DECLARE done INT DEFAULT FALSE;
DECLARE mum_cursor_usernames CURSOR FOR SELECT user FROM mysql.user WHERE CAST(user AS BINARY) RLIKE '[a-z0-9]'
    AND user NOT IN ('infobright', 'jabberserver', 'lynxdev', 'supportportal', 'enso', 'archive_loader', 'dba', 'root', 'nagios', 'pt', 'rep_user', 'monyog', 'monitoring', 'memagent', 'mycheckpoint', 'backup_user', 'cactiuser', 'clubber')
    AND user NOT LIKE '%MrT%' AND user NOT LIKE '%LYNX%' GROUP BY user;
DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

IF mum_server_environment(@@hostname) = 'DEV' THEN
    SET mum_expiry_time = 876000; -- 100 years!
END IF;

OPEN mum_cursor_usernames;

mum_cursor_usernames_loop: LOOP
    FETCH mum_cursor_usernames INTO mum_username;
    IF done THEN
        LEAVE mum_cursor_usernames_loop;
    END IF;

    -- Adding user that already exists in mysql.user, we can skip the password.
    CALL mum_user_add(mum_username, 'NONE', 'DEV', mum_expiry_time);

    SET @current_status = (SELECT login_status FROM dba_no_repl.login_status WHERE
                            login_name = mum_username);

    IF @current_status = 'locked' THEN
        CALL mum_user_lockdown(mum_username);
    ELSE
        CALL mum_user_prisonbreak(mum_username);
    END IF;

END LOOP;

CLOSE mum_cursor_usernames;

END $$

DELIMITER ;

