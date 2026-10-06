DELIMITER $$

DROP PROCEDURE IF EXISTS mum_expiry_audit $$
CREATE DEFINER=`DBO`@`localhost`
PROCEDURE mum_expiry_audit()

LANGUAGE SQL
DETERMINISTIC
MODIFIES SQL DATA
SQL SECURITY DEFINER
COMMENT 'User expiry audit, updates the login_status value in login_users based on expiry_time'

mum_add_sp:BEGIN

DECLARE mum_now TIMESTAMP DEFAULT CURRENT_TIMESTAMP();

-- Lock Users
CREATE TEMPORARY TABLE mum.tt_lock
    (PRIMARY KEY (Username))
    SELECT Username
    FROM mum.v_user_status
    WHERE Status = 'ACCESS'
    AND Expires <= mum_now
    GROUP BY Username;

UPDATE mum.login_status SET login_status = 'LOCKED'
    WHERE login_name IN (select login_name FROM mum.tt_lock);

DROP TEMPORARY TABLE mum.tt_lock;

-- Unlock Users
CREATE TEMPORARY TABLE mum.tt_unlock
    (PRIMARY KEY (Username))
    SELECT Username
    FROM mum.v_user_status
    WHERE Status = 'LOCKED'
    AND Expires >= mum_now;

UPDATE mum.login_status SET login_status = 'ACCESS'
    WHERE login_name IN (select login_name FROM mum.tt_unlock);

END $$

DELIMITER ;
