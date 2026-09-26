import uuid
import os
from flask import Flask, render_template,request,redirect,session,flash
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg
from dotenv import load_dotenv

load_dotenv()
#Flask appliction create
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

def get_db_connection():
    conn = psycopg.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432")
    )
    return conn

#Home Route
@app.route("/")
def home():

    wishlist_destinations = []

    if "user_id" in session:

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT destination_name
            FROM wishlist
            WHERE user_id = %s
            """,
            (session["user_id"],)
        )

        wishlist_destinations = [
            row[0] for row in cursor.fetchall()
        ]

        cursor.close()
        conn.close()

    return render_template(
        "index.html",
        wishlist_destinations=wishlist_destinations
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email = %s",(email,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            stored_password = user[3]
            if check_password_hash(stored_password, password):
              session["user_id"] = user[0]
              session["user_name"] = user[1]
              session["user_email"] = user[2]
              return redirect("/")
            else:
                return "Incorrect password!"
        else:
            return "User not found!"
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
         return "Passwords do not match!"

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (name, email, hashed_password)
         )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/my-bookings")
def my_bookings():

    # Check user login
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            customer_name,
            destination,
            package_name,
            travel_date,
            travelers,
            created_at,
            status,
            booking_reference
        FROM bookings
        WHERE user_id = %s
        ORDER BY created_at DESC """,
        (session["user_id"],) )

    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("my_bookings.html", bookings=bookings)
