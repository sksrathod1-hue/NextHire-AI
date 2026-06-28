from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import re

# Patch Python's SSL environment to use certifi CA certificates bundle on local machine
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
except Exception as ssl_err:
    print(f"SSL certificate configuration warning: {ssl_err}")
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from database.db_manager import get_db_connection, init_db

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper to scan files for skills
def parse_resume_text(file_path):
    # Robust printable text extraction fallback for PDF/Docx/Text
    content = ""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()
    except:
        pass
        
    if not content:
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                # Extract printable characters
                content = "".join(chr(c) if (32 <= c <= 126 or c == 10 or c == 13) else " " for c in data).lower()
        except:
            content = ""

    skills_pool = {
        "python": "Python Development",
        "javascript": "JavaScript / ES6",
        "react": "React.js Framework",
        "html": "HTML5 Semantics",
        "css": "CSS3 Visual Styling",
        "sql": "SQL Database Querying",
        "git": "Git Version Control",
        "docker": "Docker Containerization",
        "aws": "AWS Cloud Services",
        "node": "Node.js Server Runtime",
        "kubernetes": "Kubernetes Orchestration",
        "typescript": "TypeScript Compiler",
        "mongodb": "MongoDB Document Store",
        "flask": "Flask Microframework",
        "django": "Django Framework",
        "java": "Java Architecture",
        "c++": "C++ Performance Programming"
    }

    matched_skills = []
    missing_skills = []
    
    for skill_key, skill_name in skills_pool.items():
        # Match word boundaries or simple search
        if re.search(r'\b' + re.escape(skill_key) + r'\b', content) or skill_key in content:
            matched_skills.append(skill_name)
        else:
            missing_skills.append(skill_name)
            
    # Calculate Match Score
    num_matched = len(matched_skills)
    ats_score = min(50 + (num_matched * 5), 98) if num_matched > 0 else 45
    
    # Recommendations
    recs = []
    if missing_skills:
        recs.append(f"Consider integrating skill mappings for: {', '.join(missing_skills[:3])}.")
    if ats_score < 75:
        recs.append("Restructure header blocks to align with FAANG target standards.")
    else:
        recs.append("Your resume matches FAANG standard layout practices.")
    recs.append("Include more quantifiable metrics and impact metrics (e.g., 'reduced latency by 30%').")

    return {
        "score": ats_score,
        "matched": ", ".join(matched_skills) if matched_skills else "None",
        "missing": ", ".join(missing_skills[:4]) if missing_skills else "None",
        "recommendations": " ".join(recs)
    }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["fullname"] = user["fullname"]
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials. Connection rejected.")
            
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")
        college = request.form.get("college")
        
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO users (fullname, email, password, phone, college)
            VALUES (?, ?, ?, ?, ?)
            ''', (fullname, email, hashed_password, phone, college))
            conn.commit()
            
            user_id = cursor.lastrowid
            session["user_id"] = user_id
            session["fullname"] = fullname
            conn.close()
            return redirect(url_for("dashboard"))
        except Exception as e:
            conn.close()
            return render_template("signup.html", error="Email already registered in system databases.")
            
    return render_template("signup.html")

import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

@app.route("/google-login")
@app.route("/login/google")
def login_google():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    client_id = app.config['GOOGLE_CLIENT_ID']
    redirect_uri = url_for('auth_google_callback', _external=True)
    if "127.0.0.1" in redirect_uri:
        redirect_uri = redirect_uri.replace("127.0.0.1", "localhost")
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
    )
    return redirect(google_auth_url)

@app.route("/auth/google/callback", methods=["GET", "POST"])
def auth_google_callback():
    code = request.args.get("code") or request.form.get("code")
    if not code:
        return render_template("login.html", error="Google Authentication error: Missing OAuth code.")
        
    client_id = app.config['GOOGLE_CLIENT_ID']
    client_secret = app.config['GOOGLE_CLIENT_SECRET']
    redirect_uri = url_for('auth_google_callback', _external=True)
    if "127.0.0.1" in redirect_uri:
        redirect_uri = redirect_uri.replace("127.0.0.1", "localhost")
    
    # Exchange authorization code for token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    try:
        import certifi
        cert_path = certifi.where()
        token_response = requests.post(token_url, data=token_data, verify=cert_path)
        token_response_data = token_response.json()
        id_token_jwt = token_response_data.get("id_token")
        
        if not id_token_jwt:
            err_desc = token_response_data.get('error_description', 'No ID Token returned')
            return render_template("login.html", error=f"Google OAuth token exchange failed: {err_desc}")
            
        # Cryptographically verify token using custom transport session with certifi
        session_obj = requests.Session()
        session_obj.verify = cert_path
        custom_request = google_requests.Request(session=session_obj)
        
        id_info = id_token.verify_oauth2_token(
            id_token_jwt,
            custom_request,
            client_id,
            clock_skew_in_seconds=300
        )
        
        email = id_info.get("email")
        fullname = id_info.get("name")
        google_id = id_info.get("sub")
        picture = id_info.get("picture")
        
    except Exception as e:
        return render_template("login.html", error=f"Google ID Token verification failed: {str(e)}")

    if not email:
        return render_template("login.html", error="Google Authentication error: Email details not provided.")
        
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ? OR google_id = ?", (email, google_id)).fetchone()
    
    if user:
        # Sync google ID and profile picture url if not set
        if not user["google_id"] or not user["avatar_url"]:
            conn.execute(
                "UPDATE users SET google_id = ?, avatar_url = ? WHERE id = ?",
                (google_id, picture, user["id"])
            )
            conn.commit()
        user_id = user["id"]
        session_name = user["fullname"]
    else:
        # Provision a new account automatically
        cursor = conn.cursor()
        hashed_password = generate_password_hash("google-oauth-password-sentinel-key")
        cursor.execute('''
        INSERT INTO users (fullname, email, password, google_id, avatar_url, phone, college)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (fullname, email, hashed_password, google_id, picture, "+1 (555) 000-0000", "Google OAuth Verified"))
        conn.commit()
        user_id = cursor.lastrowid
        session_name = fullname
    conn.close()
    
    # Create a secure session
    session["user_id"] = user_id
    session["fullname"] = session_name
    
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    user_id = session["user_id"]
    
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    
    # Fetch Resumes Match History
    resumes = conn.execute("SELECT * FROM resumes WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    
    # Fetch Mocks History
    interviews = conn.execute("SELECT * FROM interviews WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    
    # Fetch All Users (for Admin Registry)
    all_users = conn.execute("SELECT fullname, target_role, college, (SELECT MAX(ats_score) FROM resumes WHERE user_id = users.id) as max_score FROM users").fetchall()
    
    conn.close()
    
    # Calculate stats
    current_resume_score = resumes[0]["ats_score"] if resumes else 0
    current_readiness = int(sum(i["score"] for i in interviews) / len(interviews)) if interviews else 0
    
    # Generate simple charts lists from history
    weekly_trend = [65, 70, 75, 80, 85]
    if interviews:
        # Pad or use real scores
        scores = [i["score"] for i in reversed(interviews[-5:])]
        weekly_trend = (weekly_trend + scores)[-5:]

    return render_template(
        "dashboard.html",
        user=user,
        resumes=resumes,
        interviews=interviews,
        all_users=all_users,
        current_resume_score=current_resume_score,
        current_readiness=current_readiness,
        weekly_trend=weekly_trend
    )

@app.route("/update-profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    user_id = session["user_id"]
    fullname = request.form.get("fullname")
    email = request.form.get("email")
    phone = request.form.get("phone")
    college = request.form.get("college")
    password = request.form.get("password")
    
    # Process avatar upload
    avatar_file = request.files.get("avatar")
    avatar_url = None
    if avatar_file and avatar_file.filename != "":
        try:
            avatar_dir = os.path.join(app.root_path, "static", "uploads", "avatars")
            os.makedirs(avatar_dir, exist_ok=True)
            ext = os.path.splitext(avatar_file.filename)[1]
            filename = f"avatar_{user_id}{ext}"
            avatar_path = os.path.join(avatar_dir, filename)
            avatar_file.save(avatar_path)
            avatar_url = f"/static/uploads/avatars/{filename}"
        except Exception as upload_err:
            print(f"Avatar upload warning: {upload_err}")

    conn = get_db_connection()
    try:
        if password:
            hashed_password = generate_password_hash(password)
            if avatar_url:
                conn.execute('''
                UPDATE users 
                SET fullname = ?, email = ?, phone = ?, college = ?, password = ?, avatar_url = ?
                WHERE id = ?
                ''', (fullname, email, phone, college, hashed_password, avatar_url, user_id))
            else:
                conn.execute('''
                UPDATE users 
                SET fullname = ?, email = ?, phone = ?, college = ?, password = ?
                WHERE id = ?
                ''', (fullname, email, phone, college, hashed_password, user_id))
        else:
            if avatar_url:
                conn.execute('''
                UPDATE users 
                SET fullname = ?, email = ?, phone = ?, college = ?, avatar_url = ?
                WHERE id = ?
                ''', (fullname, email, phone, college, avatar_url, user_id))
            else:
                conn.execute('''
                UPDATE users 
                SET fullname = ?, email = ?, phone = ?, college = ?
                WHERE id = ?
                ''', (fullname, email, phone, college, user_id))
        conn.commit()
        session["fullname"] = fullname
    except Exception as e:
        pass
    finally:
        conn.close()
        
    return redirect(url_for("dashboard"))

@app.route("/update-career", methods=["POST"])
def update_career():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    user_id = session["user_id"]
    target_role = request.form.get("target_role")
    experience_lvl = request.form.get("experience_lvl")
    difficulty = request.form.get("difficulty")
    
    conn = get_db_connection()
    conn.execute('''
    UPDATE users 
    SET target_role = ?, experience_lvl = ?, difficulty = ?
    WHERE id = ?
    ''', (target_role, experience_lvl, difficulty, user_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for("dashboard"))

# --- API Endpoints ---
@app.route("/api/parse-resume", methods=["POST"])
def api_parse_resume():
    if "user_id" not in session:
        return jsonify({"error": "Unauthenticated"}), 401
        
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
        
    user_id = session["user_id"]
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Parse File
    parsed = parse_resume_text(file_path)
    
    # Save to Database
    conn = get_db_connection()
    conn.execute('''
    INSERT INTO resumes (user_id, filename, ats_score, matched_skills, missing_skills, recommendations)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, filename, parsed["score"], parsed["matched"], parsed["missing"], parsed["recommendations"]))
    conn.commit()
    conn.close()
    
    return jsonify({
        "score": parsed["score"],
        "matched": parsed["matched"],
        "missing": parsed["missing"],
        "recommendations": parsed["recommendations"]
    })

def generate_targeted_questions_helper(resume, company, role):
    # Base skills
    skills = []
    if resume and resume["matched_skills"]:
        skills = [s.strip() for s in resume["matched_skills"].split(",") if s.strip()]
        
    if not skills:
        skills = ["Software Engineering", "System Design", "Scalability", "API Design", "Security"]
        
    # Custom company themes
    company_themes = {
        "Google": {
            "q1": f"Google interviews focus heavily on algorithmic scale. Given your background in {skills[0]}, how would you design an efficient indexing and query retrieval engine for Google search?",
            "q2": f"Google requires low-latency performance. How would you design a distributed cache layer using {skills[1] if len(skills) > 1 else 'consistent hashing'} to minimize server roundtrips?",
            "q3": f"Explain how you would handle fault-tolerance and replication across Google-scale data centers when processing operations utilizing {skills[2] if len(skills) > 2 else 'distributed protocols'}."
        },
        "Apple": {
            "q1": f"Apple values clean software-hardware integration. How would you design a local device sync utility using {skills[0]} that prioritizes battery conservation and fast rendering?",
            "q2": f"At Apple, user privacy is paramount. Detail how you would implement local encryption policies and secure key storage for a mobile application leveraging {skills[1] if len(skills) > 1 else 'biometrics'}?",
            "q3": f"Describe a system-level debugging challenge you faced where optimizing {skills[2] if len(skills) > 2 else 'memory leak diagnostics'} significantly improved performance."
        },
        "Vercel": {
            "q1": f"Vercel focuses on the global edge. How would you design a serverless edge function execution pipeline leveraging {skills[0]} to minimize cold starts?",
            "q2": f"For edge rendering, speed is key. How would you optimize Largest Contentful Paint (LCP) and edge cache hit ratios when deploying applications using {skills[1] if len(skills) > 1 else 'React frameworks'}?",
            "q3": f"How do you design a real-time build log streaming service built around {skills[2] if len(skills) > 2 else 'WebSockets'} that scales under traffic spikes?"
        },
        "Microsoft": {
            "q1": f"Microsoft Azure supports high enterprise scale. How would you design a highly scalable multi-tenant SaaS authentication gateway using {skills[0]}?",
            "q2": f"Describe how you would orchestrate API version control and fallback mechanisms for cloud services running on {skills[1] if len(skills) > 1 else 'Kubernetes'}?",
            "q3": f"How would you build a telemetry dashboard that processes millions of diagnostics packets using {skills[2] if len(skills) > 2 else 'Azure Event Hubs'}?"
        }
    }
    
    # Fallback/General option
    default_theme = {
        "q1": f"Based on your resume skills in {skills[0]}, how would you structure code reviews and unit test coverage to ensure high quality in production features?",
        "q2": f"Design a decoupled API layer that resolves bottleneck latencies using {skills[1] if len(skills) > 1 else 'asynchronous message queues'}.",
        "q3": f"Detail how you would identify and resolve database concurrency or race conditions when scaling operations utilizing {skills[2] if len(skills) > 2 else 'transaction locks'}."
    }
    
    selected = company_themes.get(company, default_theme)
    
    return [
        selected["q1"],
        selected["q2"],
        selected["q3"]
    ]

@app.route("/api/generate-targeted-interview", methods=["POST"])
def api_generate_targeted_interview():
    if "user_id" not in session:
        return jsonify({"error": "Unauthenticated"}), 401
        
    data = request.get_json()
    role = data.get("role", "Frontend Engineer")
    company = data.get("company", "General Mock")
    
    user_id = session["user_id"]
    
    # Fetch user's latest parsed resume
    conn = get_db_connection()
    resume = conn.execute("SELECT * FROM resumes WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,)).fetchone()
    conn.close()
    
    # Generate targeted questions
    questions = generate_targeted_questions_helper(resume, company, role)
    
    return jsonify({
        "role": role,
        "company": company,
        "questions": questions
    })

@app.route("/api/evaluate-answer", methods=["POST"])
def api_evaluate_answer():
    if "user_id" not in session:
        return jsonify({"error": "Unauthenticated"}), 401
        
    data = request.get_json()
    role = data.get("role")
    question = data.get("question")
    answer = data.get("answer", "")
    
    user_id = session["user_id"]
    
    # Simple semantic evaluation algorithm
    length_weight = min(len(answer.split()) * 2, 35) # Up to 35 points for length
    
    # Key concept checking
    concepts = {
        "react": ["dom", "render", "memo", "state", "callback", "perf", "hook", "component"],
        "latency": ["cache", "cdn", "index", "quantization", "edge", "query", "optimize"],
        "roadmap": ["prioritize", "debt", "value", "milestone", "delivery", "sprint"],
        "model": ["leak", "shift", "train", "eval", "data", "validate", "precision"]
    }
    
    concept_weight = 0
    matched_concepts = []
    
    # Find matching keywords
    answer_lower = answer.lower()
    for cat, list_words in concepts.items():
        for word in list_words:
            if word in answer_lower:
                concept_weight += 8
                matched_concepts.append(word)
                
    concept_weight = min(concept_weight, 55) # Up to 55 points for concepts
    
    base_score = 45 # Default floor score
    final_score = min(base_score + length_weight + concept_weight, 98)
    
    # Strengths and corrections
    strengths = "Good structural overview of principles."
    if matched_concepts:
        strengths = f"Excellent use of keyword metrics like: {', '.join(set(matched_concepts[:3]))}."
        
    corrections = "Include more granular infrastructure references."
    if len(answer.split()) < 15:
        corrections = "Expand explanations with project examples. Provide more detailed context."
    elif not matched_concepts:
        corrections = "Reference specific scaling strategies (caching, latency bounds, and state limits)."
        
    # Save to Database
    conn = get_db_connection()
    conn.execute('''
    INSERT INTO interviews (user_id, role, question, answer, score, strengths, corrections)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, role, question, answer, final_score, strengths, corrections))
    conn.commit()
    conn.close()
    
    return jsonify({
        "score": final_score,
        "strengths": strengths,
        "corrections": corrections
    })
@app.route("/api/generate-negotiation-strategy", methods=["POST"])
def api_generate_negotiation_strategy():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json()
    if not data or "company" not in data or "role" not in data:
        return jsonify({"error": "Missing parameters."}), 400
        
    company = data.get("company").strip()
    role = data.get("role").strip()
    
    if not company or not role:
        return jsonify({"error": "Company and role are required."}), 400
        
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    
    exp = user["experience_lvl"] if user and "experience_lvl" in user.keys() else "Mid"
    
    # Tier assessment
    tier_1_names = ["google", "apple", "microsoft", "stripe", "meta", "amazon", "netflix", "vercel", "uber", "airbnb"]
    is_tier_1 = any(t in company.lower() for t in tier_1_names)
    
    if exp == "Junior":
        low = 110000 if is_tier_1 else 80000
        med = 135000 if is_tier_1 else 95000
        high = 155000 if is_tier_1 else 115000
    elif exp == "Senior":
        low = 205000 if is_tier_1 else 145000
        med = 235000 if is_tier_1 else 170000
        high = 270000 if is_tier_1 else 195000
    else: # Mid
        low = 145000 if is_tier_1 else 105000
        med = 175000 if is_tier_1 else 125000
        high = 198000 if is_tier_1 else 148000
        
    low_str = f"${low:,}"
    med_str = f"${med:,}"
    high_str = f"${high:,}"
    range_str = f"${low:,} - ${high:,}"
    
    expectation_script = (
        f"\"Thank you for raising compensation. I am currently focused on finding the right role alignment, "
        f"but based on my research for a {role} at a company of {company}'s scale, I understand the market "
        f"range to be around {range_str}. I would be open to reviewing a competitive offer that takes my "
        f"parsed technical background into account.\""
    )
    
    counter_script = (
        f"\"Thank you so much for extending the offer for the {role} position! I am extremely excited "
        f"about the opportunity to join {company}. Based on my current pipeline and competitive benchmarks "
        f"for this role, I was hoping we could align the base compensation closer to {high_str}. "
        f"If we can move the base to this level, I am ready to sign the agreement today.\""
    )
    
    return jsonify({
        "low": low_str,
        "median": med_str,
        "high": high_str,
        "expectation_script": expectation_script,
        "counter_script": counter_script
    })
@app.route("/api/subscribe-newsletter", methods=["POST"])
def api_subscribe_newsletter():
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "Missing email details."}), 400
        
    email = data.get("email")
    if not email:
        return jsonify({"error": "Invalid email value."}), 400
        
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO newsletter_subscribers (email) VALUES (?)", (email,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Successfully subscribed to NextHire career tips!"})
    except Exception as e:
        conn.close()
        return jsonify({"success": True, "message": "You are already subscribed to our lists."})

