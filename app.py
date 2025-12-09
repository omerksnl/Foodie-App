from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from datetime import datetime, timedelta
from flask import request, redirect, url_for, flash, session
from db import get_db
from flask import session, g  

app = Flask(__name__)
app.secret_key = 'dev-secret-key'



@app.context_processor
def inject_order_history_count():
    count = 0
    if session.get('role') == 'customer' and 'user_id' in session:
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT COUNT(*) AS cnt
            FROM Cart
            WHERE user_id = %s
              AND status <> 'not bought yet'
        """, (session['user_id'],))
        count = cur.fetchone()['cnt']
        cur.close()
        conn.close()

    return dict(order_history_count=count)


@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'manager':
            return redirect(url_for('manager_dashboard'))
        elif session['role'] == 'customer':
            return redirect(url_for('customer_home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM User WHERE username = %s AND role = %s', (username, user_type))
        user = cur.fetchone()
        cur.fetchall()
        cur.close()
        conn.close()

        if user and user['password'] == password:
            session['user_id'] = user['user_id']
            session['role'] = user_type
            session['name'] = user['username']
            
            return redirect(url_for('index'))

        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/customer/home')
def customer_home():
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))
    
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    
    try:

        popular_restaurants = get_popular_restaurants(limit=3)
        print(f"DEBUG: Retrieved {len(popular_restaurants)} popular restaurants for homepage")
        
      
        cur.execute("""
            SELECT r.*, u.username, 
                   COALESCE(rt.rating_count, 0) as rating_count, 
                   COALESCE(rt.avg_rating, 0) as avg_rating
            FROM Restaurant r
            JOIN User u ON r.user_id = u.user_id
            LEFT JOIN RestaurantRatings rt ON r.restaurant_id = rt.restaurant_id
            ORDER BY COALESCE(rt.avg_rating, 0) DESC, r.name ASC
            LIMIT 10
        """)
        all_restaurants = cur.fetchall()
        

        for restaurant in all_restaurants:
            if 'rating_count' not in restaurant or restaurant['rating_count'] is None:
                restaurant['rating_count'] = 0
            if 'avg_rating' not in restaurant or restaurant['avg_rating'] is None:
                restaurant['avg_rating'] = 0
        

        cur.execute("""
            SELECT c.cart_id, c.status, r.name as restaurant_name
            FROM Cart c
            JOIN Restaurant r ON c.restaurant_id = r.restaurant_id
            WHERE c.user_id = %s AND c.status = 'not bought yet'
            LIMIT 1
        """, (session['user_id'],))
        active_cart = cur.fetchone()
        

        cur.execute("""
            SELECT COUNT(*) as pending_count
            FROM Cart
            WHERE user_id = %s AND status IN ('sent', 'accepted', 'preparing', 'delivering')
        """, (session['user_id'],))
        pending_result = cur.fetchone()
        pending_orders = pending_result['pending_count'] if pending_result else 0
        
        return render_template('customer_home.html', 
                            restaurants=all_restaurants, 
                            popular_restaurants=popular_restaurants,
                            active_cart=active_cart,
                            pending_orders=pending_orders)
                            
    except Exception as e:
        print(f"Error in customer_home: {e}")
        import traceback
        traceback.print_exc()
        flash('An error occurred while loading the homepage')
        return render_template('customer_home.html', 
                             restaurants=[], 
                             popular_restaurants=[])
    finally:
        cur.close()
        conn.close()

@app.route('/search', methods=['GET'])
def search():
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))
    
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('customer_home'))
    
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    

    cur.execute("""
        SELECT city FROM Address 
        WHERE user_id = %s AND type = 'home' 
        LIMIT 1
    """, (session['user_id'],))
    customer_address = cur.fetchone()
    
    if not customer_address:
        flash('Please set your home address first')
        return redirect(url_for('customer_home'))
    

    cur.execute("""
        SELECT DISTINCT r.*, u.username, rt.rating_count, rt.avg_rating,
               GROUP_CONCAT(t.tag) as tags
        FROM Restaurant r
        JOIN User u ON r.user_id = u.user_id
        LEFT JOIN RestaurantTags t ON r.restaurant_id = t.restaurant_id
        LEFT JOIN RestaurantRatings rt ON r.restaurant_id = rt.restaurant_id
        WHERE r.city = %s 
        AND (r.name LIKE %s OR t.tag LIKE %s)
        GROUP BY r.restaurant_id
        ORDER BY 
            CASE 
                WHEN rt.rating_count >= 10 THEN rt.avg_rating 
                ELSE 0 
            END DESC,
            r.name ASC
    """, (customer_address['city'], f'%{query}%', f'%{query}%'))
    
    restaurants = cur.fetchall()
    

    for restaurant in restaurants:
        cur.execute("""
            SELECT * FROM MenuItem WHERE restaurant_id = %s
        """, (restaurant['restaurant_id'],))
        restaurant['menu_items'] = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('search_results.html', query=query, restaurants=restaurants)

@app.route('/restaurant/<int:restaurant_id>/menu')
def restaurant_menu(restaurant_id):
    """
    Displays the menu for a specific restaurant.
    - Shows restaurant information
    - Lists all menu items with details
    Requires customer authentication.
    """
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))
    
    conn = get_db(auto_commit=True)
    cur = conn.cursor(dictionary=True)
    

    cur.execute("""
        SELECT r.*, u.username
        FROM Restaurant r
        JOIN User u ON r.user_id = u.user_id
        WHERE r.restaurant_id = %s
    """, (restaurant_id,))
    restaurant = cur.fetchone()
    
    if not restaurant:
        flash('Restaurant not found')
        return redirect(url_for('customer_home'))
    

    try:

        cur.execute("SHOW COLUMNS FROM Rating LIKE 'timestamp'")
        has_timestamp = cur.fetchone() is not None
        print(f"DEBUG: Rating table has timestamp column: {has_timestamp}")
        

        cur.execute("SELECT COUNT(*) as total_ratings FROM Rating WHERE rating_type = 'restaurant'")
        total_db_ratings = cur.fetchone()['total_ratings']
        print(f"DEBUG: Total restaurant ratings in database: {total_db_ratings}")

        cur.execute("""
            SELECT COUNT(*) as rating_count, 
                   COALESCE(ROUND(AVG(rating), 1), 0) as avg_rating
            FROM Rating
            WHERE restaurant_id = %s AND rating_type = 'restaurant'
        """, (restaurant_id,))
        rating_data = cur.fetchone()
        print(f"DEBUG: Rating data for restaurant {restaurant_id}: {rating_data}")
        

        restaurant['rating_count'] = rating_data['rating_count'] if rating_data else 0
        restaurant['avg_rating'] = rating_data['avg_rating'] if rating_data and rating_data['rating_count'] > 0 else 0
        

        cur.execute("""
            SELECT GROUP_CONCAT(tag SEPARATOR ', ') as tags
            FROM RestaurantTags
            WHERE restaurant_id = %s
        """, (restaurant_id,))
        tags_data = cur.fetchone()
        restaurant['tags'] = tags_data['tags'] if tags_data and tags_data['tags'] else ''
        
        timestamp_select = ", r.timestamp" if has_timestamp else ""
        timestamp_order = "r.timestamp DESC" if has_timestamp else "r.rating_id DESC"
        
        query = f"""
            SELECT r.rating_id, r.rating, r.comment{timestamp_select}, u.username
            FROM Rating r
            JOIN User u ON r.user_id = u.user_id
            WHERE r.restaurant_id = %s AND r.rating_type = 'restaurant'
            ORDER BY {timestamp_order}
        """
        cur.execute(query, (restaurant_id,))
        restaurant_ratings = cur.fetchall()
        print(f"DEBUG: Found {len(restaurant_ratings)} ratings for restaurant {restaurant_id}")
        
    except Exception as e:
        print(f"Error fetching restaurant details: {e}")
        import traceback
        traceback.print_exc()
        restaurant['rating_count'] = 0
        restaurant['avg_rating'] = 0
        restaurant['tags'] = ''
        restaurant_ratings = []
    
 
    cur.execute("""
        SELECT * FROM MenuItem WHERE restaurant_id = %s ORDER BY name
    """, (restaurant_id,))
    menu_items = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('restaurant_menu.html', restaurant=restaurant, menu_items=menu_items, restaurant_ratings=restaurant_ratings)

@app.route('/cart', methods=['GET'])
def view_cart():
    """
    Displays the customer's active shopping cart.
    - Shows all items in the cart with details
    - Calculates total cost
    - Shows cart status
    Requires user authentication.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    print(f"DEBUG: User {session['user_id']} viewing cart")
    conn = get_db(auto_commit=True)  
    cur = conn.cursor(dictionary=True)
    
    try:

        cur.execute("""
            SELECT c.*, r.name as restaurant_name, r.restaurant_id
            FROM Cart c
            JOIN Restaurant r ON c.restaurant_id = r.restaurant_id
            WHERE c.user_id = %s AND c.status = 'not bought yet'
        """, (session['user_id'],))
        cart = cur.fetchone()
        
        if not cart:
            print(f"DEBUG: No active cart found for user {session['user_id']}")
            return render_template('cart.html', items=[], total=0)
        
        print(f"DEBUG: Found active cart #{cart['cart_id']} for user {session['user_id']}")
        

        cur.execute("""
            SELECT ci.*, m.name, m.price, m.description, m.image
            FROM CartItem ci
            JOIN MenuItem m ON ci.item_id = m.item_id
            WHERE ci.cart_id = %s
        """, (cart['cart_id'],))
        items = cur.fetchall()
        

        total = sum(item['price'] * item['quantity'] for item in items)
        print(f"DEBUG: Cart #{cart['cart_id']} has {len(items)} items, total: ${total}")
        
        return render_template('cart.html', items=items, total=total, cart=cart)
        
    except Exception as e:
        print(f"ERROR in view_cart: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading cart')
        return redirect(url_for('customer_home'))
        
    finally:
        cur.close()
        conn.close()

@app.route('/cart/add/<int:restaurant_id>/<int:item_id>', methods=['POST'])
def add_to_cart(restaurant_id, item_id):
    """
    Adds an item to the customer's shopping cart.
    - Creates a new cart if none exists
    - Adds the selected menu item with the specified quantity
    - Prevents adding items from different restaurants to the same cart
    - Updates quantity if the item is already in the cart
    Uses transaction handling to ensure consistency.
    Requires user authentication.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        quantity = int(request.form.get('quantity', 1))
        if quantity <= 0:
            flash('Quantity must be greater than zero', 'warning')
            return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    except ValueError:
        flash('Invalid quantity specified', 'warning')
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    
    print(f"DEBUG: User {session['user_id']} adding item {item_id} from restaurant {restaurant_id} to cart, quantity: {quantity}")
    
    conn = get_db(auto_commit=False)
    cur = conn.cursor(dictionary=True)
    
    try:

        cur.execute("SELECT * FROM MenuItem WHERE item_id = %s AND restaurant_id = %s", 
                   (item_id, restaurant_id))
        menu_item = cur.fetchone()
        if not menu_item:
            print(f"DEBUG: Menu item {item_id} not found in restaurant {restaurant_id}")
            flash('Menu item not found')
            return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
            
        cur.execute("""
            SELECT c.* FROM Cart c
            WHERE c.user_id = %s AND c.status = 'not bought yet'
        """, (session['user_id'],))
        cart = cur.fetchone()
        
        if not cart:
            print(f"DEBUG: Creating new cart for user {session['user_id']} at restaurant {restaurant_id}")
            cur.execute("""
                INSERT INTO Cart (user_id, restaurant_id, status)
                VALUES (%s, %s, 'not bought yet')
            """, (session['user_id'], restaurant_id))
            
            if cur.rowcount == 0:
                raise Exception("Failed to create new cart - no rows affected")
                
            cart_id = cur.lastrowid
            print(f"DEBUG: Created new cart #{cart_id} for user {session['user_id']}")
        else:
            cart_id = cart['cart_id']
            if cart['restaurant_id'] != restaurant_id:
                print(f"DEBUG: Cart conflict - existing cart is for restaurant {cart['restaurant_id']}, not {restaurant_id}")
                
               
                cur.execute("SELECT name FROM Restaurant WHERE restaurant_id = %s", (cart['restaurant_id'],))
                current_restaurant = cur.fetchone()
                current_restaurant_name = current_restaurant['name'] if current_restaurant else "another restaurant"
                
         
                cur.execute("SELECT name FROM Restaurant WHERE restaurant_id = %s", (restaurant_id,))
                new_restaurant = cur.fetchone()
                new_restaurant_name = new_restaurant['name'] if new_restaurant else "this restaurant"
                
              
                cur.close()
                conn.close()
                
               
                return jsonify({
                    'error': 'cart_conflict', 
                    'message': f'Cannot add items from different restaurants. You already have items from {current_restaurant_name} in your cart.',
                    'current_restaurant': current_restaurant_name,
                    'new_restaurant': new_restaurant_name
                }), 400
            
            print(f"DEBUG: Using existing cart #{cart_id}")
        
    
        print(f"DEBUG: Adding item {item_id} to cart #{cart_id}, quantity: {quantity}")
        cur.execute("""
            INSERT INTO CartItem (cart_id, item_id, quantity)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity = quantity + %s
        """, (cart_id, item_id, quantity, quantity))
        
        if cur.rowcount == 0:
            raise Exception("Failed to add item to cart - no rows affected")
        
        print(f"DEBUG: Item {item_id} successfully added to cart #{cart_id}")
        
     
        cur.execute("SELECT * FROM CartItem WHERE cart_id = %s AND item_id = %s", (cart_id, item_id))
        cart_item = cur.fetchone()
        if not cart_item:
            raise Exception("Item appears to be missing from cart after addition")
            
      
        conn.commit()
        print(f"DEBUG: Transaction committed successfully")
        
        flash(f'Added {quantity} x {menu_item["name"]} to your cart!')
        
    except Exception as e:
        conn.rollback()
        flash('Error adding item to cart')
        print(f"ERROR in add_to_cart: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('view_cart'))

@app.route('/cart/remove/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):

    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    print(f"DEBUG: Remove item {item_id} from cart for user {session['user_id']}")
    conn = get_db(auto_commit=False)
    cur = conn.cursor(dictionary=True)
    
    try:
        
        cur.execute("""
            SELECT c.cart_id, c.restaurant_id, r.name as restaurant_name
            FROM Cart c
            JOIN Restaurant r ON c.restaurant_id = r.restaurant_id
            WHERE c.user_id = %s AND c.status = 'not bought yet'
        """, (session['user_id'],))
        cart = cur.fetchone()
        
        if cart:
            cart_id = cart['cart_id']
            restaurant_name = cart['restaurant_name']
            
            print(f"DEBUG: Found cart #{cart_id} for restaurant {cart['restaurant_name']}")
            
           
            cur.execute("""
                DELETE FROM CartItem 
                WHERE cart_id = %s AND item_id = %s
            """, (cart_id, item_id))
            
           
            cur.execute("SELECT COUNT(*) as count FROM CartItem WHERE cart_id = %s", (cart_id,))
            result = cur.fetchone()
            
       
            if result['count'] == 0:
                cur.execute("DELETE FROM Cart WHERE cart_id = %s", (cart_id,))
                print(f"DEBUG: Cart #{cart_id} is now empty and has been deleted")
                flash(f'Your cart is now empty. You can order from any restaurant.', 'success')
            else:
                remaining_count = result['count']
                print(f"DEBUG: Cart #{cart_id} has {remaining_count} items remaining")
                flash(f'Item removed from cart. You have {remaining_count} item(s) remaining.', 'info')
            
            conn.commit()
        else:
            print("DEBUG: No active cart found")
            flash('No active cart found', 'warning')
            
    except Exception as e:
        conn.rollback()
        flash('Error removing item from cart', 'danger')
        print(f"ERROR in remove_from_cart: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    print(f"DEBUG: User {session['user_id']} entered checkout")
    

    conn = get_db(auto_commit=False)
    cur = conn.cursor(dictionary=True)
    
    try:
       
        cur.execute("""
            SELECT c.*, r.name as restaurant_name
            FROM Cart c
            JOIN Restaurant r ON c.restaurant_id = r.restaurant_id
            WHERE c.user_id = %s AND c.status = 'not bought yet'
        """, (session['user_id'],))
        cart = cur.fetchone()
        
        if not cart:
            print(f"DEBUG: No active cart found for user {session['user_id']}")
            flash('Your cart is empty')
            return redirect(url_for('customer_home'))

        print(f"DEBUG: Found active cart #{cart['cart_id']} for user {session['user_id']}")
        
        if request.method == 'POST':
            print(f"DEBUG: Processing checkout POST request for cart #{cart['cart_id']}")
            
        
            try:
               
                cur.execute("SELECT COUNT(*) as count FROM CartItem WHERE cart_id = %s", (cart['cart_id'],))
                item_count = cur.fetchone()['count']
                if item_count == 0:
                    print(f"DEBUG: Cart #{cart['cart_id']} has no items")
                    flash('Your cart is empty. Please add items before checkout.')
                    return redirect(url_for('view_cart'))
                    
                print(f"DEBUG: Cart #{cart['cart_id']} has {item_count} items")
                
               
                now =datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                update_sql = """
                    UPDATE Cart 
                    SET status = 'sent', timestamp = %s
                    WHERE cart_id = %s
                """
                print(f"DEBUG: Executing SQL: {update_sql} with params {now}, {cart['cart_id']}")
                
                cur.execute(update_sql, (now, cart['cart_id']))
                rows_affected = cur.rowcount
                print(f"DEBUG: Update affected {rows_affected} rows")
                
              
                cur.execute("SELECT status FROM Cart WHERE cart_id = %s", (cart['cart_id'],))
                updated = cur.fetchone()
                if not updated or updated['status'] != 'sent':
                    print(f"ERROR: Failed to update cart status. Current status: {updated['status'] if updated else 'None'}")
                    conn.rollback()
                    flash('Error processing your order. Please try again.')
                    return redirect(url_for('view_cart'))
                
              
                conn.commit()
                print(f"DEBUG: Transaction committed successfully. Cart #{cart['cart_id']} now has status '{updated['status']}'")
                
                flash('Order sent successfully! Waiting for restaurant confirmation.')
                return redirect(url_for('customer_home'))
                
            except Exception as e:
            
                conn.rollback()
                print(f"ERROR in checkout transaction: {e}")
                import traceback
                traceback.print_exc()
                flash('Error processing order. Please try again.')
                return redirect(url_for('view_cart'))
        
        cur.execute("""
            SELECT ci.*, m.name, m.price, m.description, m.image
            FROM CartItem ci
            JOIN MenuItem m ON ci.item_id = m.item_id
            WHERE ci.cart_id = %s
        """, (cart['cart_id'],))
        items = cur.fetchall()
        
        
        if not items:
            flash('Your cart is empty. Please add items before checking out.')
            return redirect(url_for('customer_home'))
        
        total = sum(item['price'] * item['quantity'] for item in items)
        
        return render_template('checkout.html', cart=cart, items=items, total=total)
    finally:
        
        cur.close()
        conn.close()


@app.route('/customer/orders')
def customer_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cur  = conn.cursor(dictionary=True)

    try:
 
        cur.execute("""
            SELECT c.cart_id, c.user_id, c.restaurant_id,
                   c.status,   c.timestamp,
                   r.name      AS restaurant_name,
                   r.address,  r.phone_num
            FROM Cart c
            JOIN Restaurant r ON c.restaurant_id = r.restaurant_id
            WHERE c.user_id = %s
              AND c.status <> 'not bought yet'
            ORDER BY c.timestamp DESC
        """, (session['user_id'],))
        orders = cur.fetchall()

        now = datetime.now()

      
        for order in orders:
       
            cur.execute("""
                SELECT ci.quantity,
                       m.name,
                       m.price,
                       m.description,
                       m.item_id
                FROM CartItem ci
                JOIN MenuItem m ON ci.item_id = m.item_id
                WHERE ci.cart_id = %s
            """, (order['cart_id'],))
            items = cur.fetchall()
            order['items'] = items
            order['total'] = sum(i['price'] * i['quantity'] for i in items)

           
            status = order['status']
            if   status == 'sent':        display, css = 'Sent - Waiting for confirmation', 'text-warning'
            elif status == 'accepted':    display, css = 'Accepted - Preparing',            'text-primary'
            elif status == 'preparing':   display, css = 'Being prepared',                  'text-info'
            elif status == 'delivering':  display, css = 'Out for delivery',                'text-info'
            elif status == 'delivered':   display, css = 'Delivered',                       'text-success'
            elif status == 'cancelled':   display, css = 'Cancelled',                       'text-danger'
            else:                         display, css = status.title(),                    'text-secondary'
            order['status_display'] = display
            order['status_class']   = css

        
            ts = order['timestamp']
            order['formatted_time'] = ts.strftime('%Y-%m-%d %H:%M') if ts else 'N/A'

        
            order['can_rate'] = (
                status == 'delivered' and ts and (now - ts) < timedelta(hours=24)
            )


         

       
        cur.execute("""
            SELECT c.cart_id, r.name AS restaurant_name
            FROM Cart c
            JOIN Restaurant r ON c.restaurant_id = r.restaurant_id
            WHERE c.user_id = %s
              AND c.status  = 'not bought yet'
            LIMIT 1
        """, (session['user_id'],))
        active_cart = cur.fetchone()

        cur.execute("""
            SELECT COUNT(*) AS cnt
            FROM Cart
            WHERE user_id = %s
              AND status IN ('sent','accepted','preparing','delivering')
        """, (session['user_id'],))
        pending_count = cur.fetchone()['cnt']

        return render_template(
            'customer_orders.html',
            orders=orders,
            active_cart=active_cart,
            pending_count=pending_count
        )

    except Exception as e:
        print(f"ERROR in customer_orders: {e}", flush=True)
        flash('An error occurred while loading your orders')
        return render_template(
            'customer_orders.html',
            orders=[], active_cart=None, pending_count=0
        )

    finally:
        cur.close()
        conn.close()

@app.route('/customer/order/<int:cart_id>/rate', methods=['POST'])
def rate_order(cart_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        rating = round(float(request.form.get('rating', '').replace(',', '.')), 1)
    except ValueError:
        flash('Geçerli bir puan girin')
        return redirect(url_for('customer_orders'))

    if not (0.5 <= rating <= 5.0):
        flash('Puan 0.5 ile 5.0 arasında olmalı')
        return redirect(url_for('customer_orders'))

    comment = request.form.get('comment', '').strip()

    conn = get_db()
    cur  = conn.cursor(dictionary=True)

    try:
       
        cur.execute("""
            SELECT restaurant_id, timestamp, status
            FROM Cart
            WHERE cart_id = %s
              AND user_id  = %s
        """, (cart_id, session['user_id']))
        cart = cur.fetchone()

        if not cart or cart['status'] != 'delivered':
            flash('Sipariş bulunamadı veya puanlanamaz')
            return redirect(url_for('customer_orders'))

       
        from datetime import datetime, timedelta
        now = datetime.now()
        if now - cart['timestamp'] > timedelta(hours=24):
            flash('Puanlama süresi doldu (24 saat)')
            return redirect(url_for('customer_orders'))

        rest_id = cart['restaurant_id']
        
        print(f"DEBUG: Adding/updating rating for restaurant {rest_id}, user {session['user_id']}, rating {rating}, comment '{comment}'")

        cur.execute("SHOW COLUMNS FROM Rating LIKE 'timestamp'")
        has_timestamp = cur.fetchone() is not None
        print(f"DEBUG: Rating table has timestamp column: {has_timestamp}")

        cur.execute("""
            SELECT rating_id
            FROM Rating
            WHERE user_id     = %s
              AND rating_type = 'restaurant'
              AND restaurant_id = %s
            LIMIT 1
        """, (session['user_id'], rest_id))
        row = cur.fetchone()

        if row:
           
            print(f"DEBUG: Updating existing rating {row['rating_id']}")
            if has_timestamp:
                cur.execute("""
                    UPDATE Rating
                    SET rating = %s,
                        comment = %s,
                        timestamp = %s
                    WHERE rating_id = %s
                """, (rating, comment, now, row['rating_id']))
            else:
                cur.execute("""
                    UPDATE Rating
                    SET rating = %s,
                        comment = %s
                    WHERE rating_id = %s
                """, (rating, comment, row['rating_id']))
        else:
            print(f"DEBUG: Inserting new rating")
            if has_timestamp:
                cur.execute("""
                    INSERT INTO Rating (user_id, restaurant_id,
                                      rating_type, rating, comment, timestamp)
                    VALUES (%s, %s, 'restaurant', %s, %s, %s)
                """, (session['user_id'], rest_id, rating, comment, now))
            else:
                cur.execute("""
                    INSERT INTO Rating (user_id, restaurant_id,
                                      rating_type, rating, comment)
                    VALUES (%s, %s, 'restaurant', %s, %s)
                """, (session['user_id'], rest_id, rating, comment))
            
       
        cur.execute("SHOW TABLES LIKE 'RestaurantRatings'")
        has_ratings_view = cur.fetchone() is not None
        print(f"DEBUG: Database has RestaurantRatings view: {has_ratings_view}")

        conn.commit()
        print(f"DEBUG: Rating saved successfully")
        flash('Puanınız kaydedildi, teşekkürler!')

    except Exception as e:
        conn.rollback()
        flash('Puan kaydedilirken hata oluştu')
        print('rate_order hatası →', e)
        import traceback
        traceback.print_exc()

    finally:
        cur.close()
        conn.close()

    return redirect(url_for('customer_orders'))


@app.route('/manager/orders')
def manager_orders():
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM Restaurant WHERE user_id = %s", (session['user_id'],))
        restaurant = cursor.fetchone()
        
        if not restaurant:
            cursor.close()
            conn.close()
            flash('Please create your restaurant first.')
            return redirect(url_for('manager_restaurant'))

        print(f"DEBUG: Manager {session['user_id']} looking for orders for restaurant {restaurant['restaurant_id']} (name: {restaurant['name']})")
        
        cursor.execute("""
            SELECT c.cart_id, c.status, u.username 
            FROM Cart c
            JOIN User u ON c.user_id = u.user_id
            WHERE c.restaurant_id = %s
        """, (restaurant['restaurant_id'],))
        
        debug_orders = cursor.fetchall()
        print(f"DEBUG: Found {len(debug_orders)} total orders for restaurant {restaurant['restaurant_id']} (all statuses):")
        for order in debug_orders:
            print(f"DEBUG: Cart #{order['cart_id']} - Status: {order['status']} - Customer: {order['username']}")
            
        cursor.execute("""
            SELECT c.*, u.username as customer_name 
            FROM Cart c
            JOIN User u ON c.user_id = u.user_id
            WHERE c.restaurant_id = %s 
            AND c.status != 'not bought yet'
            ORDER BY 
                CASE c.status
                    WHEN 'sent' THEN 1
                    WHEN 'accepted' THEN 2
                    WHEN 'preparing' THEN 3
                    WHEN 'delivering' THEN 4
                    WHEN 'delivered' THEN 5
                    WHEN 'cancelled' THEN 6
                    ELSE 7
                END,
                c.timestamp DESC
        """, (restaurant['restaurant_id'],))
        
        orders = cursor.fetchall()
        if not orders:
            orders = []
            
        print(f"DEBUG: Found {len(orders)} active orders for restaurant {restaurant['restaurant_id']} (excluding 'not bought yet')")
        
        for order in orders:
            print(f"DEBUG: Processing order {order['cart_id']}, status: {order['status']}")
            cursor.execute("""
                SELECT ci.*, m.name, m.price, m.description
                FROM CartItem ci
                JOIN MenuItem m ON ci.item_id = m.item_id
                WHERE ci.cart_id = %s
            """, (order['cart_id'],))
            
            order['order_items'] = cursor.fetchall() or []
            print(f"DEBUG: Order {order['cart_id']} has {len(order['order_items'])} items")
            
            order['total'] = sum(item['price'] * item['quantity'] for item in order['order_items'])

        cursor.close()
        conn.close()
        return render_template('manager_orders.html', restaurant=restaurant, orders=orders)

    except Exception as e:
        print(f"ERROR in manager_orders: {e}")
        import traceback
        traceback.print_exc()
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        flash('An error occurred while loading orders.')
        return redirect(url_for('manager_dashboard'))

@app.route('/manager/orders/update/<int:cart_id>', methods=['POST'])
def manager_update_order_status(cart_id):
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))

    new_status = request.form.get('status')
    if new_status not in ['accepted', 'preparing', 'delivering', 'delivered', 'cancelled']:
        flash('Invalid status')
        return redirect(url_for('manager_orders'))

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    
    try:
       
        conn.autocommit = False
        
        cur.execute("""
            SELECT c.cart_id, c.status, c.restaurant_id, r.name as restaurant_name
            FROM Cart c
            JOIN Restaurant r ON c.restaurant_id = r.restaurant_id
            WHERE c.cart_id = %s AND r.user_id = %s
        """, (cart_id, session['user_id']))
        
        cart = cur.fetchone()
        if not cart:
            flash('Order not found')
            return redirect(url_for('manager_orders'))
            
        current_status = cart['status']
        restaurant_id = cart['restaurant_id']
        
        print(f"DEBUG: Updating order {cart_id} status from '{current_status}' to '{new_status}'")
        
       
        valid_transitions = {
            'sent': ['accepted', 'cancelled'],
            'accepted': ['preparing', 'cancelled'],
            'preparing': ['delivering', 'cancelled'],
            'delivering': ['delivered', 'cancelled'],
            'delivered': [],
            'cancelled': []
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            flash(f'Cannot change status from {current_status} to {new_status}')
            return redirect(url_for('manager_orders'))
        
        if new_status == 'accepted' and current_status == 'sent':
            cur.execute("""
                SELECT SUM(
                    CASE 
                        WHEN m.discount IS NOT NULL AND m.discount_end_time > NOW() 
                        THEN ci.quantity * m.price * (1 - m.discount/100)
                        ELSE ci.quantity * m.price
                    END
                ) as order_total
                FROM CartItem ci
                JOIN MenuItem m ON ci.item_id = m.item_id
                WHERE ci.cart_id = %s
            """, (cart_id,))
            
            result = cur.fetchone()
            order_total = result['order_total'] if result and result['order_total'] else 0
            
            print(f"DEBUG: Order total calculated: ${order_total}")
            
            cur.execute("SHOW COLUMNS FROM Restaurant LIKE 'balance'")
            balance_column_exists = cur.fetchone() is not None
            
            if not balance_column_exists:
                cur.execute("ALTER TABLE Restaurant ADD COLUMN balance DECIMAL(10,2) DEFAULT 0")
                conn.commit()
                print("DEBUG: Added balance column to Restaurant table")
            
            cur.execute("""
                UPDATE Restaurant 
                SET balance = COALESCE(balance, 0) + %s
                WHERE restaurant_id = %s
            """, (order_total, restaurant_id))
            
            if cur.rowcount == 0:
                print(f"DEBUG: Failed to update restaurant balance")
                flash('Error updating restaurant balance')
                conn.rollback()
                return redirect(url_for('manager_orders'))
                
            print(f"DEBUG: Updated restaurant balance (+${order_total})")
            
        cur.execute("""
            UPDATE Cart 
            SET status = %s 
            WHERE cart_id = %s
        """, (new_status, cart_id))
        
        if cur.rowcount == 0:
            print(f"DEBUG: Failed to update cart status")
            flash('Error updating order status')
            conn.rollback()
            return redirect(url_for('manager_orders'))
            
        conn.commit()
        
        if new_status == 'accepted':
            flash(f'Order #{cart_id} accepted! ${order_total:.2f} added to your balance.')
        else:
            flash(f'Order #{cart_id} updated to: {new_status}')
        
    except Exception as e:
        conn.rollback()
        flash('Error updating order status')
        print(f"Error updating order status: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
       
        conn.autocommit = True
        cur.close()
        conn.close()
    
    return redirect(url_for('manager_orders'))

@app.route('/manager/dashboard')
def manager_dashboard():
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT * FROM Restaurant WHERE user_id = %s", (session['user_id'],))
    restaurant = cur.fetchone()
    cur.fetchall()
    
    pending_orders = 0
    if restaurant:
        cur.execute("""
            SELECT COUNT(*) as pending_count 
            FROM Cart 
            WHERE restaurant_id = %s AND status IN ('sent', 'accepted', 'preparing', 'delivering')
        """, (restaurant['restaurant_id'],))
        result = cur.fetchone()
        pending_orders = result['pending_count'] if result else 0
        
        today = datetime.now().date()
        cur.execute("""
            SELECT SUM(
                CASE 
                    WHEN m.discount IS NOT NULL AND m.discount_end_time > NOW() 
                    THEN ci.quantity * m.price * (1 - m.discount/100)
                    ELSE ci.quantity * m.price
                END
            ) as today_sales
            FROM Cart c
            JOIN CartItem ci ON c.cart_id = ci.cart_id
            JOIN MenuItem m ON ci.item_id = m.item_id
            WHERE c.restaurant_id = %s 
            AND c.status = 'delivered'
            AND DATE(c.timestamp) = %s
        """, (restaurant['restaurant_id'], today))
        
        result = cur.fetchone()
        today_sales = result['today_sales'] if result and result['today_sales'] else 0
    else:
        today_sales = 0
    
    cur.close()
    conn.close()

    return render_template('manager_dashboard.html', 
                         restaurant=restaurant, 
                         pending_orders=pending_orders,
                         today_sales=today_sales)

@app.route('/manager/restaurant', methods=['GET', 'POST'])
def manager_restaurant():
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Restaurant WHERE user_id = %s", (session['user_id'],))
    restaurant = cur.fetchone()
    cur.fetchall()

    tags = []
    if restaurant:
        cur.execute("SELECT tag FROM RestaurantTags WHERE restaurant_id = %s", (restaurant['restaurant_id'],))
        tags = [row['tag'] for row in cur.fetchall()]

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        city = request.form['city']
        town = request.form['town']
        phone_num = request.form['phone_num']
        tags_input = request.form.get('tags', '')
        tag_list = [t.strip() for t in tags_input.split(',') if t.strip()]

        if restaurant:
            cur.execute("""
                UPDATE Restaurant SET name=%s, address=%s, city=%s, town=%s, phone_num=%s
                WHERE user_id=%s
            """, (name, address, city, town, phone_num, session['user_id']))
            restaurant_id = restaurant['restaurant_id']
        else:
            cur.execute("""
                INSERT INTO Restaurant (name, user_id, address, city, town, phone_num)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, session['user_id'], address, city, town, phone_num))
            restaurant_id = cur.lastrowid

        cur.execute("DELETE FROM RestaurantTags WHERE restaurant_id = %s", (restaurant_id,))
        for tag in tag_list:
            cur.execute("INSERT INTO RestaurantTags (restaurant_id, tag) VALUES (%s, %s)", (restaurant_id, tag))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('manager_dashboard'))

    cur.close()
    conn.close()
    return render_template('manager_restaurant.html', restaurant=restaurant, tags=tags)

