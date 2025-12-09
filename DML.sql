-- Clears the database for testing purposes
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE Rating;
TRUNCATE TABLE CartItem;
TRUNCATE TABLE Cart;
TRUNCATE TABLE MenuItem;
TRUNCATE TABLE RestaurantTags;
TRUNCATE TABLE Restaurant;
TRUNCATE TABLE Address;
TRUNCATE TABLE Phone;
TRUNCATE TABLE User;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO User (username, password, role) VALUES
('oliviachef', 'SecurePass123!', 'manager'),
('marcusculinary', 'FoodLover456#', 'manager'),
('sophiakitchen', 'ChefMaster789@', 'manager'),
('danielgastro', 'GourmetPro432!', 'manager'),
('isabellafusion', 'CulinaryArts567#', 'manager');

INSERT INTO User (username, password, role) VALUES
('emmafoodie', 'TastyMeals321!', 'customer'),
('jamesgourmet', 'FlavorsRock567#', 'customer'),
('lilydelights', 'YummyFood890@', 'customer');

INSERT INTO Address (user_id, type, address, city, town) VALUES
((SELECT user_id FROM User WHERE username = 'emmafoodie'), 'home', '78 Maple Avenue', 'Istanbul', 'Besiktas'),
((SELECT user_id FROM User WHERE username = 'jamesgourmet'), 'home', '143 Pine Street', 'Istanbul', 'Sisli'),
((SELECT user_id FROM User WHERE username = 'lilydelights'), 'home', '25 Cedar Boulevard', 'Istanbul', 'Kadikoy');

INSERT INTO Restaurant (name, user_id, address, city, town, phone_num) VALUES
('Olive Garden', 
 (SELECT user_id FROM User WHERE username = 'oliviachef'), 
 'Istiklal Street 127', 'Istanbul', 'Beyoglu', 
 '5551234001'),
 
('Sapphire Bistro', 
 (SELECT user_id FROM User WHERE username = 'danielgastro'), 
 'Bagdat Avenue 302', 'Istanbul', 'Kadikoy', 
 '5551234002'),
 
('Rustic Table', 
 (SELECT user_id FROM User WHERE username = 'marcusculinary'), 
 'Alemdar Street 45', 'Istanbul', 'Sultanahmet', 
 '5551234003'),
 
('The Twisted Fork', 
 (SELECT user_id FROM User WHERE username = 'isabellafusion'), 
 'Siraselviler Street 112', 'Istanbul', 'Cihangir', 
 '5551234004'),
 
('Moonlight Cuisine', 
 (SELECT user_id FROM User WHERE username = 'sophiakitchen'), 
 'Caferaga Street 78', 'Istanbul', 'Kadikoy', 
 '5551234005');

