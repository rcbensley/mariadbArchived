DELIMITER $$

DROP PROCEDURE IF EXISTS grant_access_to_login_trigger $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `grant_access_to_login_trigger`()
BEGIN
DECLARE v_sql_to_run VARCHAR(400);
DECLARE done INT DEFAULT 0;
DECLARE c CURSOR FOR select concat('grant execute on procedure mum.login_trigger to "',user,'"@"',host,'"') 
         from mysql.user;
DECLARE CONTINUE HANDLER FOR SQLSTATE '02000' SET done = 1;
OPEN c;
REPEAT
    FETCH c into v_sql_to_run;
    IF not done then
        select v_sql_to_run;
        set @stmt_text  = v_sql_to_run;
        PREPARE stmt FROM @stmt_text;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
UNTIL done END REPEAT;
END $$

DELIMITER ;
