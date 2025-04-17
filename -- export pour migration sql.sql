-- export pour migration sql
-- MySQL version of the database schema
-- Converted from PostgreSQL

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Data for table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('7ced73358e01');

-- --------------------------------------------------------

--
-- Table structure for table `answers`
--

CREATE TABLE `answers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `question_id` int NOT NULL,
  `answer_text` longtext NOT NULL,
  `is_correct` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `answers_question_id_fkey` (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Data for table `answers`
--

INSERT INTO `answers` (`id`, `question_id`, `answer_text`, `is_correct`) VALUES
(1, 1, 'A) go ', 0),
(2, 1, 'B) goes ', 0),
(3, 1, 'C) going ', 1),
(4, 1, 'D) gone', 0),
(5, 2, ' A) am ', 0),
(6, 2, 'B) was ', 0),
(7, 2, 'C) were ', 1),
(8, 2, 'D) will be', 0),
(9, 3, ' A) don\'t ', 1),
(10, 3, 'B) like ', 0),
(11, 3, 'C) playing ', 0),
(12, 3, 'D) football', 0);

-- --------------------------------------------------------

--
-- Table structure for table `questions`
--

CREATE TABLE `questions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `test_id` int NOT NULL,
  `question_text` longtext NOT NULL,
  `question_type` varchar(50) NOT NULL,
  `points` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `questions_test_id_fkey` (`test_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Data for table `questions`
--

INSERT INTO `questions` (`id`, `test_id`, `question_text`, `question_type`, `points`) VALUES
(1, 1, 'Question : Complétez la phrase :\r\n\"She ______ to the park every morning.\"', 'qcm', 1),
(2, 1, 'Question : Choisissez la bonne réponse :\r\n\"If I ______ rich, I would travel the world.\"', 'qcm', 1),
(3, 1, 'Question : Identifiez l\'erreur :\r\n\"He don\'t like playing football.\"', 'qcm', 1);

-- --------------------------------------------------------

--
-- Table structure for table `scheduled_tests`
--

CREATE TABLE `scheduled_tests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `test_id` int NOT NULL,
  `scheduled_for` datetime NOT NULL,
  `completed` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `scheduled_tests_user_id_fkey` (`user_id`),
  KEY `scheduled_tests_test_id_fkey` (`test_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `test_results`
--

CREATE TABLE `test_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `test_id` int NOT NULL,
  `score` double NOT NULL,
  `level_achieved` varchar(10) DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `validated` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `test_results_user_id_fkey` (`user_id`),
  KEY `test_results_test_id_fkey` (`test_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Data for table `test_results`
--

INSERT INTO `test_results` (`id`, `user_id`, `test_id`, `score`, `level_achieved`, `completed_at`, `validated`) VALUES
(1, 2, 1, 66.66666666666666, 'A1', '2024-12-20 16:32:51', 1),
(2, 4, 1, 0, 'A1', '2024-12-28 18:44:12', 1),
(3, 5, 1, 33.33333333333333, 'A1', '2024-12-28 19:07:56', 1),
(4, 6, 1, 33.33333333333333, 'A1', '2025-01-07 17:23:08', 0),
(5, 6, 1, 33.33333333333333, 'A1', '2025-01-10 15:55:56', 0);

-- --------------------------------------------------------

--
-- Table structure for table `test_sessions`
--

CREATE TABLE `test_sessions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `test_id` int NOT NULL,
  `started_at` datetime NOT NULL,
  `completed_at` datetime DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `test_sessions_user_id_fkey` (`user_id`),
  KEY `test_sessions_test_id_fkey` (`test_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Data for table `test_sessions`
--

INSERT INTO `test_sessions` (`id`, `user_id`, `test_id`, `started_at`, `completed_at`, `status`) VALUES
(1, 4, 1, '2024-12-28 18:30:41', '2024-12-28 18:44:12', 'completed'),
(2, 4, 1, '2024-12-28 18:31:56', NULL, 'in_progress'),
(3, 4, 1, '2024-12-28 18:37:16', NULL, 'in_progress'),
(4, 4, 1, '2024-12-28 18:37:21', NULL, 'in_progress'),
(5, 4, 1, '2024-12-28 18:37:42', NULL, 'in_progress'),
(6, 4, 1, '2024-12-28 18:39:28', NULL, 'in_progress'),
(7, 4, 1, '2024-12-28 18:41:32', NULL, 'in_progress'),
(8, 4, 1, '2024-12-28 18:43:07', NULL, 'in_progress'),
(9, 4, 1, '2024-12-28 18:43:34', NULL, 'in_progress'),
(10, 5, 1, '2024-12-28 18:59:33', '2024-12-28 19:07:56', 'completed'),
(11, 5, 1, '2024-12-28 18:59:54', NULL, 'in_progress'),
(12, 5, 1, '2024-12-28 19:00:03', NULL, 'in_progress'),
(13, 5, 1, '2024-12-28 19:01:22', NULL, 'in_progress'),
(14, 5, 1, '2024-12-28 19:01:50', NULL, 'in_progress'),
(15, 5, 1, '2024-12-28 19:07:32', NULL, 'in_progress'),
(16, 6, 1, '2025-01-07 17:22:26', '2025-01-07 17:23:08', 'completed'),
(17, 6, 1, '2025-01-10 15:55:29', '2025-01-10 15:55:56', 'completed'),
(18, 6, 1, '2025-01-10 15:56:01', NULL, 'in_progress');

-- --------------------------------------------------------

--
-- Table structure for table `tests`
--

CREATE TABLE `tests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `level` varchar(10) NOT NULL,
  `description` longtext,
  `duration` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `user_role` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Data for table `tests`
--

INSERT INTO `tests` (`id`, `title`, `level`, `description`, `duration`, `created_at`, `is_active`, `user_role`) VALUES
(1, 'Test de niveau A1 Anglais', 'A1', 'test description', 60, '2024-12-20 15:14:20', 1, 'client');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(256) NOT NULL,
  `role` varchar(20) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `username` varchar(64) DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_email_key` (`email`),
  UNIQUE KEY `users_username_key` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Data for table `users`
--

INSERT INTO `users` (`id`, `email`, `password_hash`, `role`, `created_at`, `username`, `last_login`) VALUES
(1, 'admin@example.com', 'scrypt:32768:8:1$gLbNLpWR2CkbZeeW$4cb255d79dfdb14e4f970df6c014afcb5d930bd00a8e1b0323901a9e488fbd3e4560508116a663d5b37241106cf27d9a101a7cc7200ce40a80f2cda5993200f5', 'admin', '2024-12-20 15:11:59', 'admin', '2025-02-18 16:44:39'),
(2, 'Abouhanemehdi@gmail.com', 'scrypt:32768:8:1$oQOleUFDtNjwhYhM$1b25a388dd3a5d0daa65406ef88494af9d1ffa1b7711f71833a44ef46c02862b740244d3c760c1b52b3ca096749e6a85851c9873996fa1e80510be3c9c47ae16', 'admin', '2024-12-20 15:59:36', 'ABOUHANE MEDHI', '2025-01-10 15:54:50'),
(3, 'safaetalaa@gmail.com', 'scrypt:32768:8:1$3Xycbu0Mv0JpyNZK$56ed28249382b320e3cc73705435f13394a089c92342f767ea81d9832f8b63ac6b97a0b272c62e317613a8d48cc959062d9e8d9eb39c982fe8b7b42e26028316', 'client', '2024-12-20 16:00:13', 'Safae Talaa', '2025-01-07 17:21:16'),
(4, 'student1@test.com', 'scrypt:32768:8:1$KPl0TZa6iGFTUjNy$98bfe522b25e2dd08ed7dd08e6cd6215c6f0c674e4c0c50cb24fd770ffba4d3cd4d4f741439b5aee598ba29cc011b64ccf49da91b5a68f534ada164fe5def3c9', 'client', '2024-12-28 18:02:43', 'student1', '2024-12-28 18:03:02'),
(5, 'student2@test.com', 'scrypt:32768:8:1$c40qKZJQpTE8QIis$33ea869d74b39c53648dccbee302f52346f09f2bdfb247ef649a64b66567c16189666a1f1ef8b3df2389d3432888e34e0c44d91fad69d2e109fe389cd8bf22b4', 'client', '2024-12-28 18:59:07', 'student2', '2024-12-28 18:59:23'),
(6, 'Kawtar@gmail.com', 'scrypt:32768:8:1$vXHJtT1QcoF1Upy3$a008467109a5b68c645707e0f18838a9370fa3ca6fda4dae16e0bd071bd3ea38b9acb20b526ad4e26eaf39254bd781d3cd916b00d3f91a78431ea7e6fd45ed13', 'client', '2025-01-07 17:22:01', 'Kawtar', '2025-01-10 15:55:06');

-- --------------------------------------------------------

--
-- Add foreign key constraints
--

ALTER TABLE `answers`
  ADD CONSTRAINT `answers_question_id_fkey` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`);

ALTER TABLE `questions`
  ADD CONSTRAINT `questions_test_id_fkey` FOREIGN KEY (`test_id`) REFERENCES `tests` (`id`);

ALTER TABLE `scheduled_tests`
  ADD CONSTRAINT `scheduled_tests_test_id_fkey` FOREIGN KEY (`test_id`) REFERENCES `tests` (`id`),
  ADD CONSTRAINT `scheduled_tests_user_id_fkey` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `test_results`
  ADD CONSTRAINT `test_results_test_id_fkey` FOREIGN KEY (`test_id`) REFERENCES `tests` (`id`),
  ADD CONSTRAINT `test_results_user_id_fkey` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `test_sessions`
  ADD CONSTRAINT `test_sessions_test_id_fkey` FOREIGN KEY (`test_id`) REFERENCES `tests` (`id`),
  ADD CONSTRAINT `test_sessions_user_id_fkey` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);