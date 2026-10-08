import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from pathlib import Path
import uuid


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CONSTANTS
# =========================================================

DATA_FILE = Path("expenses.csv")

CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Education",
    "Bills",
    "Entertainment",
    "Health",
    "Other"
]

PAYMENT_METHODS = [
    "Cash",
    "UPI",
    "Debit Card",
    "Credit Card",
    "Bank Transfer"
]

COLUMNS = [
    "id",
    "date",
    "description",
    "amount",
    "category",
    "payment_method",
    "notes"
]


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f8f9fa;
}

[data-testid="stMetric"] {
    background-color: white;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

h1 {
    font-weight: 700;
}

h2 {
    font-weight: 600;
}

h3 {
    font-weight: 600;
}

.stButton > button {
    border-radius: 8px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# DATA FUNCTIONS
# =========================================================

def create_csv_file():
    """Create the CSV file if it does not exist."""

    if not DATA_FILE.exists():
        empty_data = pd.DataFrame(columns=COLUMNS)
        empty_data.to_csv(DATA_FILE, index=False)


def load_expenses():
    """Load expenses from CSV file."""

    create_csv_file()

    try:
        df = pd.read_csv(DATA_FILE)

    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=COLUMNS)

    # Make sure all required columns exist
    for column in COLUMNS:
        if column not in df.columns:
            df[column] = ""

    df = df[COLUMNS]

    if not df.empty:

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        df["amount"] = pd.to_numeric(
            df["amount"],
            errors="coerce"
        ).fillna(0)

    return df


def save_expenses(df):
    """Save expenses to CSV."""

    df.to_csv(
        DATA_FILE,
        index=False
    )


def add_expense(
    expense_date,
    description,
    amount,
    category,
    payment_method,
    notes
):
    """Add a new expense."""

    df = load_expenses()

    new_expense = pd.DataFrame([
        {
            "id": str(uuid.uuid4()),
            "date": expense_date,
            "description": description.strip(),
            "amount": float(amount),
            "category": category,
            "payment_method": payment_method,
            "notes": notes.strip()
        }
    ])

    df = pd.concat(
        [df, new_expense],
        ignore_index=True
    )

    save_expenses(df)


def delete_expense(expense_id):
    """Delete one expense."""

    df = load_expenses()

    df = df[
        df["id"].astype(str) != str(expense_id)
    ]

    save_expenses(df)


def delete_all_expenses():
    """Delete all expenses."""

    empty_data = pd.DataFrame(
        columns=COLUMNS
    )

    save_expenses(empty_data)


def format_money(amount):
    """Format amount using Indian Rupee."""

    return f"₹{amount:,.2f}"


def get_current_month_expenses(df):
    """Get expenses from the current month."""

    if df.empty:
        return df.copy()

    today = pd.Timestamp.today()

    return df[
        (df["date"].dt.year == today.year)
        &
        (df["date"].dt.month == today.month)
    ].copy()


# =========================================================
# LOAD DATA
# =========================================================

if "expenses" not in st.session_state:

    st.session_state.expenses = load_expenses()


if "monthly_budget" not in st.session_state:

    st.session_state.monthly_budget = 10000.0


df = st.session_state.expenses.copy()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("💰 Expense Tracker")

st.sidebar.write(
    "Manage your personal expenses easily."
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "➕ Add Expense",
        "📜 Expense History",
        "📈 Analysis",
        "💰 Budget"
    ]
)

st.sidebar.divider()


# =========================================================
# REFRESH BUTTON
# =========================================================

if st.sidebar.button(
    "🔄 Refresh Data",
    use_container_width=True
):

    st.session_state.expenses = load_expenses()

    st.rerun()


# =========================================================
# DOWNLOAD BUTTON
# =========================================================

download_data = load_expenses()

csv_data = download_data.to_csv(
    index=False
).encode("utf-8")

st.sidebar.download_button(
    label="⬇️ Download Expense CSV",
    data=csv_data,
    file_name="expenses.csv",
    mime="text/csv",
    use_container_width=True
)


st.sidebar.divider()

