import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Healthcare Mobility Monitoring", layout="wide")

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


@st.cache_data
def generate_patient_data(patient_id: str):
    np.random.seed(hash(patient_id) % 2**31)
    today = datetime.date.today()
    dates_7 = pd.date_range(end=today, periods=7)
    dates_30 = pd.date_range(end=today, periods=30)

    daily = pd.DataFrame({
        "Date": dates_7,
        "Tremor_Intensity": np.random.uniform(0.1, 0.9, 7).round(2),
        "Tapping_Velocity": np.random.uniform(1.0, 3.0, 7).round(2),
        "MDS_UPDRS_Score": np.random.randint(1, 4, 7),
        "Sitting_Duration_hrs": np.random.uniform(1.5, 4.0, 7).round(1),
    })

    weekly = pd.DataFrame({
        "Date": dates_30,
        "Tremor_Intensity": np.random.uniform(0.1, 0.9, 30).round(2),
        "Tapping_Velocity": np.random.uniform(1.0, 3.0, 30).round(2),
        "MDS_UPDRS_Score": np.random.randint(1, 4, 30),
        "Sitting_Duration_hrs": np.random.uniform(1.5, 4.0, 30).round(1),
    })

    return daily, weekly


def get_daily_goals(patient_id: str):
    return [
        {"Goal": "Keep tremor intensity below 0.6", "Target": 0.6, "Type": "Tremor_Intensity"},
        {"Goal": "Maintain tapping velocity ≥ 1.5 reps/s", "Target": 1.5, "Type": "Tapping_Velocity"},
        {"Goal": "Sit < 2.5 hrs continuously", "Target": 2.5, "Type": "Sitting_Duration_hrs"},
    ]


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

def render_daily_report(patient_id: str):
    daily, _ = generate_patient_data(patient_id)
    today = daily.iloc[-1]
    st.subheader("📋 Daily Report")
    c1, c2, c3 = st.columns(3)
    c1.metric("Tremor Intensity", f"{today['Tremor_Intensity']:.2f}")
    c2.metric("Tapping Velocity", f"{today['Tapping_Velocity']:.1f} reps/s")
    c3.metric("Sitting Duration", f"{today['Sitting_Duration_hrs']:.1f} hrs")

    st.markdown("**Today's Sensor Readings**")
    st.dataframe(pd.DataFrame({
        "Time": ["08:00 AM", "10:00 AM", "12:00 PM", "02:00 PM", "04:00 PM"],
        "Event": ["Tremor Check", "Tapping Assessment", "Sitting Detected",
                   "Tremor Check", "Tapping Assessment"],
        "Status": ["Normal", "Normal", "Prolonged Sitting", "Normal", "Normal"],
    }), width="stretch")


def render_weekly_report(patient_id: str):
    _, weekly = generate_patient_data(patient_id)
    st.subheader("📊 Weekly Report (Last 30 Days)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Tremor Intensity Trend**")
        st.line_chart(weekly.set_index("Date")["Tremor_Intensity"])
    with col2:
        st.markdown("**Tapping Velocity**")
        st.bar_chart(weekly.set_index("Date")["Tapping_Velocity"])

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Sitting Duration (hrs)**")
        st.line_chart(weekly.set_index("Date")["Sitting_Duration_hrs"])
    with col4:
        st.markdown("**MDS-UPDRS Score**")
        st.bar_chart(weekly.set_index("Date")["MDS_UPDRS_Score"])


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
    daily, weekly = generate_patient_data(patient_id)
    csv = weekly.to_csv(index=False).encode("utf-8")
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
    daily, _ = generate_patient_data(uid)
    today = daily.iloc[-1]

    st.sidebar.title(f"👤 {name}")
    st.sidebar.caption(f"Patient ID: {uid}")
    if st.sidebar.button("Logout"):
        do_logout()
        st.rerun()

    menu = st.sidebar.radio("Navigation",
                            ["Home", "Daily Goals", "Daily Report",
                             "Weekly Report", "Alerts", "Doctor Feedback",
                             "Download Report"])

    # --- HOME ---
    if menu == "Home":
        st.markdown(f"<h1 style='text-align:center;'>Welcome, {name}!</h1>",
                    unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center;'>Your daily mobility summary</h3>",
                    unsafe_allow_html=True)
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Tremor Level", f"{today['Tremor_Intensity']:.2f}", "Stable")
        c2.metric("Tapping Activity", f"{today['Tapping_Velocity']:.1f} reps/s")
        c3.metric("Sitting Duration", f"{today['Sitting_Duration_hrs']:.1f} hrs")

        if today["Sitting_Duration_hrs"] > 2.0:
            st.warning("⏱️ You have been sitting for over 2 hours. Time for a stretch!")
        if today["Tremor_Intensity"] < 0.6:
            st.success("🏆 Great! Your tremor levels are within the target range today.")

    # --- DAILY GOALS ---
    elif menu == "Daily Goals":
        st.title("🎯 Daily Goals")
        goals = get_daily_goals(uid)
        for g in goals:
            col_a, col_b = st.columns([3, 1])
            actual = today.get(g["Type"], 0)
            target = g["Target"]
            if g["Type"] in ("Sitting_Duration_hrs", "Tremor_Intensity"):
                met = actual <= target
            else:
                met = actual >= target
            col_a.markdown(f"**{g['Goal']}**")
            if met:
                col_b.success("✅ Achieved")
            else:
                col_b.warning("❌ Not yet")

        st.divider()
        st.markdown("**Sensor Metrics Progress**")
        progress_data = pd.DataFrame({
            "Metric": ["Tremor Intensity", "Tapping Velocity (reps/s)", "Sitting (hrs)"],
            "Actual": [round(today["Tremor_Intensity"], 2),
                       round(today["Tapping_Velocity"], 2),
                       round(today["Sitting_Duration_hrs"], 1)],
            "Target": [0.6, 1.5, 2.5],
        })
        st.dataframe(progress_data, width="stretch")

    # --- DAILY REPORT ---
    elif menu == "Daily Report":
        render_daily_report(uid)

    # --- WEEKLY REPORT ---
    elif menu == "Weekly Report":
        render_weekly_report(uid)

    # --- ALERTS ---
    elif menu == "Alerts":
        render_alerts(uid)

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

    # --- DOWNLOAD REPORT ---
    elif menu == "Download Report":
        st.title("📥 Download Your Report")
        render_download_button(uid)


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
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["Daily Report", "Weekly Report", "Alerts", "Feedback", "Download"])

        with tab1:
            render_daily_report(pid)
        with tab2:
            render_weekly_report(pid)
        with tab3:
            render_alerts(pid)
        with tab4:
            render_send_feedback(uid, pid, label="patient")
        with tab5:
            render_download_button(pid)
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
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["Daily Report", "Weekly Report", "Alerts", "Feedback", "Download"])
        with tab1:
            render_daily_report(pid)
        with tab2:
            render_weekly_report(pid)
        with tab3:
            render_alerts(pid)
        with tab4:
            render_send_feedback(uid, pid, label="patient")
            # Also allow feedback to the caregiver of this patient
            cg_id = USERS[pid].get("caregiver")
            if cg_id:
                render_send_feedback(uid, cg_id, label="caregiver")
        with tab5:
            render_download_button(pid)
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