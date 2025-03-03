-- Create Database
CREATE DATABASE IF NOT EXISTS linkedin_db;
USE linkedin_db;

-- Table: Users
CREATE TABLE IF NOT EXISTS Users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    profile_image VARCHAR(255),
    active BOOLEAN DEFAULT TRUE,
    deleted BOOLEAN DEFAULT FALSE,
    deleted_by_guid BIGINT DEFAULT NULL,
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table: User_Posts
CREATE TABLE IF NOT EXISTS User_Posts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    media_url VARCHAR(255),
    visibility ENUM('PUBLIC', 'CONNECTIONS', 'PRIVATE') DEFAULT 'PUBLIC',
    active BOOLEAN DEFAULT TRUE,
    deleted BOOLEAN DEFAULT FALSE,
    deleted_by_guid BIGINT DEFAULT NULL,
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Table: Post_Likes
CREATE TABLE IF NOT EXISTS Post_Likes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    post_id BIGINT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    deleted BOOLEAN DEFAULT FALSE,
    deleted_by_guid BIGINT DEFAULT NULL,
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE(user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES User_Posts(id) ON DELETE CASCADE
);

-- Table: Post_Comments
CREATE TABLE IF NOT EXISTS Post_Comments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    post_id BIGINT NOT NULL,
    comment_text TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    deleted BOOLEAN DEFAULT FALSE,
    deleted_by_guid BIGINT DEFAULT NULL,
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES User_Posts(id) ON DELETE CASCADE
);

-- Insert Dummy Users
INSERT INTO Users (full_name, email, profile_image) VALUES
('John Doe', 'john.doe@example.com', 'john_profile.jpg'),
('Jane Smith', 'jane.smith@example.com', 'jane_profile.jpg'),
('Alice Johnson', 'alice.johnson@example.com', 'alice_profile.jpg');

-- Insert Dummy User Posts
INSERT INTO User_Posts (user_id, content, media_url, visibility) VALUES
(1, 'Excited to start my new job at TechCorp!', 'post1.jpg', 'PUBLIC'),
(2, 'Just attended an amazing AI conference!', 'post2.jpg', 'CONNECTIONS'),
(3, 'My latest blog post on cloud computing is live!', NULL, 'PUBLIC');

-- Insert Dummy Post Likes
INSERT INTO Post_Likes (user_id, post_id) VALUES
(1, 2),  -- John likes Jane's post
(2, 3),  -- Jane likes Alice's post
(3, 1);  -- Alice likes John's post

-- Insert Dummy Post Comments
INSERT INTO Post_Comments (user_id, post_id, comment_text) VALUES
(2, 1, 'Congratulations, John! Best of luck!'),
(3, 2, 'AI conferences are always insightful. What was your biggest takeaway?'),
(1, 3, 'Great article on cloud computing, Alice!');

ALTER TABLE Users MODIFY COLUMN deleted_at BIGINT;