st.sidebar.info(
    "Your expenses are stored locally in expenses.csv"
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "📊 Dashboard":

    st.title("📊 Expense Dashboard")

    st.write(
        "Welcome to your Personal Expense Tracker!"
    )

    st.divider()

    # Calculate dashboard values

    total_expenses = (
        df["amount"].sum()
        if not df.empty
        else 0
    )

    transaction_count = len(df)

    highest_expense = (
        df["amount"].max()
        if not df.empty
        else 0
    )

    average_expense = (
        df["amount"].mean()
        if not df.empty
        else 0
    )

    # Dashboard cards

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💸 Total Expenses",
        format_money(total_expenses)
    )

    col2.metric(
        "🧾 Transactions",
        transaction_count
    )

    col3.metric(
        "📈 Highest Expense",
        format_money(highest_expense)
    )

    col4.metric(
        "📊 Average Expense",
        format_money(average_expense)
    )

    st.divider()

    # Recent expenses

    if df.empty:

        st.info(
            "No expenses yet. "
            "Go to 'Add Expense' to add your first expense."
        )

    else:

        st.subheader("🕒 Recent Expenses")

        recent = df.sort_values(
            "date",
            ascending=False
        ).head(5)

        recent_display = recent[
            [
                "date",
                "description",
                "category",
                "amount",
                "payment_method"
            ]
        ].copy()

        recent_display["date"] = (
            recent_display["date"]
            .dt.strftime("%d-%m-%Y")
        )

        recent_display["amount"] = (
            recent_display["amount"]
            .apply(format_money)
        )

        st.dataframe(
            recent_display,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # Category pie chart

        st.subheader(
            "🍕 Spending by Category"
        )

        category_data = (
            df.groupby(
                "category",
                as_index=False
            )["amount"]
            .sum()
            .sort_values(
                "amount",
                ascending=False
            )
        )

        category_chart = px.pie(
            category_data,
            names="category",
            values="amount",
            hole=0.35,
            title="Category-wise Expenses"
        )

        st.plotly_chart(
            category_chart,
            use_container_width=True
        )


# =========================================================
# ADD EXPENSE
# =========================================================

elif page == "➕ Add Expense":

    st.title("➕ Add New Expense")

    st.write(
        "Enter the details of your expense."
    )

    st.divider()

    with st.form(
        "expense_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)

        # -----------------------------------------
        # LEFT SIDE
        # -----------------------------------------

        with col1:

            expense_date = st.date_input(
                "📅 Date *",
                value=date.today()
            )

            description = st.text_input(
                "📝 Expense Title / Description *",
                placeholder="Example: Lunch at college"
            )

            amount = st.number_input(
                "💵 Amount (₹) *",
                min_value=0.0,
                value=0.0,
                step=10.0,
                format="%.2f"
            )

            category = st.selectbox(
                "📂 Category",
                CATEGORIES
            )

        # -----------------------------------------
        # RIGHT SIDE
        # -----------------------------------------

        with col2:

            payment_method = st.selectbox(
                "💳 Payment Method",
                PAYMENT_METHODS
            )

            notes = st.text_area(
                "📌 Notes (Optional)",
                placeholder="Add additional information..."
            )

        submitted = st.form_submit_button(
            "💾 Save Expense",
            use_container_width=True
        )

    # ---------------------------------------------
    # VALIDATION
    # ---------------------------------------------

    if submitted:

        if expense_date is None:

            st.error(
                "❌ Please select a date."
            )

        elif not description.strip():

            st.error(
                "❌ Expense description cannot be empty."
            )

        elif amount <= 0:

            st.error(
                "❌ Amount must be greater than ₹0."
            )

        else:

            add_expense(
                expense_date,
                description,
                amount,
                category,
                payment_method,
                notes
            )

            st.session_state.expenses = (
                load_expenses()
            )

            st.success(
                "✅ Expense added successfully!"
            )

            st.rerun()


# =========================================================
# EXPENSE HISTORY
# =========================================================

elif page == "📜 Expense History":

    st.title("📜 Expense History")

    st.write(
        "Search, filter and manage your expenses."
    )

    st.divider()

    if df.empty:

        st.info(
            "No expenses available yet."
        )

    else:

        # ---------------------------------------------
        # SEARCH
        # ---------------------------------------------

        search = st.text_input(
            "🔎 Search Expenses",
            placeholder=(
                "Search description, category, "
                "payment method or notes..."
            )
        )

        # ---------------------------------------------
        # FILTERS
        # ---------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            selected_categories = st.multiselect(
                "📂 Category",
                CATEGORIES
            )

        with col2:

            minimum_date = (
                df["date"]
                .min()
                .date()
            )

            maximum_date = (
                df["date"]
                .max()
                .date()
            )

            start_date = st.date_input(
                "📅 From Date",
                value=minimum_date
            )

        with col3:

            end_date = st.date_input(
                "📅 To Date",
                value=maximum_date
            )

        filtered = df.copy()

        # ---------------------------------------------
        # SEARCH FILTER
        # ---------------------------------------------

        if search.strip():

            search_text = (
                search.strip()
                .lower()
            )

            searchable_text = (
                filtered["description"]
                .fillna("")
                .astype(str)
                + " "
                +
                filtered["category"]
                .fillna("")
                .astype(str)
                + " "
                +
                filtered["payment_method"]
                .fillna("")
                .astype(str)
                + " "
                +
                filtered["notes"]
                .fillna("")
                .astype(str)
            ).str.lower()

            filtered = filtered[
                searchable_text.str.contains(
                    search_text,
                    na=False
                )
            ]

        # ---------------------------------------------
        # CATEGORY FILTER
        # ---------------------------------------------

        if selected_categories:

            filtered = filtered[
                filtered["category"]
                .isin(selected_categories)
            ]

        # ---------------------------------------------
        # DATE FILTER
        # ---------------------------------------------

        if start_date > end_date:

            st.error(
                "❌ From Date cannot be after To Date."
            )

        else:

            filtered = filtered[
                (filtered["date"].dt.date >= start_date)
                &
                (filtered["date"].dt.date <= end_date)
            ]

            # Newest first

            filtered = filtered.sort_values(
                "date",
                ascending=False
            )

            st.write(
                f"Showing **{len(filtered)}** transaction(s)."
            )

            # -----------------------------------------
            # DISPLAY TABLE
            # -----------------------------------------

            if filtered.empty:

                st.warning(
                    "No expenses match your filters."
                )

            else:

                display_df = filtered[
                    [
                        "date",
                        "description",
                        "category",
                        "amount",
                        "payment_method",
                        "notes"
                    ]
                ].copy()

                display_df["date"] = (
                    display_df["date"]
                    .dt.strftime("%d-%m-%Y")
                )

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "amount": st.column_config.NumberColumn(
                            "Amount",
                            format="₹%.2f"
                        )
                    }
                )

                # -----------------------------------------
                # DELETE SECTION
                # -----------------------------------------

                st.divider()

                st.subheader(
                    "🗑️ Delete an Expense"
                )

                for _, row in filtered.iterrows():

                    col1, col2, col3, col4 = (
                        st.columns(
                            [2, 4, 2, 1]
                        )
                    )

                    with col1:

                        st.write(
                            row["date"]
                            .strftime("%d-%m-%Y")
                        )

                    with col2:

                        st.write(
                            f"**{row['description']}**"
                        )

                        st.caption(
                            f"{row['category']} • "
                            f"{format_money(row['amount'])}"
                        )

                    with col3:

                        st.write(
                            row["payment_method"]
                        )

                    with col4:

                        if st.button(
                            "🗑️",
                            key=f"delete_{row['id']}",
                            help="Delete this expense"
                        ):

                            delete_expense(
                                row["id"]
                            )

                            st.session_state.expenses = (
                                load_expenses()
                            )

                            st.success(
                                "Expense deleted."
                            )

                            st.rerun()

    # =====================================================
    # CLEAR ALL EXPENSES
    # =====================================================

    st.divider()

    st.subheader(
        "⚠️ Clear All Expenses"
    )

    confirm_delete = st.checkbox(
        "I understand that this will permanently delete all expenses."
    )

    if st.button(
        "🗑️ Clear All Expenses",
        disabled=not confirm_delete
    ):

        delete_all_expenses()

        st.session_state.expenses = (
            load_expenses()
        )

        st.success(
            "All expenses have been deleted."
        )

        st.rerun()