@app.route("/api/submit-contact", methods=["POST"])
def api_submit_contact():
    data = request.get_json()
    if not data or "name" not in data or "email" not in data or "message" not in data:
        return jsonify({"error": "Missing contact form fields."}), 400
        
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")
    
    if not name or not email or not message:
        return jsonify({"error": "All fields are required."}), 400
        
    import re
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        return jsonify({"error": "Please enter a valid email address."}), 400
        
    if len(message.strip()) < 10:
        return jsonify({"error": "Message must be at least 10 characters long."}), 400
        
    conn = get_db_connection()
    conn.execute("INSERT INTO contact_messages (name, email, message) VALUES (?, ?, ?)", (name, email, message))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "Your message was sent successfully! We will get back to you shortly."})

def get_row_count(conn, query, params=()):
    row = conn.execute(query, params).fetchone()
    if not row:
        return 0
    if isinstance(row, dict) or (hasattr(row, 'keys') and not isinstance(row, tuple)):
        return list(row.values())[0]
    return row[0]

@app.route("/admin")
@app.route("/admin/<tab>")
def admin_portal(tab="dashboard"):
    if "user_id" not in session:
        return redirect(url_for("home", error="Access Denied: Administrator privileges required."))
        
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    
    if not user or not user["is_admin"]:
        if not user or user["email"] != "sksrathod1@gmail.com":
            conn.close()
            return redirect(url_for("home", error="Access Denied: Administrator privileges required."))
            
    # Gather statistics
    stats = {}
    
    # Contacts list fetching with search and filters
    search_query = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()
    
    contacts_query = "SELECT * FROM contact_messages"
    contacts_params = []
    
    where_clauses = []
    if search_query:
        where_clauses.append("(name LIKE ? OR email LIKE ?)")
        contacts_params.extend([f"%{search_query}%", f"%{search_query}%"])
    if status_filter:
        where_clauses.append("status = ?")
        contacts_params.append(status_filter)
        
    if where_clauses:
        contacts_query += " WHERE " + " AND ".join(where_clauses)
        
    contacts_query += " ORDER BY created_at DESC"
    contacts = conn.execute(contacts_query, contacts_params).fetchall()
    
    stats["total_messages"] = get_row_count(conn, "SELECT COUNT(*) FROM contact_messages")
    stats["unread_messages"] = get_row_count(conn, "SELECT COUNT(*) FROM contact_messages WHERE status = 'Unread'")
    stats["read_messages"] = get_row_count(conn, "SELECT COUNT(*) FROM contact_messages WHERE status = 'Read'")
    
    stats["total_users"] = get_row_count(conn, "SELECT COUNT(*) FROM users")
    stats["total_subscribers"] = get_row_count(conn, "SELECT COUNT(*) FROM newsletter_subscribers")
    stats["total_resumes"] = get_row_count(conn, "SELECT COUNT(*) FROM resumes")
    stats["total_interviews"] = get_row_count(conn, "SELECT COUNT(*) FROM interviews")
    
    # Lists for tabs
    users_list = conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    subscribers_list = conn.execute("SELECT * FROM newsletter_subscribers ORDER BY created_at DESC").fetchall()
    
    try:
        resumes_list = conn.execute("SELECT r.*, u.fullname FROM resumes r JOIN users u ON r.user_id = u.id ORDER BY r.created_at DESC").fetchall()
    except Exception:
        resumes_list = []
        
    try:
        interviews_list = conn.execute("SELECT i.*, u.fullname FROM interviews i JOIN users u ON i.user_id = u.id ORDER BY i.created_at DESC").fetchall()
    except Exception:
        interviews_list = []
        
    conn.close()
    
    return render_template(
        "admin.html",
        active_tab=tab,
        stats=stats,
        contacts=contacts,
        users=users_list,
        subscribers=subscribers_list,
        resumes=resumes_list,
        interviews=interviews_list,
        search_query=search_query,
        status_filter=status_filter,
        admin_user=user
    )

