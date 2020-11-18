SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

CREATE TABLE `account` (
  `ts` timestamp NOT NULL DEFAULT current_timestamp(),
  `username` varchar(16) NOT NULL,
  `level` int(11) UNSIGNED NOT NULL DEFAULT 0,
  `total_exp` int(11) UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `counter` (
  `ts` timestamp NOT NULL DEFAULT current_timestamp(),
  `name` varchar(16) NOT NULL,
  `counter` mediumint(8) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `raid` (
  `ts` timestamp NOT NULL DEFAULT current_timestamp(),
  `total` mediumint(8) UNSIGNED NOT NULL DEFAULT 0,
  `level1` mediumint(8) UNSIGNED NOT NULL DEFAULT 0,
  `level2` mediumint(8) UNSIGNED NOT NULL DEFAULT 0,
  `level3` mediumint(8) UNSIGNED NOT NULL DEFAULT 0,
  `level4` mediumint(8) UNSIGNED NOT NULL DEFAULT 0,
  `level5` mediumint(8) UNSIGNED NOT NULL DEFAULT 0,
  `level6` mediumint(8) UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `account` ADD KEY `ts_ix` (`ts`) USING BTREE;
ALTER TABLE `counter` ADD UNIQUE KEY `ts_name_ix` (`ts`,`name`) USING BTREE;
ALTER TABLE `raid` ADD UNIQUE KEY `ts_ix` (`ts`);
COMMIT;
