import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Healthcare Mobility Monitoring", layout="wide")

# --- ELDER-FRIENDLY STYLING ---
st.markdown("""
<style>
    /* Larger base font for readability */
    html, body, [class*="st-"] {
        font-size: 18px !important;
    }
    /* Headings */
    h1 { font-size: 2.2rem !important; }
    h2 { font-size: 1.8rem !important; }
    h3 { font-size: 1.5rem !important; }
    h4 { font-size: 1.3rem !important; }
    /* Larger body text */
    p, span, label, .stMarkdown, .stCaption p {
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
    }
    /* Metric values - large and bold */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    /* Sidebar text */
    [data-testid="stSidebar"] * {
        font-size: 1.05rem !important;
    }
    /* Buttons */
    .stButton > button {
        font-size: 1.1rem !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
    }
    /* Checkboxes */
    .stCheckbox label {
        font-size: 1.1rem !important;
    }
    /* Dataframe text */
    .stDataFrame td, .stDataFrame th {
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# MOCK DATA
# =====================================================================

USERS = {
    "P1001": {"password": "pass123", "role": "Patient", "name": "John Smith",
              "caregiver": "C2001", "clinician": "D3001"},
    "P1002": {"password": "pass123", "role": "Patient", "name": "Mary Johnson",
              "caregiver": "C2001", "clinician": "D3001"},
    "P1003": {"password": "pass123", "role": "Patient", "name": "Robert Davis",
              "caregiver": "C2002", "clinician": "D3001"},
    "P1004": {"password": "pass123", "role": "Patient", "name": "Linda Wilson",
              "caregiver": "C2002", "clinician": "D3002"},
    "P1005": {"password": "pass123", "role": "Patient", "name": "James Brown",
              "caregiver": "C2003", "clinician": "D3002"},
    "C2001": {"password": "pass123", "role": "Caregiver", "name": "Alice Martin",
              "clinician": "D3001", "patients": ["P1001", "P1002"]},
    "C2002": {"password": "pass123", "role": "Caregiver", "name": "Bob Taylor",
              "clinician": "D3001", "patients": ["P1003", "P1004"]},
    "C2003": {"password": "pass123", "role": "Caregiver", "name": "Carol White",
              "clinician": "D3002", "patients": ["P1005"]},
    "D3001": {"password": "pass123", "role": "Clinician", "name": "Dr. Sarah Lee",
              "caregivers": ["C2001", "C2002"]},
    "D3002": {"password": "pass123", "role": "Clinician", "name": "Dr. Michael Chen",
              "caregivers": ["C2003"]},
}



def get_alerts(patient_id: str):
    """Return mock alerts for a patient."""
    return [
        {"time": "10:45 AM", "type": "Fall Risk",
         "message": "Near-fall detected during sit-to-stand transition.", "severity": "high"},
        {"time": "02:15 PM", "type": "Inactivity",
         "message": "Seated for over 2.5 hours — encourage movement.", "severity": "medium"},
        {"time": "11:30 AM", "type": "Tremor Spike",
         "message": "Tremor intensity exceeded threshold (0.8).", "severity": "high"},
    ]


def get_exercises(patient_id: str):
    """Return mock exercises assigned to a patient, aligned with IoT devices."""
    all_exercises = [
        # --- Upper Limb Exercises (Parkinson's tremor & fine motor) ---
        {"name": "Finger Tapping Drill", "category": "Upper Limb Exercises",
         "duration": "5 min", "frequency": "Daily", "device": "Glove",
         "metric": "Tapping Speed (taps/s)", "target": 2.0, "lower_is_better": False,
         "youtube": "https://www.youtube.com/watch?v=OKpGKiEGbFY",
         "description": "Tap each finger to thumb rapidly for 1 minute per hand. "
                        "Tracked via glove sensors for MDS-UPDRS tapping score."},
        {"name": "Hand Open-Close Repetitions", "category": "Upper Limb Exercises",
         "duration": "5 min", "frequency": "Daily", "device": "Glove",
         "metric": "Grip Force (N)", "target": 15.0, "lower_is_better": False,
         "youtube": "https://www.youtube.com/watch?v=QFpLkgD3R_8",
         "description": "Fully open and close each hand 20 times. "
                        "Glove measures grip force and release speed."},
        {"name": "Pronation-Supination Rotation", "category": "Upper Limb Exercises",
         "duration": "5 min", "frequency": "Daily", "device": "Glove",
         "metric": "Rotation Angle (deg)", "target": 150.0, "lower_is_better": False,
         "youtube": "https://www.youtube.com/watch?v=Chwu0AV-wqM",
         "description": "Rotate forearms palm-up to palm-down for 1 minute per arm. "
                        "Glove tracks rotational tremor patterns."},
        {"name": "Resting Tremor Assessment", "category": "Upper Limb Exercises",
         "duration": "3 min", "frequency": "Daily", "device": "Glove",
         "metric": "Tremor Intensity", "target": 0.4, "lower_is_better": True,
         "youtube": "https://www.youtube.com/watch?v=4SZsPGa-yBQ",
         "description": "Rest hands on lap for 3 minutes while glove records "
                        "resting tremor intensity and frequency."},
        {"name": "Wrist Flexion-Extension Stretch", "category": "Upper Limb Exercises",
         "duration": "5 min", "frequency": "3x per week", "device": "Glove",
         "metric": "Range of Motion (deg)", "target": 70.0, "lower_is_better": False,
         "youtube": "https://www.youtube.com/watch?v=mXMR-IC-G6c",
         "description": "Slowly flex and extend wrists through full range of motion. "
                        "Glove monitors rigidity and range improvement."},
        # --- Lower Limb Exercises (Leg mobility & sit-to-stand) ---
        {"name": "Sit-to-Stand Practice", "category": "Lower Limb Exercises",
         "duration": "10 min", "frequency": "Daily", "device": "Chair",
         "metric": "Transition Time (s)", "target": 2.5, "lower_is_better": True,
         "youtube": "https://www.youtube.com/watch?v=RjnNMRsmNqU",
         "description": "Rise from the sensor chair without using hands, 10 reps. "
                        "Chair sensors measure transition time and balance."},
        {"name": "Seated Leg Raises", "category": "Lower Limb Exercises",
         "duration": "10 min", "frequency": "Daily", "device": "Chair",
         "metric": "Leg Height (cm)", "target": 30.0, "lower_is_better": False,
         "youtube": "https://www.youtube.com/watch?v=YoGa_PoFfEo",
         "description": "Lift each leg straight out while seated, 3 sets of 10. "
                        "Chair sensors track leg elevation and hold duration."},
        {"name": "Seated Marching", "category": "Lower Limb Exercises",
         "duration": "5 min", "frequency": "Daily", "device": "Chair",
         "metric": "Steps/min", "target": 40.0, "lower_is_better": False,
         "youtube": "https://www.youtube.com/watch?v=J5_QC1ZZqvg",
         "description": "Alternate lifting knees in a marching motion while seated. "
                        "Chair detects movement rhythm and symmetry."},
        {"name": "Seated Ankle Circles", "category": "Lower Limb Exercises",
         "duration": "5 min", "frequency": "Daily", "device": "Chair",
         "metric": "Range of Motion (deg)", "target": 35.0, "lower_is_better": False,
         "youtube": "https://www.youtube.com/watch?v=3GjNWHDjBj8",
         "description": "Rotate each ankle clockwise and counter-clockwise, 15 reps each. "
                        "Chair monitors lower-limb range of motion."},
        {"name": "Chair-Assisted Calf Raises", "category": "Lower Limb Exercises",
         "duration": "5 min", "frequency": "3x per week", "device": "Chair",
         "metric": "Raise Height (cm)", "target": 8.0, "lower_is_better": False,
         "youtube": "https://www.youtube.com/watch?v=gWLwQzGF84o",
         "description": "Stand behind chair and rise onto toes, 3 sets of 12. "
                        "Chair sensors track weight shift and balance."},
    ]
    # Assign a subset based on patient_id for variety
    np.random.seed(hash(patient_id + "exercises") % 2**31)
    count = np.random.randint(5, len(all_exercises) + 1)
    indices = np.random.choice(len(all_exercises), size=count, replace=False)
    return [all_exercises[i] for i in sorted(indices)]


def generate_exercise_history(patient_id: str, exercise: dict):
    """Generate 7-day mock data for a specific exercise."""
    seed = hash(patient_id + exercise["name"]) % 2**31
    np.random.seed(seed)
    today = datetime.date.today()
    dates = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
    # Use short day labels (e.g., "Mon 10", "Tue 11") so charts show only 7 points
    day_labels = [d.strftime("%a %d") for d in dates]
    target = exercise["target"]

    # Duration in minutes (how long the patient spent on the exercise each day)
    durations = np.random.uniform(
        max(1, float(exercise["duration"].split()[0]) - 3),
        float(exercise["duration"].split()[0]) + 2,
        7
    ).round(1)

    # Primary metric values (trending around target)
    if exercise["lower_is_better"]:
        metrics = np.random.uniform(target * 0.6, target * 1.8, 7).round(2)
    else:
        metrics = np.random.uniform(target * 0.5, target * 1.3, 7).round(2)

    df = pd.DataFrame({
        "Day": day_labels,
        "Duration (min)": durations,
        exercise["metric"]: metrics,
    })
    return df


def get_exercise_remark(exercise: dict, latest_value: float):
    """Return an emoji and remark based on performance vs target."""
    target = exercise["target"]
    if exercise["lower_is_better"]:
        ratio = target / latest_value if latest_value > 0 else 1.0
    else:
        ratio = latest_value / target if target > 0 else 1.0

    if ratio >= 1.0:
        return "😊", "On Track"
    elif ratio >= 0.75:
        return "😐", "Needs Attention"
    else:
        return "😟", "Below Target"


def get_exercise_feedbacks(patient_id: str):
    """Return mock clinician/caregiver feedback keyed by exercise name."""
    user_info = USERS[patient_id]
    clinician_id = user_info.get("clinician", "")
    caregiver_id = user_info.get("caregiver", "")
    clinician_name = USERS.get(clinician_id, {}).get("name", "Clinician")
    caregiver_name = USERS.get(caregiver_id, {}).get("name", "Caregiver")

    return {
        "Finger Tapping Drill": {
            "from": clinician_name, "role": "Clinician", "date": "2026-03-14",
            "message": "Tapping speed is improving. Keep consistent with daily practice."},
        "Hand Open-Close Repetitions": {
            "from": caregiver_name, "role": "Caregiver", "date": "2026-03-15",
            "message": "Grip strength looks better this week. Great effort!"},
        "Pronation-Supination Rotation": {
            "from": clinician_name, "role": "Clinician", "date": "2026-03-13",
            "message": "Rotation range has plateaued. Try slower, fuller rotations."},
        "Resting Tremor Assessment": {
            "from": clinician_name, "role": "Clinician", "date": "2026-03-15",
            "message": "Tremor intensity trending down — medication adjustment is working."},
        "Wrist Flexion-Extension Stretch": {
            "from": caregiver_name, "role": "Caregiver", "date": "2026-03-12",
            "message": "Good flexibility improvement. Continue stretching after warm-up."},
        "Sit-to-Stand Practice": {
            "from": clinician_name, "role": "Clinician", "date": "2026-03-14",
            "message": "Transition time is decreasing. Watch balance during the rise."},
        "Seated Leg Raises": {
            "from": caregiver_name, "role": "Caregiver", "date": "2026-03-15",
            "message": "Leg elevation has improved. Try holding for 3 seconds at top."},
        "Seated Marching": {
            "from": clinician_name, "role": "Clinician", "date": "2026-03-13",
            "message": "Good rhythm symmetry. Increase pace gradually next week."},
        "Seated Ankle Circles": {
            "from": caregiver_name, "role": "Caregiver", "date": "2026-03-14",
            "message": "Range of motion is within target. Keep it up!"},
        "Chair-Assisted Calf Raises": {
            "from": clinician_name, "role": "Clinician", "date": "2026-03-12",
            "message": "Calf strength improving. Ensure full heel drop between reps."},
    }


def get_todays_exercises(patient_id: str):
    """Return today's scheduled exercises."""
    exercises = get_exercises(patient_id)
    np.random.seed(hash(patient_id + str(datetime.date.today())) % 2**31)
    todays = []
    for ex in exercises:
        if ex["frequency"] == "Daily":
            todays.append(ex)
        elif np.random.random() > 0.5:
            todays.append(ex)
    return todays


def get_feedbacks(patient_id: str):
    """Return mock doctor/caregiver feedback for a patient."""
    return [
        {"from": "Dr. Sarah Lee", "date": "2026-02-24", "source": "Doctor",
         "message": "Tremor levels look stable this week. Keep up the exercises."},
        {"from": "Dr. Michael Chen", "date": "2026-02-22", "source": "Doctor",
         "message": "Consider adjusting sitting breaks — prolonged sitting detected."},
        {"from": "Alice Martin", "date": "2026-02-23", "source": "Caregiver",
         "message": "Your tapping velocity has improved — keep it up!"},
        {"from": "Bob Taylor", "date": "2026-02-21", "source": "Caregiver",
         "message": "Remember to do your stretches after long sitting periods."},
    ]


# =====================================================================
# SESSION STATE HELPERS
# =====================================================================

def init_session():
    for key in ["logged_in", "user_id", "role", "name", "view", "selected_patient",
                "selected_caregiver"]:
        if key not in st.session_state:
            st.session_state[key] = None
    if st.session_state.logged_in is None:
        st.session_state.logged_in = False


def do_login(user_id: str, password: str, role: str):
    user_id = user_id.strip().upper()
    if user_id in USERS and USERS[user_id]["password"] == password and USERS[user_id]["role"] == role:
        st.session_state.logged_in = True
        st.session_state.user_id = user_id
        st.session_state.role = role
        st.session_state.name = USERS[user_id]["name"]
        st.session_state.view = "home"
        st.session_state.selected_patient = None
        st.session_state.selected_caregiver = None
        return True
    return False


def do_logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.logged_in = False


# =====================================================================
# SHARED COMPONENTS
# =====================================================================

def render_reports(patient_id: str):
    """Render Daily and Weekly reports using exercise-based data (in sync with homepage)."""
    exercises = get_exercises(patient_id)
    ex_feedbacks = get_exercise_feedbacks(patient_id)

    tab_daily, tab_weekly, tab_download = st.tabs(
        ["📋 Daily Report", "📊 Weekly Report", "📥 Download"])

    # --- DAILY REPORT TAB ---
    with tab_daily:
        st.subheader("📋 Today's Exercise Report")

        # Today's summary metrics (same logic as homepage top row)
        on_track = 0
        glove_scores = []
        chair_scores = []
        exercise_rows = []

        for ex in exercises:
            history = generate_exercise_history(patient_id, ex)
            latest_val = history[ex["metric"]].iloc[-1]
            latest_dur = history["Duration (min)"].iloc[-1]
            emoji, remark_text = get_exercise_remark(ex, latest_val)

            target = ex["target"]
            if ex["lower_is_better"]:
                ratio = target / latest_val if latest_val > 0 else 1.0
            else:
                ratio = latest_val / target if target > 0 else 1.0
            ratio = min(ratio, 1.5)

            if remark_text == "On Track":
                on_track += 1
            if ex["category"] == "Upper Limb Exercises":
                glove_scores.append(ratio)
            else:
                chair_scores.append(ratio)

            exercise_rows.append({
                "Exercise": ex["name"],
                "Device": ex["device"],
                "Duration (min)": latest_dur,
                ex["metric"]: latest_val,
                "Target": ex["target"],
                "Status": f"{emoji} {remark_text}",
            })

        total_ex = len(exercises)
        glove_avg = round(sum(glove_scores) / len(glove_scores) * 100) if glove_scores else 0
        chair_avg = round(sum(chair_scores) / len(chair_scores) * 100) if chair_scores else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Exercises On Track", f"{on_track}/{total_ex}")
        c2.metric("Upper-Limb Score", f"{glove_avg}%")
        c3.metric("Lower-Limb Score", f"{chair_avg}%")

        st.divider()

        # Per-exercise today's details
        categories = {}
        for ex in exercises:
            categories.setdefault(ex["category"], []).append(ex)

        device_icons = {"Upper Limb Exercises": "🧤", "Lower Limb Exercises": "🪑"}
        for cat, exs in categories.items():
            icon = device_icons.get(cat, "")
            st.markdown(f"### {icon} {cat}")
            for ex in exs:
                history = generate_exercise_history(patient_id, ex)
                latest_val = history[ex["metric"]].iloc[-1]
                latest_dur = history["Duration (min)"].iloc[-1]
                emoji, remark_text = get_exercise_remark(ex, latest_val)
                target_label = "below" if ex["lower_is_better"] else "above"

                st.markdown(f"**{ex['name']}**")
                mc1, mc2, mc3 = st.columns(3)
                mc1.metric("Duration", f"{latest_dur} min")
                mc2.metric(ex["metric"], f"{latest_val}")
                mc2.caption(f"Target: {target_label} {ex['target']}")
                mc3.metric("Status", remark_text)

                fb = ex_feedbacks.get(ex["name"])
                if fb:
                    role_icon = "🩺" if fb["role"] == "Clinician" else "🤝"
                    st.info(
                        f"{role_icon} **{fb['from']}** ({fb['role']}) — _{fb['date']}_: "
                        f"{fb['message']}"
                    )
                st.divider()

    # --- WEEKLY REPORT TAB ---
    with tab_weekly:
        st.subheader("📊 Past 7 Days — Exercise Trends")

        categories = {}
        for ex in exercises:
            categories.setdefault(ex["category"], []).append(ex)

        device_icons = {"Upper Limb Exercises": "🧤", "Lower Limb Exercises": "🪑"}
        for cat, exs in categories.items():
            icon = device_icons.get(cat, "")
            st.markdown(f"### {icon} {cat}")
            for ex in exs:
                history = generate_exercise_history(patient_id, ex)
                st.markdown(f"**{ex['name']}** — _{ex['duration']}, {ex['frequency']}_")

                col_dur, col_metric = st.columns(2)
                with col_dur:
                    st.markdown("**Duration (min)**")
                    st.line_chart(history.set_index("Day")[["Duration (min)"]], height=180)
                with col_metric:
                    st.markdown(f"**{ex['metric']}**")
                    st.bar_chart(history.set_index("Day")[[ex["metric"]]], height=180)
                    target_label = "below" if ex["lower_is_better"] else "above"
                    st.caption(f"Target: {target_label} {ex['target']}")

                st.divider()

    # --- DOWNLOAD TAB ---
    with tab_download:
        st.subheader("📥 Download Report")
        render_download_button(patient_id)


def render_alerts(patient_id: str):
    alerts = get_alerts(patient_id)
    st.subheader("🚨 Alerts")
    for a in alerts:
        if a["severity"] == "high":
            st.error(f"**{a['time']} — {a['type']}**: {a['message']}")
        elif a["severity"] == "medium":
            st.warning(f"**{a['time']} — {a['type']}**: {a['message']}")
        else:
            st.info(f"**{a['time']} — {a['type']}**: {a['message']}")


def render_download_button(patient_id: str):
    exercises = get_exercises(patient_id)
    rows = []
    for ex in exercises:
        history = generate_exercise_history(patient_id, ex)
        for _, row in history.iterrows():
            rows.append({
                "Exercise": ex["name"],
                "Device": ex["device"],
                "Day": row["Day"],
                "Duration (min)": row["Duration (min)"],
                "Metric": ex["metric"],
                "Value": row[ex["metric"]],
                "Target": ex["target"],
            })
    csv = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Patient Report (CSV)",
        data=csv,
        file_name=f"patient_{patient_id}_report.csv",
        mime="text/csv",
    )