@app.route("/cancel-booking/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE bookings
        SET status = 'Cancelled'
        WHERE id = %s AND user_id = %s
        """,
        (booking_id, session["user_id"])
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/my-bookings")

@app.route("/booking", methods=["GET", "POST"])
def booking():

    # User login hai ya nahi check
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        full_name = request.form.get("fullName")
        email = request.form.get("email")
        phone = request.form.get("phone")
        destination = request.form.get("destination")
        travel_date = request.form.get("travelDate")
        travelers = request.form.get("persons")
        package_name = request.form.get("packageName")
        booking_reference = "TE-" + uuid.uuid4().hex[:8].upper()
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
    """ INSERT INTO bookings( user_id, customer_name, email, phone, destination, package_name, travel_date, travelers, status, booking_reference ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """,
    ( session["user_id"],full_name,email,phone,destination, package_name, travel_date,travelers,"Confirmed",booking_reference))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template(
    "booking_success.html",
    name=full_name,
    package=package_name,
    destination=destination,
    travel_date=travel_date,
    travelers=travelers,
    booking_reference=booking_reference
)
    return render_template("booking.html")

@app.route("/contact", methods=["POST"])
def contact():

    name = request.form.get("name")
    email = request.form.get("email")
    subject = request.form.get("subject")
    message = request.form.get("message")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO contact_messages
        (name, email, subject, message)
        VALUES (%s, %s, %s, %s)
        """,
        (name, email, subject, message)
    )

    conn.commit()
    cursor.close()
    conn.close()
    flash("Message sent successfully! We will get back to you soon.", "success")
    return redirect("/#contact")

@app.route("/toggle-wishlist", methods=["POST"])
def toggle_wishlist():

    # User login check
    if "user_id" not in session:
        return {"success": False, "message": "Please login first"}

    data = request.get_json()

    destination = data.get("destination")
    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check destination already wishlist me hai ya nahi
    cursor.execute(
        """
        SELECT id FROM wishlist
        WHERE user_id = %s AND destination_name = %s
        """,
        (user_id, destination)
    )

    existing_item = cursor.fetchone()

    if existing_item:
        # Already exists → remove
        cursor.execute(
            """
            DELETE FROM wishlist
            WHERE user_id = %s AND destination_name = %s
            """,
            (user_id, destination)
        )

        action = "removed"

    else:
        # Does not exist → add
        cursor.execute(
            """
            INSERT INTO wishlist (user_id, destination_name)
            VALUES (%s, %s)
            """,
            (user_id, destination)
        )

        action = "added"

    conn.commit()

    cursor.close()
    conn.close()

    return {"success": True, "action": action}
@app.route("/subscribe", methods=["POST"])
def subscribe():

    email = request.form.get("email")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check email already subscribed hai ya nahi
    cursor.execute(
        """
        SELECT id FROM newsletter_subscribers
        WHERE email = %s
        """,
        (email,)
    )

    existing_email = cursor.fetchone()

    if existing_email:

        cursor.close()
        conn.close()

        flash("This email is already subscribed!", "error")

        return redirect("/#newsletter")

    # New email save
    cursor.execute(
        """
        INSERT INTO newsletter_subscribers (email)
        VALUES (%s)
        """,
        (email,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash("Successfully subscribed to TravelEase!", "success")

    return redirect("/#newsletter")

@app.route("/manager-login", methods=["GET", "POST"])
def manager_login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, name, email, password
            FROM managers
            WHERE email = %s
            """,
            (email,)
        )

        manager = cursor.fetchone()

        cursor.close()
        conn.close()

        if manager:

            stored_password = manager[3]

            if check_password_hash(stored_password, password):

                session["manager_id"] = manager[0]
                session["manager_name"] = manager[1]

                return redirect("/manager-dashboard")

            else:
                return "Incorrect manager password!"

        else:
            return "Manager not found!"

    return render_template("manager_login.html")

@app.route("/manager-dashboard")
def manager_dashboard():

    # Manager login check
    if "manager_id" not in session:
        return redirect("/manager-login")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Total users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # Total bookings
    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    # Confirmed bookings
    cursor.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = %s",
        ("Confirmed",)
    )
    confirmed_bookings = cursor.fetchone()[0]

    # Cancelled bookings
    cursor.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = %s",
        ("Cancelled",)
    )
    cancelled_bookings = cursor.fetchone()[0]

    # Contact messages
    cursor.execute("SELECT COUNT(*) FROM contact_messages")
    total_messages = cursor.fetchone()[0]

    # Newsletter subscribers
    cursor.execute("SELECT COUNT(*) FROM newsletter_subscribers")
    total_subscribers = cursor.fetchone()[0]

    # Wishlist items
    cursor.execute("SELECT COUNT(*) FROM wishlist")
    total_wishlist = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return render_template(
        "manager_dashboard.html",
        total_users=total_users,
        total_bookings=total_bookings,
        confirmed_bookings=confirmed_bookings,
        cancelled_bookings=cancelled_bookings,
        total_messages=total_messages,
        total_subscribers=total_subscribers,
        total_wishlist=total_wishlist
    )

@app.route("/manager-logout")
def manager_logout():

    session.pop("manager_id", None)
    session.pop("manager_name", None)

    return redirect("/manager-login")
@app.route("/manager-bookings")
def manager_bookings():

    if "manager_id" not in session:
        return redirect("/manager-login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            customer_name,
            email,
            phone,
            destination,
            package_name,
            travel_date,
            travelers,
            status,
            booking_reference,
            created_at
        FROM bookings
        ORDER BY created_at DESC
        """
    )

    bookings = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "manager_bookings.html",
        bookings=bookings
    )
@app.route("/manager-update-booking/<int:booking_id>", methods=["POST"])
def manager_update_booking(booking_id):

    if "manager_id" not in session:
        return redirect("/manager-login")

    status = request.form.get("status")

    allowed_statuses = ["Confirmed", "Pending", "Cancelled"]

    if status not in allowed_statuses:
        return "Invalid booking status!"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE bookings
        SET status = %s
        WHERE id = %s
        """,
        (status, booking_id)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/manager-bookings")

@app.route("/manager-delete-booking/<int:booking_id>", methods=["POST"])
def manager_delete_booking(booking_id):

    if "manager_id" not in session:
        return redirect("/manager-login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM bookings
        WHERE id = %s
        """,
        (booking_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/manager-bookings")    

@app.route("/manager-users")
def manager_users():

    if "manager_id" not in session:
        return redirect("/manager-login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, email
        FROM users
        ORDER BY id DESC
        """
    )

    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "manager_users.html",
        users=users
    )
@app.route("/manager-delete-user/<int:user_id>", methods=["POST"])
def manager_delete_user(user_id):

    if "manager_id" not in session:
        return redirect("/manager-login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM users
        WHERE id = %s
        """,
        (user_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/manager-users")
@app.route("/manager-messages")
def manager_messages():

    if "manager_id" not in session:
        return redirect("/manager-login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, email, subject, message, created_at
        FROM contact_messages
        ORDER BY created_at DESC
        """
    )

    messages = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "manager_messages.html",
        messages=messages
    )

@app.route("/manager-delete-message/<int:message_id>", methods=["POST"])
def manager_delete_message(message_id):

    if "manager_id" not in session:
        return redirect("/manager-login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM contact_messages
        WHERE id = %s
        """,
        (message_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/manager-messages")
@app.route("/manager-delete-subscriber/<int:subscriber_id>", methods=["POST"])
def manager_delete_subscriber(subscriber_id):

    if "manager_id" not in session:
        return redirect("/manager-login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM newsletter_subscribers
        WHERE id = %s
        """,
        (subscriber_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/manager-subscribers")
@app.route("/manager-subscribers")
def manager_subscribers():

    if "manager_id" not in session:
        return redirect("/manager-login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, email, subscribed_at
        FROM newsletter_subscribers
        ORDER BY subscribed_at DESC
        """
    )

    subscribers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "manager_subscribers.html",
        subscribers=subscribers
    )

@app.route("/manager-wishlist")
def manager_wishlist():

    if "manager_id" not in session:
        return redirect("/manager-login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            wishlist.id,
            users.name,
            users.email,
            wishlist.destination_name,
            wishlist.created_at
        FROM wishlist
        JOIN users
        ON wishlist.user_id = users.id
        ORDER BY wishlist.created_at DESC
        """
    )

    wishlist_items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "manager_wishlist.html",
        wishlist_items=wishlist_items
    )
@app.route("/destination/<name>")
def destination_details(name):

    destinations = {

    "Kashmir": {
        "name": "Kashmir",
        "location": "Kashmir, India",

        "package_name": "Magical Kashmir",
        "package_price": "24999",
        "package_days": "5",

        "rating": "4.9",
        "image": "kashmir.jpg",
        "description": "Experience beautiful mountains, peaceful lakes and breathtaking valleys surrounded by nature.",
        "hotel_name": "The Grand Kashmir Hotel",
        "hotel_image": "hotel-kashmir.jpg",
        "hotel_rating": "4.6",
        "hotel_description": "Comfortable stay with modern rooms, beautiful views and convenient facilities.",
        "hotel_features": ["Free Wi-Fi", "Breakfast", "Room Service", "Parking"],
        "places": ["Dal Lake", "Gulmarg", "Pahalgam", "Sonamarg", "Srinagar"],
        "food": "Enjoy Kashmiri cuisine including Rogan Josh, Dum Aloo, Kashmiri Pulao and traditional local dishes.",
        "itinerary": [
            {"day": "Day 1", "plan": "Arrival in Srinagar and hotel check-in."},
            {"day": "Day 2", "plan": "Visit Dal Lake and explore Srinagar."},
            {"day": "Day 3", "plan": "Day trip to Gulmarg."},
            {"day": "Day 4", "plan": "Visit Pahalgam and explore beautiful valleys."},
            {"day": "Day 5", "plan": "Local sightseeing and departure."}
        ],
        "included": ["Hotel accommodation", "Daily breakfast", "Sightseeing", "Local transportation", "Tour assistance"],
        "not_included": ["Flight tickets", "Personal expenses", "Adventure activities", "Travel insurance"]
    },

    "Dubai": {
        "name": "Dubai",
        "location": "Dubai, UAE",

        "package_name": "Dubai Luxury Escape",
        "package_price": "39999",
        "package_days": "6",

        "rating": "4.8",
        "image": "dubai.jpg",
        "description": "Discover luxury, adventure, modern architecture, desert experiences and unforgettable attractions.",
        "hotel_name": "Dubai Grand Hotel",
        "hotel_image": "hotel-dubai.jpg",
        "hotel_rating": "4.7",
        "hotel_description": "Modern hotel with comfortable rooms, excellent service and convenient city access.",
        "hotel_features": ["Free Wi-Fi", "Breakfast", "Swimming Pool", "Gym"],
        "places": ["Burj Khalifa", "Dubai Mall", "Palm Jumeirah", "Dubai Marina", "Desert Safari"],
        "food": "Enjoy delicious Middle Eastern cuisine, Arabic dishes, international food and traditional desserts.",
        "itinerary": [
            {"day": "Day 1", "plan": "Arrival in Dubai and hotel check-in."},
            {"day": "Day 2", "plan": "Visit Burj Khalifa and Dubai Mall."},
            {"day": "Day 3", "plan": "Explore Palm Jumeirah and Dubai Marina."},
            {"day": "Day 4", "plan": "Enjoy desert safari and evening entertainment."},
            {"day": "Day 5", "plan": "Explore local markets and attractions."},
            {"day": "Day 6", "plan": "Breakfast and departure."}
        ],
        "included": ["Hotel accommodation", "Daily breakfast", "Sightseeing", "Airport transfers", "Tour assistance"],
        "not_included": ["Flight tickets", "Personal expenses", "Visa charges", "Travel insurance"]
    },

    "Paris": {
        "name": "Paris",
        "location": "Paris, France",
        "rating": "4.9",
        "image": "paris.jpg",
        "description": "Explore iconic landmarks, beautiful architecture, rich culture and charming streets of Paris.",
        "hotel_name": "Paris Central Hotel",
        "hotel_image": "hotel-paris.jpg",
        "hotel_rating": "4.6",
        "hotel_description": "Elegant accommodation located close to major attractions with comfortable rooms and modern facilities.",
        "hotel_features": ["Free Wi-Fi", "Breakfast", "Restaurant", "Room Service"],
        "places": ["Eiffel Tower", "Louvre Museum", "Arc de Triomphe", "Notre-Dame", "Champs-Élysées"],
        "food": "Experience French cuisine including pastries, croissants, cheese, desserts and traditional French dishes.",
        "itinerary": [
            {"day": "Day 1", "plan": "Arrival in Paris and hotel check-in."},
            {"day": "Day 2", "plan": "Visit Eiffel Tower and Champs-Élysées."},
            {"day": "Day 3", "plan": "Explore Louvre Museum and central Paris."},
            {"day": "Day 4", "plan": "Visit Notre-Dame and Arc de Triomphe."},
            {"day": "Day 5", "plan": "Free time for shopping and local exploration."}
        ],
        "included": ["Hotel accommodation", "Daily breakfast", "City sightseeing", "Local transportation", "Tour assistance"],
        "not_included": ["Flight tickets", "Personal expenses", "Museum tickets", "Travel insurance"]
    },

    "Manali": {
        "name": "Manali",
        "location": "Manali, India",
        "rating": "4.7",
        "image": "manali.jpg",
        "description": "Enjoy peaceful valleys, snowy mountains, beautiful landscapes and exciting adventures.",
        "hotel_name": "Mountain View Manali Resort",
        "hotel_image": "hotel-manali.jpg",
        "hotel_rating": "4.5",
        "hotel_description": "Peaceful mountain resort offering comfortable rooms and beautiful views of the surrounding valleys.",
        "hotel_features": ["Free Wi-Fi", "Breakfast", "Mountain View", "Parking"],
        "places": ["Solang Valley", "Rohtang Pass", "Hadimba Temple", "Old Manali", "Mall Road"],
        "food": "Enjoy Himachali cuisine, traditional Indian dishes, warm beverages and local mountain food.",
        "itinerary": [
            {"day": "Day 1", "plan": "Arrival in Manali and hotel check-in."},
            {"day": "Day 2", "plan": "Visit Hadimba Temple and Old Manali."},
            {"day": "Day 3", "plan": "Explore Solang Valley."},
            {"day": "Day 4", "plan": "Visit Rohtang Pass and surrounding areas."},
            {"day": "Day 5", "plan": "Explore Mall Road and departure."}
        ],
        "included": ["Hotel accommodation", "Daily breakfast", "Sightseeing", "Local transportation", "Tour assistance"],
        "not_included": ["Travel tickets", "Personal expenses", "Adventure activities", "Travel insurance"]
    },

    "Bali": {
        "name": "Bali",
        "location": "Bali, Indonesia",

        "package_name": "Bali Island Paradise",
        "package_price": "44999",
        "package_days": "7",

        "rating": "4.8",
        "image": "bali.jpg",
        "description": "Relax on tropical beaches and discover beautiful temples, resorts and island culture.",
        "hotel_name": "Bali Paradise Resort",
        "hotel_image": "hotel-bali.jpg",
        "hotel_rating": "4.7",
        "hotel_description": "Beautiful tropical resort with comfortable rooms, relaxing surroundings and modern facilities.",
        "hotel_features": ["Free Wi-Fi", "Breakfast", "Swimming Pool", "Spa"],
        "places": ["Ubud", "Kuta Beach", "Tanah Lot", "Seminyak", "Uluwatu Temple"],
        "food": "Enjoy Indonesian cuisine, tropical fruits, seafood, traditional dishes and refreshing beverages.",
        "itinerary": [
            {"day": "Day 1", "plan": "Arrival in Bali and resort check-in."},
            {"day": "Day 2", "plan": "Explore Ubud and its cultural attractions."},
            {"day": "Day 3", "plan": "Relax at Kuta Beach and explore nearby areas."},
            {"day": "Day 4", "plan": "Visit Tanah Lot and Seminyak."},
            {"day": "Day 5", "plan": "Visit Uluwatu Temple and enjoy sunset views."},
            {"day": "Day 6", "plan": "Free day for relaxation and shopping."},
            {"day": "Day 7", "plan": "Breakfast and departure."}
        ],
        "included": ["Resort accommodation", "Daily breakfast", "Sightseeing", "Local transportation", "Tour assistance"],
        "not_included": ["Flight tickets", "Personal expenses", "Water activities", "Travel insurance"]
    },

    "Switzerland": {
        "name": "Switzerland",
        "location": "Switzerland",
        "rating": "4.9",
        "image": "switzerland.jpg",
        "description": "Experience stunning Alps, peaceful lakes, snowy mountains and charming villages.",
        "hotel_name": "Swiss Alpine Resort",
        "hotel_image": "hotel-switzerland.jpg",
        "hotel_rating": "4.8",
        "hotel_description": "Comfortable alpine accommodation surrounded by beautiful mountain landscapes and peaceful scenery.",
        "hotel_features": ["Free Wi-Fi", "Breakfast", "Mountain View", "Restaurant"],
        "places": ["Zurich", "Lucerne", "Interlaken", "Jungfraujoch", "Lake Geneva"],
        "food": "Enjoy Swiss cuisine including cheese fondue, rösti, chocolates and traditional mountain dishes.",
        "itinerary": [
            {"day": "Day 1", "plan": "Arrival in Zurich and hotel check-in."},
            {"day": "Day 2", "plan": "Explore Zurich city and nearby attractions."},
            {"day": "Day 3", "plan": "Visit Lucerne and Lake Lucerne."},
            {"day": "Day 4", "plan": "Explore Interlaken and surrounding mountains."},
            {"day": "Day 5", "plan": "Visit Jungfraujoch and enjoy Alpine views."},
            {"day": "Day 6", "plan": "Explore Lake Geneva and local attractions."},
            {"day": "Day 7", "plan": "Breakfast and departure."}
        ],
        "included": ["Hotel accommodation", "Daily breakfast", "Sightseeing", "Local transportation", "Tour assistance"],
        "not_included": ["Flight tickets", "Personal expenses", "Adventure activities", "Travel insurance"]
    }
}

    destination = destinations.get(name)

    if not destination:
        return "Destination not found!", 404

    return render_template(
        "destination_details.html",
        destination=destination
    )
#run the appliction
if __name__ == "__main__":
    app.run(debug=True)

