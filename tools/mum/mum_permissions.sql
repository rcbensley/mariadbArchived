DELIMITER $$

DROP PROCEDURE IF EXISTS mum_permissions $$
CREATE DEFINER=`root`@`localhost`
PROCEDURE mum_permissions( IN mum_username CHAR(16), IN mum_hostname CHAR(60) )

LANGUAGE SQL
MODIFIES SQL DATA
SQL SECURITY DEFINER
COMMENT 'Revoke and re-grant default permissions on a user.'

mum_grant_sp:BEGIN

DECLARE tempdb_grants TINYINT(1) DEFAULT 0;
DECLARE new_trigger TINYINT(1) DEFAULT 0;
DECLARE old_trigger TINYINT(1) DEFAULT 0;
SET @mysql_user = mum_username;
SET @mysql_host = mum_hostname;

-- Check privileges exist, remove accordingly.
SELECT 1
	FROM mysql.db
	WHERE User = @mysql_user
    AND Host = @mysql_host
	AND Db = 'tempdb'
	INTO tempdb_grants;

SELECT 1
	FROM mysql.procs_priv
	WHERE User = @mysql_user
    AND Host = @mysql_host
	AND Db = 'mum'
	AND Routine_name = 'login_trigger'
	AND Proc_priv = 'Execute'
	INTO new_trigger;

SELECT 1
	FROM mysql.procs_priv
	WHERE User = @mysql_user
    AND Host = @mysql_host
	AND Db = 'dba_repl'
	AND Routine_name = 'login_trigger'
	AND Proc_priv = 'Execute'
	INTO old_trigger;

IF tempdb_grants = 1 THEN
    SET @revoke_tempdb = CONCAT("REVOKE ALL PRIVILEGES ON tempdb.* FROM '", @mysql_user, "'@'", @mysql_host,"';");
    PREPARE revoke_tempdb_statement FROM @revoke_tempdb;
    EXECUTE revoke_tempdb_statement;
END IF;

IF new_trigger = 1 THEN
    SET @revoke_new = CONCAT("REVOKE EXECUTE ON PROCEDURE mum.login_trigger FROM '", @mysql_user, "'@'", @mysql_host,"';");
    PREPARE revoke_new_statement FROM @revoke_new;
    EXECUTE revoke_new_statement;
END IF;

IF old_trigger = 1 THEN
    SET @revoke_old = CONCAT("REVOKE EXECUTE ON PROCEDURE dba_repl.login_trigger FROM '", @mysql_user, "'@'", @mysql_host,"';");
    PREPARE revoke_old_statement FROM @revoke_old;
    EXECUTE revoke_old_statement;
END IF;

-- Grant privileges.
SET @grant_tempdb = CONCAT("GRANT SELECT, INSERT, UPDATE, DELETE, DROP, ALTER, INDEX, CREATE TEMPORARY TABLES ON tempdb.* TO ", @mysql_user, "@'", @mysql_host, "';");
SET @grant_login_trigger = CONCAT("GRANT EXECUTE ON PROCEDURE mum.login_trigger TO ", @mysql_user, "@'%';");

PREPARE grant_tempdb_statement FROM @grant_tempdb;
EXECUTE grant_tempdb_statement;

PREPARE grant_login_trigger_statement FROM @grant_login_trigger;
EXECUTE grant_login_trigger_statement;

END $$

DELIMITER ;