@app.route('/manager/menu', methods=['GET', 'POST'])
def manager_menu():
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Restaurant WHERE user_id = %s", (session['user_id'],))
    restaurant = cur.fetchone()
    cur.fetchall()
    if not restaurant:
        cur.close()
        conn.close()
        flash('Please create your restaurant first.')
        return redirect(url_for('manager_restaurant'))

    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        cuisine_type = request.form['cuisine_type']
        price = request.form['price']
        discount = request.form.get('discount')
        if discount == '':
            discount = None
        discount_end_time = request.form.get('discount_end_time')
        image = request.form.get('image')
        cur.execute("""
            INSERT INTO MenuItem (restaurant_id, name, description, cuisine_type, price, discount, discount_end_time, image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (restaurant['restaurant_id'], name, description, cuisine_type, price, discount, discount_end_time, image))
        conn.commit()

    
    cur.execute("SELECT * FROM MenuItem WHERE restaurant_id = %s ORDER BY name", (restaurant['restaurant_id'],))
    menu_items = cur.fetchall()
    for item in menu_items:
        if item['discount_end_time']:
            item['discount_end_time'] = item['discount_end_time'].strftime('%Y-%m-%dT%H:%M')
    cur.close()
    conn.close()
    now = datetime.now().strftime('%Y-%m-%dT%H:%M')
    return render_template('manager_menu.html', restaurant=restaurant, menu_items=menu_items, now=now)

@app.route('/manager/menu/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_menu_item(item_id):
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(dictionary=True)
   
    cur.execute("SELECT * FROM Restaurant WHERE user_id = %s", (session['user_id'],))
    restaurant = cur.fetchone()
    cur.fetchall()
    if not restaurant:
        cur.close()
        conn.close()
        flash('Please create your restaurant first.')
        return redirect(url_for('manager_restaurant'))
   
    cur.execute("SELECT * FROM MenuItem WHERE item_id = %s AND restaurant_id = %s", (item_id, restaurant['restaurant_id']))
    item = cur.fetchone()
    if not item:
        cur.close()
        conn.close()
        flash('Menu item not found.')
        return redirect(url_for('manager_menu'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        cuisine_type = request.form['cuisine_type']
        price = request.form['price']
        discount = request.form.get('discount')
        if discount == '':
            discount = None
        discount_end_time = request.form.get('discount_end_time')
        image = request.form.get('image')
        cur.execute("""
            UPDATE MenuItem SET name=%s, description=%s, cuisine_type=%s, price=%s, discount=%s, discount_end_time=%s, image=%s
            WHERE item_id=%s AND restaurant_id=%s
        """, (name, description, cuisine_type, price, discount, discount_end_time, image, item_id, restaurant['restaurant_id']))
        conn.commit()
        cur.close()
        conn.close()
        flash('Menu item updated!')
        return redirect(url_for('manager_menu'))
    
    if item['discount_end_time']:
        item['discount_end_time'] = item['discount_end_time'].strftime('%Y-%m-%dT%H:%M')
    cur.close()
    conn.close()
    return render_template('edit_menu_item.html', restaurant=restaurant, item=item)

@app.route('/manager/sales')
def manager_sales():
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))
    
    conn = None
    cursor = None
    
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        
        cursor.execute("SELECT * FROM Restaurant WHERE user_id = %s", (session['user_id'],))
        restaurant = cursor.fetchone()
        
        if not restaurant:
            flash('Please create your restaurant first.')
            return redirect(url_for('manager_restaurant'))
            
        restaurant_id = restaurant['restaurant_id']
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT c.cart_id) as order_count,
                COALESCE(SUM(
                    CASE 
                        WHEN m.discount IS NOT NULL AND m.discount_end_time > NOW() 
                        THEN ci.quantity * m.price * (1 - m.discount/100)
                        ELSE ci.quantity * m.price
                    END
                ), 0) as total_revenue
            FROM Cart c
            JOIN CartItem ci ON c.cart_id = ci.cart_id
            JOIN MenuItem m ON ci.item_id = m.item_id
            WHERE c.restaurant_id = %s 
            AND c.status = 'delivered' 
            AND c.timestamp BETWEEN %s AND %s
        """, (restaurant_id, start_date, end_date))
        summary = cursor.fetchone()
        summary = summary if summary else {'order_count': 0, 'total_revenue': 0}
        
       
        cursor.execute("""
            SELECT 
                m.name,
                COALESCE(SUM(ci.quantity), 0) as total_quantity,
                COALESCE(SUM(
                    CASE 
                        WHEN m.discount IS NOT NULL AND m.discount_end_time > NOW() 
                        THEN ci.quantity * m.price * (1 - m.discount/100)
                        ELSE ci.quantity * m.price
                    END
                ), 0) as total_revenue
            FROM MenuItem m
            LEFT JOIN CartItem ci ON m.item_id = ci.item_id
            LEFT JOIN Cart c ON ci.cart_id = c.cart_id 
                AND c.status = 'delivered' 
                AND c.timestamp BETWEEN %s AND %s
            WHERE m.restaurant_id = %s
            GROUP BY m.item_id, m.name
            ORDER BY total_quantity DESC
        """, (start_date, end_date, restaurant_id))
        item_stats = list(cursor.fetchall())
        
      
        cursor.execute("""
            SELECT 
                u.username,
                COUNT(DISTINCT c.cart_id) as order_count
            FROM Cart c
            JOIN User u ON c.user_id = u.user_id
            WHERE c.restaurant_id = %s 
            AND c.status = 'delivered' 
            AND c.timestamp BETWEEN %s AND %s
            GROUP BY u.user_id, u.username
            ORDER BY order_count DESC
            LIMIT 1
        """, (restaurant_id, start_date, end_date))
        top_customer = cursor.fetchone()
        
        
        cursor.execute("""
            SELECT 
                u.username,
                c.cart_id,
                c.timestamp,
                COALESCE(SUM(
                    CASE 
                        WHEN m.discount IS NOT NULL AND m.discount_end_time > NOW() 
                        THEN ci.quantity * m.price * (1 - m.discount/100)
                        ELSE ci.quantity * m.price
                    END
                ), 0) as cart_total
            FROM Cart c
            JOIN User u ON c.user_id = u.user_id
            JOIN CartItem ci ON c.cart_id = ci.cart_id
            JOIN MenuItem m ON ci.item_id = m.item_id
            WHERE c.restaurant_id = %s 
            AND c.status = 'delivered' 
            AND c.timestamp BETWEEN %s AND %s
            GROUP BY c.cart_id, u.username, c.timestamp
            HAVING cart_total > 0
            ORDER BY cart_total DESC
            LIMIT 1
        """, (restaurant_id, start_date, end_date))
        top_cart = cursor.fetchone()

        return render_template('manager_sales.html',
                             restaurant=restaurant,
                             summary=summary,
                             item_stats=item_stats,
                             top_customer=top_customer,
                             top_cart=top_cart)

    except Exception as e:
        print(f"Error in sales statistics: {e}")
        flash('Error retrieving sales statistics')
        return redirect(url_for('manager_dashboard'))
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/manager/update_sales_portfolio', methods=['POST'])
def update_sales_portfolio():
    """Force update the sales portfolio for a restaurant."""
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))
        
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    
    try:
      
        cur.execute("SELECT * FROM Restaurant WHERE user_id = %s", (session['user_id'],))
        restaurant = cur.fetchone()
        
        if not restaurant:
            flash('Restaurant not found')
            return redirect(url_for('manager_dashboard'))
            
       
        cur.execute("""
            SELECT SUM(
                CASE 
                    WHEN m.discount IS NOT NULL AND m.discount_end_time > NOW() 
                    THEN ci.quantity * m.price * (1 - m.discount/100)
                    ELSE ci.quantity * m.price
                END
            ) as total_sales
            FROM Cart c
            JOIN CartItem ci ON c.cart_id = ci.cart_id
            JOIN MenuItem m ON ci.item_id = m.item_id
            WHERE c.restaurant_id = %s 
            AND c.status IN ('delivered', 'accepted')
        """, (restaurant['restaurant_id'],))
        
        result = cur.fetchone()
        total_sales = result['total_sales'] if result and result['total_sales'] else 0
        

        cur.execute("SHOW COLUMNS FROM Restaurant LIKE 'balance'")
        balance_column_exists = cur.fetchone() is not None
        

        if not balance_column_exists:
            cur.execute("ALTER TABLE Restaurant ADD COLUMN balance DECIMAL(10,2) DEFAULT 0")
            conn.commit()
        

        cur.execute("""
            UPDATE Restaurant 
            SET balance = %s
            WHERE restaurant_id = %s
        """, (total_sales, restaurant['restaurant_id']))
        
        conn.commit()
        flash(f'Sales portfolio updated! Current balance: ${total_sales:.2f}')
        
    except Exception as e:
        conn.rollback()
        flash('Error updating sales portfolio')
        print(f"Error updating sales portfolio: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        cur.close()
        conn.close()
        
    return redirect(url_for('manager_dashboard'))


def get_popular_restaurants(limit=3):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    try:
       
        cur.execute("""
            SELECT  r.*, u.username, rt.rating_count, rt.avg_rating,
                    GROUP_CONCAT(rtag.tag SEPARATOR ',') AS tags
            FROM Restaurant r
            JOIN User u               ON r.user_id = u.user_id
            JOIN RestaurantRatings rt ON r.restaurant_id = rt.restaurant_id
            LEFT JOIN RestaurantTags rtag ON rtag.restaurant_id = r.restaurant_id
            WHERE rt.rating_count >= 2
            GROUP BY r.restaurant_id
            ORDER BY COALESCE(rt.avg_rating, 0) DESC, r.name ASC
            LIMIT %s
        """, (limit,))

        restaurants = cur.fetchall()
        return restaurants                  

    except Exception as e:
        print("Error getting popular restaurants:", e)
        import traceback
        traceback.print_exc()
        return []

    finally:
        cur.close()
        conn.close()













if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)