def render_send_feedback(sender_id: str, target_id: str, label: str = "patient"):
    """Simple form to send feedback/alert to a target user."""
    with st.expander(f"✉️ Send Feedback / Alert to {label} {target_id}"):
        fb_type = st.selectbox("Type", ["Feedback", "Alert"], key=f"fb_type_{target_id}")
        fb_msg = st.text_area("Message", key=f"fb_msg_{target_id}")
        if st.button("Send", key=f"fb_send_{target_id}"):
            if fb_msg.strip():
                st.success(f"{fb_type} sent to {target_id} successfully!")
            else:
                st.warning("Please enter a message.")


# =====================================================================
# LOGIN PAGE
# =====================================================================

def login_page():
    st.markdown("<h1 style='text-align:center;'>Healthcare Mobility Monitoring System</h1>",
                unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>Login to continue</h4>",
                unsafe_allow_html=True)
    st.divider()

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        role = st.selectbox("I am a:", ["Patient", "Caregiver", "Clinician"])
        user_id = st.text_input("User ID")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            if do_login(user_id, password, role):
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

        st.divider()
        st.markdown("**Demo credentials** (password for all: `pass123`)")
        demo = {
            "Patient": "P1001, P1002, P1003, P1004, P1005",
            "Caregiver": "C2001, C2002, C2003",
            "Clinician": "D3001, D3002",
        }
        for r, ids in demo.items():
            st.markdown(f"- **{r}**: {ids}")


