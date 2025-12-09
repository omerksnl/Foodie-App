
CREATE DATABASE IF NOT EXISTS theapp;
USE theapp;

CREATE TABLE IF NOT EXISTS `User` (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(20) NOT NULL CHECK (CHAR_LENGTH(username) >= 2),
    password VARCHAR(100) NOT NULL CHECK (CHAR_LENGTH(password) >= 8),
    role ENUM('customer', 'manager') NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Address (
    address_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    type ENUM('home', 'work') NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(50) NOT NULL,
    town VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES `User`(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Phone (
    phone_number BIGINT PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES `User`(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Restaurant (
    restaurant_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    user_id INT,
    address TEXT NOT NULL,
    city VARCHAR(50) NOT NULL,
    town VARCHAR(50) NOT NULL,
    phone_num BIGINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES `User`(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS RestaurantTags (
    tag_id INT PRIMARY KEY AUTO_INCREMENT,
    restaurant_id INT,
    tag VARCHAR(50),
    FOREIGN KEY (restaurant_id) REFERENCES Restaurant(restaurant_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS MenuItem (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    restaurant_id INT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    cuisine_type VARCHAR(50),
    price DECIMAL(10,2) NOT NULL,
    image VARCHAR(255),
    discount DECIMAL(5,2),
    discount_end_time DATETIME,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurant(restaurant_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Cart (
    cart_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    restaurant_id INT,
    status ENUM('not bought yet','sent','accepted','preparing','delivering','delivered','cancelled') NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES `User`(user_id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurant(restaurant_id) ON DELETE CASCADE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS CartItem (
    cart_item_id INT PRIMARY KEY AUTO_INCREMENT,
    cart_id INT,
    item_id INT,
    note TEXT,
    quantity INT NOT NULL CHECK (quantity >= 1),
    FOREIGN KEY (cart_id) REFERENCES Cart(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES MenuItem(item_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Rating (
    rating_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    restaurant_id INT,
    item_id INT,
    rating_type ENUM('restaurant','item') NOT NULL,
    rating DECIMAL(2,1) NOT NULL CHECK (rating BETWEEN 0.5 AND 5.0),
    comment TEXT,
    FOREIGN KEY (user_id) REFERENCES `User`(user_id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurant(restaurant_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES MenuItem(item_id) ON DELETE SET NULL
) ENGINE=InnoDB;

DELIMITER //
CREATE TRIGGER rating_check BEFORE INSERT ON Rating
FOR EACH ROW
BEGIN
  IF (NEW.rating_type = 'item' AND NEW.item_id IS NULL)
     OR (NEW.rating_type = 'restaurant' AND NEW.item_id IS NOT NULL) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Invalid rating.';
  END IF;
END//
DELIMITER ;

CREATE OR REPLACE VIEW RestaurantRatings AS
SELECT
  r.restaurant_id,
  r.name,
  r.city,
  r.address,
  r.town,
  r.phone_num,
  COUNT(CASE WHEN rt.rating_type = 'restaurant' THEN 1 END) AS rating_count,
  ROUND(AVG(CASE WHEN rt.rating_type = 'restaurant' THEN rt.rating END), 1) AS avg_rating
FROM Restaurant r
LEFT JOIN Rating rt
  ON r.restaurant_id = rt.restaurant_id
GROUP BY
  r.restaurant_id,
  r.name,
  r.city,
  r.address,
  r.town,
  r.phone_num;

