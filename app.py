import streamlit as st
import oracledb
import pandas as pd

st.set_page_config(
    page_title="Student Analytics System",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Attendance and Performance Analytics")
st.write("Oracle Database Management System")

# Oracle connection
with st.sidebar:
    st.header("Oracle Connection")

    username = st.text_input("Username", value="SYSTEM")
    password = st.text_input("Password", type="password")

    if st.button("Connect"):
        try:
            conn = oracledb.connect(
                user=username,
                password=password,
                dsn="localhost:1521/XE"
            )
            st.session_state["conn"] = conn
            st.success("Connected successfully!")

        except Exception as e:
            st.error(str(e))

if "conn" not in st.session_state:
    st.info("Enter Oracle password and click Connect.")
    st.stop()

conn = st.session_state["conn"]

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Dashboard",
        "View Students",
        "Attendance",
        "Performance Report"
    ]
)

if menu == "Dashboard":

    st.subheader("Welcome to Student Analytics System")

    col1, col2, col3 = st.columns(3)

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Students")
    students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Attendance")
    attendance = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Marks")
    marks = cursor.fetchone()[0]

    col1.metric("Total Students", students)
    col2.metric("Attendance Records", attendance)
    col3.metric("Examination Records", marks)

    st.success("Your Student Analytics System is running!")

elif menu == "View Students":

    st.subheader("Student Details")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_id, student_name, course, email
        FROM Students
    """)

    rows = cursor.fetchall()

    st.dataframe(
        pd.DataFrame(
            rows,
            columns=["Student ID", "Name", "Course", "Email"]
        ),
        use_container_width=True
    )

elif menu == "Attendance":

    st.subheader("Mark Student Attendance")

    attendance_id = st.number_input(
        "Attendance ID", min_value=1, step=1
    )

    student_id = st.number_input(
        "Student ID", min_value=1, step=1
    )

    subject_id = st.number_input(
        "Subject ID", min_value=1, step=1
    )

    status = st.selectbox(
        "Attendance Status",
        ["PRESENT", "ABSENT"]
    )

    if st.button("Mark Attendance"):

        try:
            cursor = conn.cursor()

            cursor.callproc(
                "Mark_Attendance",
                [
                    int(attendance_id),
                    int(student_id),
                    int(subject_id),
                    status
                ]
            )

            st.success("Attendance recorded successfully!")

            cursor.close()

        except Exception as e:
            st.error(str(e))

elif menu == "Performance Report":

    st.subheader("Student Performance Report")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            s.student_name,
            sub.subject_name,
            m.exam_name,
            m.marks_obtained,
            m.total_marks,
            ROUND(
                m.marks_obtained / m.total_marks * 100,
                2
            ) AS percentage
        FROM Students s
        JOIN Marks m
            ON s.student_id = m.student_id
        JOIN Subjects sub
            ON m.subject_id = sub.subject_id
    """)

    rows = cursor.fetchall()

    st.dataframe(
        pd.DataFrame(
            rows,
            columns=[
                "Student",
                "Subject",
                "Exam",
                "Marks",
                "Total Marks",
                "Percentage"
            ]
        ),
        use_container_width=True
    )