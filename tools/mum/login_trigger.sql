USE mum;

DELIMITER $$

DROP PROCEDURE IF EXISTS login_trigger $$
CREATE DEFINER=`root`@`localhost` PROCEDURE login_trigger()

LANGUAGE SQL
READS SQL DATA
SQL SECURITY DEFINER

login_sp:BEGIN
DECLARE lock_status INT DEFAULT 0;
DECLARE mum_username VARCHAR(20);
DECLARE process_id INT;
DECLARE mum_now DATETIME;
SET mum_now = NOW();

SELECT SUBSTRING_INDEX(USER(),'@',1) INTO mum_username;
SELECT CONNECTION_ID() INTO process_id;

SELECT 1 FROM mum.v_user_status
    WHERE Username = mum_username
    AND Hostname = @@hostname
    AND Type = 'DEV'
    AND Status = 'LOCKED'
    INTO lock_status;

IF lock_status = 1 THEN
    KILL process_id;
END IF;

END $$

DELIMITER ;

