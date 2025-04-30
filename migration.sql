-- Ajout des nouveaux champs à la table users
ALTER TABLE users
ADD COLUMN phone VARCHAR(20) NULL,
ADD COLUMN city VARCHAR(100) NULL,
ADD COLUMN subscription_date DATETIME NULL;

-- Ajout des nouveaux champs à la table tests
ALTER TABLE tests
ADD COLUMN is_free BOOLEAN DEFAULT FALSE,
ADD COLUMN test_type VARCHAR(20) DEFAULT 'qcm';

-- Ajout des nouveaux champs à la table user_answers
ALTER TABLE user_answers
ADD COLUMN writing_score FLOAT NULL,
ADD COLUMN is_evaluated BOOLEAN DEFAULT FALSE;

-- Création de la table writing_performance_levels
CREATE TABLE writing_performance_levels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    criteria_id INT NOT NULL,
    level VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    points INT NOT NULL,
    FOREIGN KEY (criteria_id) REFERENCES writing_criteria(id)
);

-- Création de la table writing_evaluations
CREATE TABLE writing_evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_answer_id INT NOT NULL,
    criteria_id INT NOT NULL,
    score INT NOT NULL,
    comment TEXT,
    FOREIGN KEY (user_answer_id) REFERENCES user_answers(id),
    FOREIGN KEY (criteria_id) REFERENCES writing_criteria(id)
); 