# =====================================================================
# PATIENT FRONTEND
# =====================================================================

def patient_dashboard():
    uid = st.session_state.user_id
    name = st.session_state.name

    st.sidebar.title(f"👤 {name}")
    st.sidebar.caption(f"Patient ID: {uid}")
    if st.sidebar.button("Logout"):
        do_logout()
        st.rerun()

    menu = st.sidebar.radio("Navigation",
                            ["Home", "Daily Goals", "Reports",
                             "Doctor Feedback"])

    # --- HOME ---
    if menu == "Home":
        # Header row with bell icon for alerts in top-right
        hdr_left, hdr_right = st.columns([5, 1])
        with hdr_left:
            st.markdown(f"<h1 style='text-align:center;'>Welcome, {name}!</h1>",
                        unsafe_allow_html=True)
            st.markdown("<h3 style='text-align:center;'>Your daily mobility summary</h3>",
                        unsafe_allow_html=True)
        with hdr_right:
            alerts = get_alerts(uid)
            high_count = sum(1 for a in alerts if a["severity"] == "high")
            bell_label = f"🔔 {len(alerts)}" if alerts else "🔔"
            with st.popover(bell_label):
                st.markdown("### 🚨 Alerts")
                if alerts:
                    for a in alerts:
                        if a["severity"] == "high":
                            st.error(f"**{a['time']} — {a['type']}**: {a['message']}")
                        elif a["severity"] == "medium":
                            st.warning(f"**{a['time']} — {a['type']}**: {a['message']}")
                        else:
                            st.info(f"**{a['time']} — {a['type']}**: {a['message']}")
                else:
                    st.caption("No alerts right now.")
        st.divider()

        # --- Overall health summary derived from actual exercises ---
        exercises = get_exercises(uid)
        ex_feedbacks = get_exercise_feedbacks(uid)

        on_track = 0
        needs_attention = 0
        below_target = 0
        glove_scores = []
        chair_scores = []

        for ex in exercises:
            history = generate_exercise_history(uid, ex)
            latest_val = history[ex["metric"]].iloc[-1]
            emoji, remark_text = get_exercise_remark(ex, latest_val)
            if remark_text == "On Track":
                on_track += 1
            elif remark_text == "Needs Attention":
                needs_attention += 1
            else:
                below_target += 1

            # Compute per-exercise score (ratio to target)
            target = ex["target"]
            if ex["lower_is_better"]:
                ratio = target / latest_val if latest_val > 0 else 1.0
            else:
                ratio = latest_val / target if target > 0 else 1.0
            ratio = min(ratio, 1.5)  # cap at 150%

            if ex["category"] == "Upper Limb Exercises":
                glove_scores.append(ratio)
            else:
                chair_scores.append(ratio)

        total_ex = len(exercises)
        overall_pct = round(on_track / total_ex * 100) if total_ex else 0
        glove_avg = round(sum(glove_scores) / len(glove_scores) * 100) if glove_scores else 0
        chair_avg = round(sum(chair_scores) / len(chair_scores) * 100) if chair_scores else 0

        # Overall health status
        if overall_pct >= 75:
            health_label = "Good"
        elif overall_pct >= 50:
            health_label = "Fair"
        else:
            health_label = "Needs Improvement"

        # Top row: overall metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Exercises On Track", f"{on_track}/{total_ex}")
        c2.metric("Upper-Limb Score", f"{glove_avg}%")
        c3.metric("Lower-Limb Score", f"{chair_avg}%")
        c4.metric("Overall Health", health_label)

        # Brief health status message
        st.divider()
        if below_target > 0:
            st.warning(
                f"⚠️ {below_target} exercise(s) are below target today. "
                f"Check the summaries below for details."
            )
        if needs_attention > 0:
            st.info(
                f"💡 {needs_attention} exercise(s) need attention — you're close to target, "
                f"keep pushing!"
            )
        if on_track == total_ex:
            st.success("🏆 All exercises are on track today! Excellent work!")

        st.divider()
        st.subheader("🏋️ Assigned Exercises — Summary Charts")

        # Group by category (device-aligned)
        categories = {}
        for ex in exercises:
            categories.setdefault(ex["category"], []).append(ex)

        device_icons = {"Upper Limb Exercises": "🧤", "Lower Limb Exercises": "🪑"}

        for cat, exs in categories.items():
            icon = device_icons.get(cat, "")
            st.markdown(f"### {icon} {cat}")

            for ex in exs:
                history = generate_exercise_history(uid, ex)
                latest_val = history[ex["metric"]].iloc[-1]
                emoji, remark_text = get_exercise_remark(ex, latest_val)

                st.markdown(f"#### {ex['name']}  —  _{ex['duration']}, {ex['frequency']}_")
                col_time, col_metric, col_remark = st.columns([2, 2, 1])

                # Today's summary (latest row highlight)
                with col_time:
                    st.markdown("**Duration (past 7 days)**")
                    chart_data = history.set_index("Day")[["Duration (min)"]]
                    st.line_chart(chart_data, height=180)
                    st.caption(f"Today: **{history['Duration (min)'].iloc[-1]} min**")

                with col_metric:
                    st.markdown(f"**{ex['metric']} (past 7 days)**")
                    metric_data = history.set_index("Day")[[ex["metric"]]]
                    st.bar_chart(metric_data, height=180)
                    target_label = "below" if ex["lower_is_better"] else "above"
                    st.caption(
                        f"Today: **{latest_val}** · Target: {target_label} {ex['target']}"
                    )

                with col_remark:
                    st.markdown("**Remarks**")
                    st.markdown(
                        f"<div style='text-align:center;font-size:3rem;'>{emoji}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='text-align:center;font-weight:bold;'>{remark_text}</div>",
                        unsafe_allow_html=True,
                    )

                # Feedback for this exercise
                fb = ex_feedbacks.get(ex["name"])
                if fb:
                    role_icon = "🩺" if fb["role"] == "Clinician" else "🤝"
                    st.info(
                        f"{role_icon} **{fb['from']}** ({fb['role']}) — _{fb['date']}_: "
                        f"{fb['message']}"
                    )

                st.divider()

    # --- DAILY GOALS ---
    elif menu == "Daily Goals":
        st.title("🎯 Daily Goals")

        todays_ex = get_todays_exercises(uid)

        if todays_ex:
            total = len(todays_ex)

            # Placeholder for progress bar — filled after checkboxes render
            progress_placeholder = st.empty()
            completion_placeholder = st.empty()
            st.divider()

            today_cats = {}
            for ex in todays_ex:
                today_cats.setdefault(ex["category"], []).append(ex)

            device_icons = {"Upper Limb Exercises": "🧤", "Lower Limb Exercises": "🪑"}
            for cat, exs in today_cats.items():
                icon = device_icons.get(cat, "")
                st.markdown(f"### {icon} {cat}")
                for ex in exs:
                    chk_key = f"chk_{uid}_{ex['name']}"
                    done = st.checkbox(
                        f"**{ex['name']}** — {ex['duration']}",
                        key=chk_key,
                    )
                    if done:
                        st.caption("✅ Completed")
                    else:
                        st.caption(f"📝 {ex['description']}")
                    st.markdown(
                        f"[▶ Watch exercise video]({ex['youtube']})"
                    )

            # Compute progress from checkbox widget keys after they render
            completed_count = sum(
                1 for ex in todays_ex
                if st.session_state.get(f"chk_{uid}_{ex['name']}", False)
            )
            progress_placeholder.progress(
                completed_count / total,
                text=f"{completed_count}/{total} exercises completed"
            )
            if completed_count == total:
                st.balloons()
                completion_placeholder.success(
                    "🎉 All exercises completed for today! Great work!"
                )
        else:
            st.info("No exercises scheduled for today. Enjoy your rest day!")

    # --- REPORTS ---
    elif menu == "Reports":
        st.title("📊 Reports")
        render_reports(uid)

    # --- DOCTOR FEEDBACK ---
    elif menu == "Doctor Feedback":
        st.title("💬 Feedback from Your Care Team")
        feedbacks = get_feedbacks(uid)
        doctor_fb = [fb for fb in feedbacks if fb["source"] == "Doctor"]
        caregiver_fb = [fb for fb in feedbacks if fb["source"] == "Caregiver"]

        st.markdown("### 🩺 Doctor Feedback")
        if doctor_fb:
            for fb in doctor_fb:
                with st.container():
                    st.markdown(f"**{fb['from']}** — _{fb['date']}_")
                    st.info(fb["message"])
        else:
            st.caption("No doctor feedback yet.")

        st.divider()

        st.markdown("### 🤝 Caregiver Feedback")
        if caregiver_fb:
            for fb in caregiver_fb:
                with st.container():
                    st.markdown(f"**{fb['from']}** — _{fb['date']}_")
                    st.success(fb["message"])
        else:
            st.caption("No caregiver feedback yet.")