INSERT INTO RestaurantTags (restaurant_id, tag) VALUES
((SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 'Mediterranean'),
((SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 'Italian'),
((SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 'Pasta'),
((SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 'Family-friendly'),

((SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 'French'),
((SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 'Fine Dining'),
((SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 'Seafood'),
((SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 'Romantic'),

((SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 'Farm-to-Table'),
((SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 'American'),
((SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 'Burgers'),
((SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 'Organic'),

((SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 'Fusion'),
((SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 'Asian-inspired'),
((SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 'Creative'),
((SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 'Tapas'),

((SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 'Turkish'),
((SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 'Mediterranean'),
((SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 'Meze'),
((SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 'Historical');

INSERT INTO MenuItem (restaurant_id, name, description, cuisine_type, price, discount, discount_end_time, image) VALUES
((SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 
 'Signature Lasagna', 
 'Layers of pasta, ricotta, parmesan, and our house-made meat sauce', 
 'Italian', 
 135.00, 
 15, 
 DATE_ADD(NOW(), INTERVAL 7 DAY),
 'lasagna.jpg'),
 
((SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 
 'Fettuccine Alfredo', 
 'Creamy alfredo sauce with garlic and fresh parmesan over fettuccine', 
 'Italian', 
 110.00, 
 NULL, 
 NULL,
 'fettuccine.jpg'),
 
((SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 
 'Mediterranean Salad', 
 'Fresh greens with olives, feta, cucumber, tomatoes and house dressing', 
 'Mediterranean', 
 70.00, 
 NULL, 
 NULL,
 'med_salad.jpg'),

((SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 
 'Coq au Vin', 
 'Traditional French chicken stew with red wine, mushrooms and pearl onions', 
 'French', 
 190.00, 
 NULL, 
 NULL,
 'coq_au_vin.jpg'),
 
((SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 
 'Lobster Thermidor', 
 'Lobster meat in a rich brandy cream sauce, gratinéed with cheese', 
 'French', 
 295.00, 
 10, 
 DATE_ADD(NOW(), INTERVAL 5 DAY),
 'lobster.jpg'),
 
((SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 
 'Crème Brûlée', 
 'Classic vanilla custard with caramelized sugar crust', 
 'French', 
 85.00, 
 NULL, 
 NULL,
 'creme_brulee.jpg'),

((SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 
 'Farm Burger', 
 'Grass-fed beef with aged cheddar, caramelized onions, and special sauce', 
 'American', 
 125.00, 
 NULL, 
 NULL,
 'farm_burger.jpg'),
 
((SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 
 'Harvest Bowl', 
 'Seasonal roasted vegetables, ancient grains, free-range chicken, and tahini dressing', 
 'Farm-to-Table', 
 110.00, 
 20, 
 DATE_ADD(NOW(), INTERVAL 10 DAY),
 'harvest_bowl.jpg'),
 
((SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 
 'Apple Pie', 
 'Organic apples, cinnamon, with a flaky butter crust and vanilla ice cream', 
 'American', 
 80.00, 
 NULL, 
 NULL,
 'apple_pie.jpg'),

((SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 
 'Korean BBQ Tacos', 
 'Marinated bulgogi beef, kimchi slaw, and gochujang aioli on corn tortillas', 
 'Fusion', 
 105.00, 
 NULL, 
 NULL,
 'korean_tacos.jpg'),
 
((SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 
 'Miso Glazed Salmon', 
 'Scottish salmon with miso glaze, wasabi mashed potatoes, and bok choy', 
 'Asian-inspired', 
 175.00, 
 15, 
 DATE_ADD(NOW(), INTERVAL 6 DAY),
 'miso_salmon.jpg'),
 
((SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 
 'Thai Basil Mojito', 
 'Refreshing cocktail with rum, lime, mint, Thai basil, and lemongrass syrup', 
 'Fusion', 
 65.00, 
 NULL, 
 NULL,
 'thai_mojito.jpg'),

((SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 
 'Sultan\'s Delight', 
 'Slow-cooked lamb on smoky eggplant puree with traditional spices', 
 'Turkish', 
 155.00, 
 NULL, 
 NULL,
 'sultans_delight.jpg'),
 
((SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 
 'Meze Platter', 
 'Selection of traditional appetizers including hummus, cacik, and stuffed grape leaves', 
 'Mediterranean', 
 120.00, 
 25, 
 DATE_ADD(NOW(), INTERVAL 4 DAY),
 'meze_platter.jpg'),
 
((SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 
 'Baklava', 
 'Layers of phyllo pastry with pistachios and honey syrup', 
 'Turkish', 
 60.00, 
 NULL, 
 NULL,
 'baklava.jpg');

-- Create Carts (10 total with items)
-- Cart 1: Delivered order for emmafoodie at Olive Garden
INSERT INTO Cart (user_id, restaurant_id, status, timestamp) VALUES
((SELECT user_id FROM User WHERE username = 'emmafoodie'),
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'),
 'delivered', DATE_SUB(NOW(), INTERVAL 20 DAY));

SET @cart1_id = LAST_INSERT_ID();

INSERT INTO CartItem (cart_id, item_id, quantity) VALUES
(@cart1_id, (SELECT item_id FROM MenuItem WHERE name = 'Signature Lasagna' LIMIT 1), 2),
(@cart1_id, (SELECT item_id FROM MenuItem WHERE name = 'Mediterranean Salad' LIMIT 1), 1);

-- Cart 2: Delivered order for jamesgourmet at Sapphire Bistro
INSERT INTO Cart (user_id, restaurant_id, status, timestamp) VALUES
((SELECT user_id FROM User WHERE username = 'jamesgourmet'),
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'),
 'delivered', DATE_SUB(NOW(), INTERVAL 15 DAY));

SET @cart2_id = LAST_INSERT_ID();

INSERT INTO CartItem (cart_id, item_id, quantity) VALUES
(@cart2_id, (SELECT item_id FROM MenuItem WHERE name = 'Lobster Thermidor' LIMIT 1), 1),
(@cart2_id, (SELECT item_id FROM MenuItem WHERE name = 'Crème Brûlée' LIMIT 1), 2);

-- Cart 3: Preparing order for lilydelights at Rustic Table
INSERT INTO Cart (user_id, restaurant_id, status, timestamp) VALUES
((SELECT user_id FROM User WHERE username = 'lilydelights'),
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'),
 'preparing', NOW());

SET @cart3_id = LAST_INSERT_ID();

INSERT INTO CartItem (cart_id, item_id, quantity) VALUES
(@cart3_id, (SELECT item_id FROM MenuItem WHERE name = 'Farm Burger' LIMIT 1), 2),
(@cart3_id, (SELECT item_id FROM MenuItem WHERE name = 'Harvest Bowl' LIMIT 1), 1);

-- Cart 4: Delivered order for emmafoodie at The Twisted Fork
INSERT INTO Cart (user_id, restaurant_id, status, timestamp) VALUES
((SELECT user_id FROM User WHERE username = 'emmafoodie'),
 (SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'),
 'delivered', DATE_SUB(NOW(), INTERVAL 10 DAY));

SET @cart4_id = LAST_INSERT_ID();

INSERT INTO CartItem (cart_id, item_id, quantity) VALUES
(@cart4_id, (SELECT item_id FROM MenuItem WHERE name = 'Korean BBQ Tacos' LIMIT 1), 3),
(@cart4_id, (SELECT item_id FROM MenuItem WHERE name = 'Thai Basil Mojito' LIMIT 1), 2);

-- Cart 5: Sent order for jamesgourmet at Moonlight Cuisine
INSERT INTO Cart (user_id, restaurant_id, status, timestamp) VALUES
((SELECT user_id FROM User WHERE username = 'jamesgourmet'),
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'),
 'sent', NOW());

SET @cart5_id = LAST_INSERT_ID();

INSERT INTO CartItem (cart_id, item_id, quantity) VALUES
(@cart5_id, (SELECT item_id FROM MenuItem WHERE name = 'Sultan\'s Delight' LIMIT 1), 1),
(@cart5_id, (SELECT item_id FROM MenuItem WHERE name = 'Meze Platter' LIMIT 1), 1);

INSERT INTO Cart (user_id, restaurant_id, status, timestamp) VALUES
((SELECT user_id FROM User WHERE username = 'emmafoodie'),
 (SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'),
 'delivered', DATE_SUB(NOW(), INTERVAL 7 DAY));

SET @cart6_id = LAST_INSERT_ID();

INSERT INTO CartItem (cart_id, item_id, quantity) VALUES
(@cart6_id, (SELECT item_id FROM MenuItem WHERE name = 'Miso Glazed Salmon' LIMIT 1), 2);

INSERT INTO Cart (user_id, restaurant_id, status, timestamp) VALUES
((SELECT user_id FROM User WHERE username = 'jamesgourmet'),
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'),
 'delivered', DATE_SUB(NOW(), INTERVAL 5 DAY));

SET @cart7_id = LAST_INSERT_ID();

INSERT INTO CartItem (cart_id, item_id, quantity) VALUES
(@cart7_id, (SELECT item_id FROM MenuItem WHERE name = 'Baklava' LIMIT 1), 4),
(@cart7_id, (SELECT item_id FROM MenuItem WHERE name = 'Sultan\'s Delight' LIMIT 1), 1);

INSERT INTO Cart (user_id, restaurant_id, status, timestamp) VALUES
((SELECT user_id FROM User WHERE username = 'lilydelights'),
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'),
 'delivered', DATE_SUB(NOW(), INTERVAL 3 DAY));

SET @cart8_id = LAST_INSERT_ID();

INSERT INTO CartItem (cart_id, item_id, quantity) VALUES
(@cart8_id, (SELECT item_id FROM MenuItem WHERE name = 'Fettuccine Alfredo' LIMIT 1), 1),
(@cart8_id, (SELECT item_id FROM MenuItem WHERE name = 'Mediterranean Salad' LIMIT 1), 2);

INSERT INTO Cart (user_id, restaurant_id, status, timestamp) VALUES
((SELECT user_id FROM User WHERE username = 'jamesgourmet'),
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'),
 'delivering', NOW());

SET @cart9_id = LAST_INSERT_ID();

INSERT INTO CartItem (cart_id, item_id, quantity) VALUES
(@cart9_id, (SELECT item_id FROM MenuItem WHERE name = 'Coq au Vin' LIMIT 1), 1),
(@cart9_id, (SELECT item_id FROM MenuItem WHERE name = 'Crème Brûlée' LIMIT 1), 1);

INSERT INTO Cart (user_id, restaurant_id, status, timestamp) VALUES
((SELECT user_id FROM User WHERE username = 'lilydelights'),
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'),
 'accepted', NOW());

SET @cart10_id = LAST_INSERT_ID();

INSERT INTO CartItem (cart_id, item_id, quantity) VALUES
(@cart10_id, (SELECT item_id FROM MenuItem WHERE name = 'Apple Pie' LIMIT 1), 2);

SET @sql = (SELECT IF(
    EXISTS(
        SELECT * FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'theapp' AND TABLE_NAME = 'Rating' AND COLUMN_NAME = 'timestamp'
    ),
    'SELECT 1',
    'ALTER TABLE Rating ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP'
));

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

INSERT INTO Rating (user_id, restaurant_id, rating_type, rating, comment, timestamp) VALUES
((SELECT user_id FROM User WHERE username = 'emmafoodie'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 
 'restaurant', 4.5, 
 'The lasagna was incredible - authentic Italian flavor and perfect portion size!',
 DATE_SUB(NOW(), INTERVAL 19 DAY)),
 
((SELECT user_id FROM User WHERE username = 'jamesgourmet'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 
 'restaurant', 5.0, 
 'Best pasta in town - the sauce is clearly homemade and the service was impeccable.',
 DATE_SUB(NOW(), INTERVAL 45 DAY)),
 
((SELECT user_id FROM User WHERE username = 'lilydelights'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 
 'restaurant', 4.0, 
 'Lovely ambiance and the Mediterranean salad was very fresh. Would definitely return!',
 DATE_SUB(NOW(), INTERVAL 2 DAY)),
 
((SELECT user_id FROM User WHERE username = 'oliviachef'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 
 'restaurant', 4.0, 
 'As a chef myself, I appreciate the attention to detail in their pasta dishes.',
 DATE_SUB(NOW(), INTERVAL 15 DAY)),
 
((SELECT user_id FROM User WHERE username = 'marcusculinary'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 
 'restaurant', 4.5, 
 'Excellent Italian offerings with good wine pairing suggestions from staff.',
 DATE_SUB(NOW(), INTERVAL 10 DAY)),
 
((SELECT user_id FROM User WHERE username = 'sophiakitchen'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 
 'restaurant', 4.0, 
 'Authentic Mediterranean flavors that reminded me of my travels to Italy.',
 DATE_SUB(NOW(), INTERVAL 25 DAY)),
 
((SELECT user_id FROM User WHERE username = 'danielgastro'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 
 'restaurant', 4.8, 
 'Some of the most authentic Italian food I\'ve had outside of Italy. Remarkable.',
 DATE_SUB(NOW(), INTERVAL 42 DAY)),
 
((SELECT user_id FROM User WHERE username = 'isabellafusion'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 
 'restaurant', 4.2, 
 'Great pasta dishes with well-balanced flavors. The bread service is exceptional.',
 DATE_SUB(NOW(), INTERVAL 33 DAY)),
 
((SELECT user_id FROM User WHERE username = 'emmafoodie'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 
 'restaurant', 5.0, 
 'My second visit was even better than the first! The fettuccine alfredo is to die for.',
 DATE_SUB(NOW(), INTERVAL 5 DAY)),
 
((SELECT user_id FROM User WHERE username = 'lilydelights'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Olive Garden'), 
 'restaurant', 4.5, 
 'Family-friendly with great options for kids, but still sophisticated enough for adults.',
 DATE_SUB(NOW(), INTERVAL 1 DAY));

INSERT INTO Rating (user_id, restaurant_id, rating_type, rating, comment, timestamp) VALUES
((SELECT user_id FROM User WHERE username = 'emmafoodie'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 
 'restaurant', 5.0, 
 'The Lobster Thermidor was divine - perfectly cooked with a delicate balance of flavors.',
 DATE_SUB(NOW(), INTERVAL 40 DAY)),
 
((SELECT user_id FROM User WHERE username = 'jamesgourmet'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 
 'restaurant', 4.5, 
 'Excellent French cuisine in an elegant setting. The wine selection is impressive!',
 DATE_SUB(NOW(), INTERVAL 14 DAY)),
 
((SELECT user_id FROM User WHERE username = 'lilydelights'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 
 'restaurant', 5.0, 
 'The Coq au Vin transported me straight to Paris. Absolutely magnificent.',
 DATE_SUB(NOW(), INTERVAL 35 DAY)),
 
((SELECT user_id FROM User WHERE username = 'oliviachef'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 
 'restaurant', 4.5, 
 'As a chef, I was impressed by their technique and presentation. Truly exceptional.',
 DATE_SUB(NOW(), INTERVAL 28 DAY)),
 
((SELECT user_id FROM User WHERE username = 'marcusculinary'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 
 'restaurant', 5.0, 
 'The seafood is incredibly fresh and prepared with expert French techniques.',
 DATE_SUB(NOW(), INTERVAL 42 DAY)),
 
((SELECT user_id FROM User WHERE username = 'sophiakitchen'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 
 'restaurant', 4.5, 
 'A true fine dining experience with spectacular attention to detail.',
 DATE_SUB(NOW(), INTERVAL 21 DAY)),
 
((SELECT user_id FROM User WHERE username = 'danielgastro'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 
 'restaurant', 4.7, 
 'Precise French cooking techniques executed flawlessly. The dessert menu is outstanding.',
 DATE_SUB(NOW(), INTERVAL 18 DAY)),
 
((SELECT user_id FROM User WHERE username = 'isabellafusion'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 
 'restaurant', 4.8, 
 'Every dish tells a story - elegant plating with focus on seasonal ingredients.',
 DATE_SUB(NOW(), INTERVAL 25 DAY)),
 
((SELECT user_id FROM User WHERE username = 'jamesgourmet'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 
 'restaurant', 4.0, 
 'My second visit confirmed that their consistency is remarkable. Always excellent.',
 DATE_SUB(NOW(), INTERVAL 7 DAY)),
 
((SELECT user_id FROM User WHERE username = 'emmafoodie'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Sapphire Bistro'), 
 'restaurant', 4.5, 
 'The romantic atmosphere and exquisite food make this place special.',
 DATE_SUB(NOW(), INTERVAL 2 DAY));

INSERT INTO Rating (user_id, restaurant_id, rating_type, rating, comment, timestamp) VALUES
((SELECT user_id FROM User WHERE username = 'emmafoodie'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 
 'restaurant', 4.5, 
 'Farm-to-table at its best! You can taste the freshness in every bite.',
 DATE_SUB(NOW(), INTERVAL 18 DAY)),
 
((SELECT user_id FROM User WHERE username = 'jamesgourmet'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 
 'restaurant', 4.0, 
 'The Farm Burger is honestly life-changing - perfectly cooked with quality ingredients.',
 DATE_SUB(NOW(), INTERVAL 38 DAY)),
 
((SELECT user_id FROM User WHERE username = 'lilydelights'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 
 'restaurant', 5.0, 
 'Love their commitment to organic and sustainable ingredients. And the food is delicious!',
 DATE_SUB(NOW(), INTERVAL 2 DAY)),
 
((SELECT user_id FROM User WHERE username = 'oliviachef'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 
 'restaurant', 4.0, 
 'As a chef, I appreciate their transparency about ingredient sourcing. Great flavors!',
 DATE_SUB(NOW(), INTERVAL 55 DAY)),
 
((SELECT user_id FROM User WHERE username = 'marcusculinary'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 
 'restaurant', 4.5, 
 'The rustic atmosphere perfectly complements the honest, flavorful food.',
 DATE_SUB(NOW(), INTERVAL 33 DAY)),
 
((SELECT user_id FROM User WHERE username = 'sophiakitchen'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 
 'restaurant', 5.0, 
 'Impressive attention to seasonal ingredients. Every dish celebrates what\'s fresh now.',
 DATE_SUB(NOW(), INTERVAL 49 DAY)),
 
((SELECT user_id FROM User WHERE username = 'danielgastro'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 
 'restaurant', 4.3, 
 'Their farm-to-table philosophy is evident in every aspect of the meal. Delicious.',
 DATE_SUB(NOW(), INTERVAL 22 DAY)),
 
((SELECT user_id FROM User WHERE username = 'isabellafusion'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 
 'restaurant', 4.6, 
 'The simplicity of the dishes highlights the quality of ingredients. Simply wonderful.',
 DATE_SUB(NOW(), INTERVAL 44 DAY)),
 
((SELECT user_id FROM User WHERE username = 'lilydelights'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 
 'restaurant', 4.0, 
 'The staff is knowledgeable about every ingredient and genuinely care about food quality.',
 DATE_SUB(NOW(), INTERVAL 1 DAY)),
 
((SELECT user_id FROM User WHERE username = 'jamesgourmet'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Rustic Table'), 
 'restaurant', 4.5, 
 'My go-to place for honest American cooking with an elevated twist.',
 DATE_SUB(NOW(), INTERVAL 9 DAY));

INSERT INTO Rating (user_id, restaurant_id, rating_type, rating, comment, timestamp) VALUES
((SELECT user_id FROM User WHERE username = 'emmafoodie'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 
 'restaurant', 5.0, 
 'The fusion dishes here are truly innovative! Korean BBQ Tacos were a flavor explosion.',
 DATE_SUB(NOW(), INTERVAL 6 DAY)),
 
((SELECT user_id FROM User WHERE username = 'jamesgourmet'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 
 'restaurant', 4.5, 
 'Creative combinations that somehow work perfectly together. Great culinary adventure!',
 DATE_SUB(NOW(), INTERVAL 44 DAY)),
 
((SELECT user_id FROM User WHERE username = 'lilydelights'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 
 'restaurant', 4.0, 
 'Unique fusion concept executed with real culinary skill. The Thai Basil Mojito is amazing!',
 DATE_SUB(NOW(), INTERVAL 30 DAY)),
 
((SELECT user_id FROM User WHERE username = 'oliviachef'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 
 'restaurant', 5.0, 
 'As a chef, I\'m blown away by their creativity and technical skill. Breaking boundaries!',
 DATE_SUB(NOW(), INTERVAL 17 DAY)),
 
((SELECT user_id FROM User WHERE username = 'marcusculinary'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 
 'restaurant', 4.5, 
 'Bold flavors, beautiful plating, and truly innovative combinations. Impressive!',
 DATE_SUB(NOW(), INTERVAL 25 DAY)),
 
((SELECT user_id FROM User WHERE username = 'sophiakitchen'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 
 'restaurant', 4.0, 
 'The tapas-style small plates are perfect for trying many different fusion creations.',
 DATE_SUB(NOW(), INTERVAL 36 DAY)),
 
((SELECT user_id FROM User WHERE username = 'danielgastro'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 
 'restaurant', 4.8, 
 'Their willingness to experiment with flavors results in truly memorable dishes.',
 DATE_SUB(NOW(), INTERVAL 29 DAY)),
 
((SELECT user_id FROM User WHERE username = 'isabellafusion'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 
 'restaurant', 5.0, 
 'Being a fusion chef myself, I\'m inspired by their creative combinations of cuisines.',
 DATE_SUB(NOW(), INTERVAL 19 DAY)),
 
((SELECT user_id FROM User WHERE username = 'emmafoodie'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 
 'restaurant', 5.0, 
 'My second visit was even better than the first! The menu keeps evolving with new ideas.',
 DATE_SUB(NOW(), INTERVAL 5 DAY)),
 
((SELECT user_id FROM User WHERE username = 'jamesgourmet'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'The Twisted Fork'), 
 'restaurant', 4.5, 
 'The cocktails are just as creative as the food - perfect flavor pairings!',
 DATE_SUB(NOW(), INTERVAL 2 DAY));

INSERT INTO Rating (user_id, restaurant_id, rating_type, rating, comment, timestamp) VALUES
((SELECT user_id FROM User WHERE username = 'emmafoodie'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 
 'restaurant', 4.5, 
 'Authentic Turkish flavors in a beautiful setting. The Sultan\'s Delight is exceptional!',
 DATE_SUB(NOW(), INTERVAL 32 DAY)),
 
((SELECT user_id FROM User WHERE username = 'jamesgourmet'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 
 'restaurant', 5.0, 
 'The best baklava I\'ve had outside of Turkey! Perfect sweetness and texture.',
 DATE_SUB(NOW(), INTERVAL 4 DAY)),
 
((SELECT user_id FROM User WHERE username = 'lilydelights'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 
 'restaurant', 4.5, 
 'The meze platter offers an incredible variety of flavors - perfect for sharing!',
 DATE_SUB(NOW(), INTERVAL 23 DAY)),
 
((SELECT user_id FROM User WHERE username = 'oliviachef'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 
 'restaurant', 4.5, 
 'As a chef, I\'m impressed by their mastery of traditional techniques. Authentic taste!',
 DATE_SUB(NOW(), INTERVAL 39 DAY)),
 
((SELECT user_id FROM User WHERE username = 'marcusculinary'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 
 'restaurant', 4.0, 
 'The spice combinations are complex and beautiful - a true taste of Turkish tradition.',
 DATE_SUB(NOW(), INTERVAL 28 DAY)),
 
((SELECT user_id FROM User WHERE username = 'sophiakitchen'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 
 'restaurant', 5.0, 
 'The atmosphere makes you feel like you\'re dining in a historic Istanbul villa. Magical!',
 DATE_SUB(NOW(), INTERVAL 15 DAY)),
 
((SELECT user_id FROM User WHERE username = 'danielgastro'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 
 'restaurant', 4.7, 
 'Rich, complex flavors that speak to centuries of culinary tradition. Transported me to Istanbul.',
 DATE_SUB(NOW(), INTERVAL 11 DAY)),
 
((SELECT user_id FROM User WHERE username = 'isabellafusion'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 
 'restaurant', 4.3, 
 'Their lamb dishes are some of the best I\'ve ever had - tender and perfectly seasoned.',
 DATE_SUB(NOW(), INTERVAL 37 DAY)),
 
((SELECT user_id FROM User WHERE username = 'jamesgourmet'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 
 'restaurant', 4.5, 
 'Each visit brings new delights - the seasonal specials are always worth trying!',
 DATE_SUB(NOW(), INTERVAL 3 DAY)),
 
((SELECT user_id FROM User WHERE username = 'emmafoodie'), 
 (SELECT restaurant_id FROM Restaurant WHERE name = 'Moonlight Cuisine'), 
 'restaurant', 5.0, 
 'The traditional Turkish coffee service at the end of the meal is a perfect finish.',
 DATE_SUB(NOW(), INTERVAL 1 DAY)); 