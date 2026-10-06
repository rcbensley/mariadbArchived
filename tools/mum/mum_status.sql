DELIMITER $$ 
DROP PROCEDURE IF EXISTS mum_status $$
CREATE PROCEDURE mum_status()
BEGIN
    SELECT * FROM mum.v_user_status;
END $$
DELIMITER ;
