import streamlit as st
import pandas as pd
import os


TASKS_FILE = 'Tasklist.csv'


def load_tasks():
    if os.path.exists(TASKS_FILE):
        tasks = pd.read_csv(TASKS_FILE)
        # Ensure 'Username' column exists
        if 'Username' not in tasks.columns:
            tasks['Username'] = ''
        return tasks
    else:
        return pd.DataFrame(columns=['Username', 'Company', 'Task', 'Status', 'Evidence', 'Rationale'])


def save_tasks(tasks):
    tasks.to_csv(TASKS_FILE, index=False)

# Load existing tasks from the file at the start
if 'tasks' not in st.session_state:
    st.session_state.tasks = load_tasks()

# Initialize session state for username and companies
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'companies' not in st.session_state:
    st.session_state.companies = []

# App Title
st.title("📝 ISO Task Management Application")

# Sidebar for Username Entry
st.sidebar.header("User Login")
username = st.sidebar.text_input("Enter your username:")

# Save the username in session state
if username:
    st.session_state.username = username

# Check if username is entered
if st.session_state.username:
    st.sidebar.success(f"Logged in as {st.session_state.username}")

    # Ensure 'Username' column exists in tasks
    if 'Username' not in st.session_state.tasks.columns:
        st.session_state.tasks['Username'] = ''

    # Filter tasks based on the logged-in username
    user_tasks = st.session_state.tasks[st.session_state.tasks['Username'] == st.session_state.username]

    # Sidebar for company selection
    st.sidebar.header("Company Selection")

    # Option to add a new company
    new_company = st.sidebar.text_input("Add New Company:")
    if new_company and st.sidebar.button("Add Company"):
        st.session_state.companies.append(new_company)
        st.success(f"Added {new_company} to the company list.")

    # Select existing company
    selected_company = st.sidebar.selectbox("Select Company:", st.session_state.companies)

    # Task Status Selection
    st.sidebar.header("Task Status")
    task_status = st.sidebar.selectbox("Select Task Status:", ["Pending", "Under Evaluation", "Completed"])

    if task_status == "Pending":
        st.header("Pending Tasks")
        st.info("Documents uploaded but analysis not initiated.")

        if selected_company:
            st.write(f"Selected Company: **{selected_company}**")

            # File uploader for pending tasks
            uploaded_file = st.file_uploader("Upload your document", type=["pdf", "docx", "xlsx", "csv", "txt"])

            if uploaded_file:
                new_task = pd.DataFrame({
                    'Username': [st.session_state.username],
                    'Company': [selected_company],
                    'Task': [f"Document upload by {st.session_state.username}"],
                    'Status': ['Pending'],
                    'Evidence': [None],
                    'Rationale': [None]
                })
                st.session_state.tasks = pd.concat([st.session_state.tasks, new_task], ignore_index=True)
                save_tasks(st.session_state.tasks)  # Save the updated tasks
                st.success(f"Document '{uploaded_file.name}' uploaded for {selected_company} and task marked as Pending.")

    elif task_status == "Under Evaluation":
        st.header("Tasks Under Evaluation")
        st.info("Tasks currently being evaluated.")

        # Display tasks under evaluation
        if not user_tasks.empty:
            under_eval_tasks = user_tasks[user_tasks['Status'] == 'Under Evaluation']
            st.write(under_eval_tasks)

            # Select a task to evaluate and mark as complete
            selected_task = st.selectbox("Select a task to evaluate:", under_eval_tasks['Company'].unique())
            if selected_task:
                st.subheader(f"Evaluation for {selected_task}")

                # Option to provide evidence and rationale
                evidence = st.text_area("Provide Evidence:")
                rationale = st.text_area("Provide Rationale:")

                # Button to mark the task as complete
                if st.button("Mark as Completed"):
                    st.session_state.tasks.loc[
                        (st.session_state.tasks['Username'] == st.session_state.username) &
                        (st.session_state.tasks['Company'] == selected_task) &
                        (st.session_state.tasks['Status'] == 'Under Evaluation'),
                        ['Evidence', 'Rationale', 'Status']
                    ] = [evidence, rationale, 'Completed']
                    save_tasks(st.session_state.tasks)  # Save the updated tasks
                    st.success(f"Task for {selected_task} has been marked as Completed.")

    elif task_status == "Completed":
        st.header("Completed Tasks")
        st.info("Review completed tasks.")

        # Filter and select completed tasks
        if not user_tasks.empty:
            completed_tasks = user_tasks[user_tasks['Status'] == 'Completed']
            selected_task = st.selectbox("Select a company to review:", completed_tasks['Company'].unique())

            if selected_task:
                st.subheader(f"Review for {selected_task}")

                # Tabbed layout for Fulfilled/Not Fulfilled
                tab1, tab2, tab3 = st.tabs(["Fulfilled", "Not Fulfilled", "Generate Questions"])

                with tab1:
                    st.subheader("Fulfilled Clauses")
                    fulfilled = completed_tasks[
                        (completed_tasks['Company'] == selected_task) & (completed_tasks['Evidence'].notnull())]
                    if not fulfilled.empty:
                        st.data_editor(fulfilled[['Task', 'Evidence', 'Rationale']], height=300, hide_columns=['Task'],
                                       disable_text_wrap=True)

                with tab2:
                    st.subheader("Not Fulfilled Clauses")
                    not_fulfilled = completed_tasks[
                        (completed_tasks['Company'] == selected_task) & (completed_tasks['Evidence'].isnull())]
                    if not not_fulfilled.empty:
                        st.data_editor(not_fulfilled[['Task', 'Evidence', 'Rationale']], height=300,
                                       hide_columns=['Task'], disable_text_wrap=True)

                with tab3:
                    st.subheader("Generate Questions")
                    st.write("This section will allow you to generate questions based on the selected task.")


    st.header("Task Status Overview")
    if not user_tasks.empty:
        st.write(user_tasks)
    else:
        st.info("No tasks to display.")

# About section in sidebar
st.sidebar.header("About")
st.sidebar.info(
    "This app allows users to manage and review ISO tasks based on their status (Pending, Under Evaluation, Completed). "
    "Select a task to review its fulfillment of ISO clauses or generate relevant questions."
)