# =====================================================================
# CAREGIVER FRONTEND
# =====================================================================

def caregiver_dashboard():
    uid = st.session_state.user_id
    name = st.session_state.name
    user_info = USERS[uid]
    patient_ids = user_info.get("patients", [])

    st.sidebar.title(f"👤 {name}")
    st.sidebar.caption(f"Caregiver ID: {uid}")
    if st.sidebar.button("Logout"):
        do_logout()
        st.rerun()

    # If a patient is selected, show their detail view
    if st.session_state.selected_patient:
        pid = st.session_state.selected_patient
        pname = USERS[pid]["name"]
        if st.sidebar.button("⬅ Back to Patient List"):
            st.session_state.selected_patient = None
            st.rerun()

        st.title(f"Patient: {pname} ({pid})")
        tab1, tab2, tab3 = st.tabs(
            ["Reports", "Alerts", "Feedback"])

        with tab1:
            render_reports(pid)
        with tab2:
            render_alerts(pid)
        with tab3:
            render_send_feedback(uid, pid, label="patient")
        return

    # --- Patient List ---
    st.title("My Patients")
    st.divider()
    for pid in patient_ids:
        pname = USERS[pid]["name"]
        col1, col2 = st.columns([3, 1])
        col1.markdown(f"### {pname}")
        col1.caption(f"Patient ID: {pid}")
        if col2.button("View Details", key=f"view_{pid}"):
            st.session_state.selected_patient = pid
            st.rerun()
        st.divider()

    # Caregiver's own alerts section
    st.subheader("🚨 Patient Alerts Overview")
    for pid in patient_ids:
        pname = USERS[pid]["name"]
        alerts = get_alerts(pid)
        high_alerts = [a for a in alerts if a["severity"] == "high"]
        if high_alerts:
            for a in high_alerts:
                st.error(f"**{pname} ({pid})** — {a['time']}: {a['message']}")