# =========================================================
# ANALYSIS
# =========================================================

elif page == "📈 Analysis":

    st.title("📈 Expense Analysis")

    st.write(
        "Analyze where your money is being spent."
    )

    st.divider()

    if df.empty:

        st.info(
            "Add some expenses first to see the analysis."
        )

    else:

        # ---------------------------------------------
        # CATEGORY DATA
        # ---------------------------------------------

        category_data = (
            df.groupby(
                "category",
                as_index=False
            )["amount"]
            .sum()
            .sort_values(
                "amount",
                ascending=False
            )
        )

        # ---------------------------------------------
        # PAYMENT DATA
        # ---------------------------------------------

        payment_data = (
            df.groupby(
                "payment_method",
                as_index=False
            )["amount"]
            .sum()
            .sort_values(
                "amount",
                ascending=False
            )
        )

        # ---------------------------------------------
        # MONTHLY DATA
        # ---------------------------------------------

        monthly_df = df.copy()

        monthly_df["month"] = (
            monthly_df["date"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly_data = (
            monthly_df.groupby(
                "month",
                as_index=False
            )["amount"]
            .sum()
        )

        # =================================================
        # CATEGORY PIE CHART
        # =================================================

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "🍕 Category-wise Spending"
            )

            category_chart = px.pie(
                category_data,
                names="category",
                values="amount",
                hole=0.35
            )

            st.plotly_chart(
                category_chart,
                use_container_width=True
            )

        # =================================================
        # PAYMENT METHOD BAR CHART
        # =================================================

        with col2:

            st.subheader(
                "💳 Payment Method Spending"
            )

            payment_chart = px.bar(
                payment_data,
                x="payment_method",
                y="amount",
                text_auto=".2f"
            )

            payment_chart.update_layout(
                xaxis_title="Payment Method",
                yaxis_title="Amount (₹)"
            )

            st.plotly_chart(
                payment_chart,
                use_container_width=True
            )

        # =================================================
        # MONTHLY BAR CHART
        # =================================================

        st.subheader(
            "📅 Monthly Spending"
        )

        monthly_chart = px.bar(
            monthly_data,
            x="month",
            y="amount",
            text_auto=".2f"
        )

        monthly_chart.update_layout(
            xaxis_title="Month",
            yaxis_title="Amount (₹)"
        )

        st.plotly_chart(
            monthly_chart,
            use_container_width=True
        )

        # =================================================
        # CATEGORY SUMMARY
        # =================================================

        st.subheader(
            "📋 Category Summary"
        )

        summary = category_data.copy()

        summary["amount"] = (
            summary["amount"]
            .apply(format_money)
        )

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# BUDGET
# =========================================================

elif page == "💰 Budget":

    st.title("💰 Monthly Budget")

    st.write(
        "Set your monthly budget and monitor your spending."
    )

    st.divider()

    # ---------------------------------------------
    # CURRENT MONTH EXPENSES
    # ---------------------------------------------

    current_month = (
        get_current_month_expenses(df)
    )

    amount_spent = (
        current_month["amount"].sum()
        if not current_month.empty
        else 0
    )

    # ---------------------------------------------
    # SET BUDGET
    # ---------------------------------------------

    st.subheader(
        "🎯 Set Your Monthly Budget"
    )

    budget = st.number_input(
        "Monthly Budget (₹)",
        min_value=0.0,
        value=float(
            st.session_state.monthly_budget
        ),
        step=500.0,
        format="%.2f"
    )

    if st.button(
        "💾 Save Budget",
        use_container_width=True
    ):

        if budget <= 0:

            st.error(
                "❌ Budget must be greater than ₹0."
            )

        else:

            st.session_state.monthly_budget = (
                budget
            )

            st.success(
                "✅ Monthly budget saved."
            )

            st.rerun()

    # ---------------------------------------------
    # BUDGET CALCULATIONS
    # ---------------------------------------------

    monthly_budget = (
        st.session_state.monthly_budget
    )

    remaining = (
        monthly_budget - amount_spent
    )

    if monthly_budget > 0:

        percentage_used = (
            amount_spent
            / monthly_budget
            * 100
        )

    else:

        percentage_used = 0

    st.divider()

    # ---------------------------------------------
    # BUDGET METRICS
    # ---------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💰 Monthly Budget",
        format_money(monthly_budget)
    )

    col2.metric(
        "💸 Amount Spent",
        format_money(amount_spent)
    )

    if remaining >= 0:

        col3.metric(
            "🟢 Remaining",
            format_money(remaining)
        )

    else:

        col3.metric(
            "🔴 Over Budget",
            format_money(abs(remaining))
        )

    col4.metric(
        "📊 Budget Used",
        f"{percentage_used:.1f}%"
    )

    st.divider()

    # ---------------------------------------------
    # PROGRESS BAR
    # ---------------------------------------------

    progress = min(
        percentage_used / 100,
        1.0
    )

    st.progress(
        progress,
        text=(
            f"{percentage_used:.1f}% "
            "of your budget used"
        )
    )

    st.divider()

    # ---------------------------------------------
    # BUDGET ALERTS
    # ---------------------------------------------

    if percentage_used >= 100:

        st.error(
            f"🚨 Budget exceeded by "
            f"{format_money(abs(remaining))}!"
        )

    elif percentage_used >= 80:

        st.warning(
            f"⚠️ You have used "
            f"{percentage_used:.1f}% of your budget. "
            f"Only {format_money(remaining)} remains."
        )

    elif percentage_used >= 60:

        st.info(
            f"ℹ️ You have used "
            f"{percentage_used:.1f}% of your budget."
        )

    else:

        st.success(
            f"✅ You are within your budget. "
            f"{format_money(remaining)} remains."
        )

    st.caption(
        "Budget spending is calculated using "
        "expenses from the current calendar month."
    )