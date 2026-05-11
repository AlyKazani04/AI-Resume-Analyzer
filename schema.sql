CREATE DATABASE IF NOT EXISTS resume_analyzer;
USE resume_analyzer;

-- 1. Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    last_login_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Resumes Table (Hashed for Deduplication)
CREATE TABLE resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    content LONGTEXT NOT NULL,
    content_hash CHAR(64) NOT NULL, -- SHA-256 Fingerprint
    file_type ENUM('pdf', 'docx') NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevents the same user from duplicating the same file content
    UNIQUE KEY unq_user_resume_content (user_id, content_hash),
    CONSTRAINT fk_resumes_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Job Descriptions Table (Now linked to Users + Hashed)
CREATE TABLE job_descriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content LONGTEXT NOT NULL,
    content_hash CHAR(64) NOT NULL, -- SHA-256 Fingerprint
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY unq_user_jd_content (user_id, content_hash),
    CONSTRAINT fk_jd_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Analysis Sessions Table (add llm_score)
CREATE TABLE analysis_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    resume_id INT NOT NULL,
    jd_id INT NOT NULL,
    similarity_score DECIMAL(5,2) NOT NULL,
    llm_score DECIMAL(5,2) NOT NULL,
    gap_report LONGTEXT NOT NULL,
    missing_keywords JSON NULL,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_sessions_resume FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE,
    CONSTRAINT fk_sessions_jd FOREIGN KEY (jd_id) REFERENCES job_descriptions(id) ON DELETE CASCADE,
    CONSTRAINT chk_similarity_score CHECK (similarity_score BETWEEN 0 AND 100),
    CONSTRAINT chk_llm_score CHECK (llm_score BETWEEN 0 AND 100)
);

-- 5. Performance Indexes
CREATE INDEX idx_resumes_history ON resumes (user_id, uploaded_at DESC);
CREATE INDEX idx_sessions_history ON analysis_sessions (user_id, analyzed_at DESC);
CREATE INDEX idx_sessions_resume_lookup ON analysis_sessions (resume_id);
CREATE INDEX idx_sessions_jd_lookup ON analysis_sessions (jd_id);

-- use resume_analyzer;
-- select * from analysis_sessions;
