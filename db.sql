CREATE DATABASE mynode
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

CREATE USER `mynode`@`%` IDENTIFIED WITH 'mysql_native_password' AS 'password';

GRANT ALL PRIVILEGES ON `mynode`.* TO `mynode`@`%`

SET NAMES 'utf8';

USE mynode;

CREATE TABLE workers (
	id int UNSIGNED NOT NULL AUTO_INCREMENT,
	login varchar(50) NOT NULL DEFAULT (SUBSTR(MD5(RAND()), 1, 4)),
	password varchar(50) NOT NULL DEFAULT (SUBSTR(MD5(RAND()), 1, 6)),
	name varchar(50) DEFAULT NULL,
	description varchar(255) DEFAULT NULL,
	enabled tinyint(1) NOT NULL DEFAULT 0,
	active_dt datetime DEFAULT NULL,
	PRIMARY KEY (id)
)
ENGINE = INNODB;

CREATE TABLE files (
	id int NOT NULL AUTO_INCREMENT,
	name varchar(255) NOT NULL,
	parameters json DEFAULT NULL,
	processed tinyint DEFAULT 0,
	prompt text DEFAULT NULL,
	dt datetime DEFAULT CURRENT_TIMESTAMP,
	worker_id int DEFAULT NULL,
	PRIMARY KEY (id)
)
ENGINE = INNODB;

CREATE
DEFINER = 'mynode'@'%'
PROCEDURE get_next (IN arg_login varchar(50), IN arg_password varchar(50))
BEGIN
	DECLARE var_user_id int;
	DECLARE var_file_id int;

	SELECT
		w.id INTO var_user_id
	FROM workers w
	WHERE w.login = arg_login
	AND w.password = arg_password
	AND enabled = 1
	;

	START TRANSACTION;
		IF var_user_id IS NOT NULL THEN

			UPDATE workers w
			SET w.active_dt = CURRENT_TIMESTAMP()
			WHERE w.id = var_user_id;

			SELECT
				id INTO var_file_id
			FROM files f
			WHERE f.processed = 0
			LIMIT 1
			FOR UPDATE;

			IF var_file_id IS NOT NULL THEN
				UPDATE files f
				SET f.processed = 1
				WHERE f.id = var_file_id;

				SELECT
					'ok' AS result,
					f.*
				FROM files f
				WHERE f.id = var_file_id;
			ELSE
				SELECT
					'empty' AS result;
			END IF;

		ELSE
			DO SLEEP(5);
			SELECT
				'error' AS result,
				'user not found' AS message;
		END IF;

	COMMIT;

END
$$

DELIMITER ;