@app.route("/admin/contacts/<int:msg_id>/read", methods=["POST"])
def admin_mark_read(msg_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    if not user or not user["is_admin"]:
        if not user or user["email"] != "sksrathod1@gmail.com":
            conn.close()
            return jsonify({"error": "Forbidden"}), 403
            
    conn.execute("UPDATE contact_messages SET status = 'Read' WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/admin/contacts/<int:msg_id>/unread", methods=["POST"])
def admin_mark_unread(msg_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    if not user or not user["is_admin"]:
        if not user or user["email"] != "sksrathod1@gmail.com":
            conn.close()
            return jsonify({"error": "Forbidden"}), 403
            
    conn.execute("UPDATE contact_messages SET status = 'Unread' WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/admin/contacts/<int:msg_id>/delete", methods=["POST"])
def admin_delete_msg(msg_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    if not user or not user["is_admin"]:
        if not user or user["email"] != "sksrathod1@gmail.com":
            conn.close()
            return jsonify({"error": "Forbidden"}), 403
            
    conn.execute("DELETE FROM contact_messages WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/manifest.json")
def serve_manifest():
    from flask import send_from_directory
    return send_from_directory("static", "manifest.json")

@app.route("/sw.js")
def serve_sw():
    from flask import send_from_directory, make_response
    response = make_response(send_from_directory("static", "sw.js"))
    response.headers["Content-Type"] = "application/javascript"
    response.headers["Service-Worker-Allowed"] = "/"
    return response

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