# =====================================================================
# CLINICIAN FRONTEND
# =====================================================================

def clinician_dashboard():
    uid = st.session_state.user_id
    name = st.session_state.name
    user_info = USERS[uid]
    caregiver_ids = user_info.get("caregivers", [])

    st.sidebar.title(f"👤 {name}")
    st.sidebar.caption(f"Clinician ID: {uid}")
    if st.sidebar.button("Logout"):
        do_logout()
        st.rerun()

    # --- Sidebar: Search patient by ID ---
    st.sidebar.divider()
    st.sidebar.subheader("🔍 Search Patient")
    search_pid = st.sidebar.text_input("Enter Patient ID").strip().upper()
    if st.sidebar.button("Search"):
        if search_pid in USERS and USERS[search_pid]["role"] == "Patient":
            st.session_state.selected_patient = search_pid
            st.session_state.selected_caregiver = None
            st.rerun()
        elif search_pid:
            st.sidebar.error("Patient not found.")

    # --- Viewing a specific patient ---
    if st.session_state.selected_patient:
        pid = st.session_state.selected_patient
        pname = USERS[pid]["name"]
        if st.sidebar.button("⬅ Back"):
            st.session_state.selected_patient = None
            st.session_state.selected_caregiver = None
            st.rerun()

        st.title(f"Patient: {pname} ({pid})")
        tab1, tab2, tab3 = st.tabs(
            ["Reports", "Alerts", "Feedback"])
        with tab1:
            render_reports(pid)
        with tab2:
            render_alerts(pid)
        with tab3:
            render_send_feedback(uid, pid, label="patient")
            # Also allow feedback to the caregiver of this patient
            cg_id = USERS[pid].get("caregiver")
            if cg_id:
                render_send_feedback(uid, cg_id, label="caregiver")
        return

    # --- Viewing patients under a caregiver ---
    if st.session_state.selected_caregiver:
        cg_id = st.session_state.selected_caregiver
        cg_name = USERS[cg_id]["name"]
        cg_patients = USERS[cg_id].get("patients", [])

        if st.sidebar.button("⬅ Back to Caregivers"):
            st.session_state.selected_caregiver = None
            st.rerun()

        st.title(f"Caregiver: {cg_name} ({cg_id})")
        render_send_feedback(uid, cg_id, label="caregiver")
        st.divider()
        st.subheader("Patients under this caregiver")
        for pid in cg_patients:
            pname = USERS[pid]["name"]
            col1, col2 = st.columns([3, 1])
            col1.markdown(f"### {pname}")
            col1.caption(f"Patient ID: {pid}")
            if col2.button("View Patient", key=f"cview_{pid}"):
                st.session_state.selected_patient = pid
                st.rerun()
            st.divider()
        return

    # --- Default: Caregiver list ---
    st.title("My Caregivers")
    st.divider()
    for cg_id in caregiver_ids:
        cg_name = USERS[cg_id]["name"]
        cg_patients = USERS[cg_id].get("patients", [])
        col1, col2 = st.columns([3, 1])
        col1.markdown(f"### {cg_name}")
        col1.caption(f"Caregiver ID: {cg_id} · Patients: {len(cg_patients)}")
        if col2.button("View Caregiver", key=f"cg_{cg_id}"):
            st.session_state.selected_caregiver = cg_id
            st.rerun()
        st.divider()


# =====================================================================
# MAIN
# =====================================================================

init_session()

if not st.session_state.logged_in:
    login_page()
else:
    role = st.session_state.role
    if role == "Patient":
        patient_dashboard()
    elif role == "Caregiver":
        caregiver_dashboard()
    elif role == "Clinician":
        clinician_dashboard()
