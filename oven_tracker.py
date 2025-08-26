import streamlit as st
import pandas as pd
from datetime import datetime
import os

DATA_FILE = "cylinders.csv"
EXPORT_FILE = "unloaded_cylinders.xlsx"

# Load existing data or create a new DataFrame
def load_data():
    try:
        df = pd.read_csv(DATA_FILE, parse_dates=["LoadTime", "UnloadTime"])
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            "OrderNumber", "CurrentID", "NeededID", "OvenNumber",
            "EstimatedDuration", "Operator", "Material", "Thickness",
            "LoadTime", "UnloadTime"
        ])
    return df

# Save data to CSV
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Unload a cylinder and export it
def unload_cylinder(index):
    df.loc[index, "UnloadTime"] = datetime.now()
    save_data(df)

    # Export all unloaded cylinders
    unloaded_df = df[df["UnloadTime"].notna()]
    unloaded_df.to_excel(EXPORT_FILE, index=False)

    st.rerun()

# Load the current data
df = load_data()

st.title("Cylinder Oven Tracker")

# ➕ Summary: Total count per oven
st.subheader("Oven Summary")
summary_df = df[df["UnloadTime"].isna()].groupby("OvenNumber").size().reset_index(name="Cylinders In Oven")
st.dataframe(summary_df, use_container_width=True)

# Show in-oven cylinders
in_oven_df = df[df["UnloadTime"].isna()]

if in_oven_df.empty:
    st.success("All cylinders have been unloaded")
else:
    st.subheader("Currently in the Oven")

    for i, row in in_oven_df.iterrows():
        elapsed_minutes = int((datetime.now() - row["LoadTime"]).total_seconds() / 60)
        overdue = elapsed_minutes > row["EstimatedDuration"]

        # Conditional color styling
        style = "background-color:#f20000; padding:10px; border-radius:5px;" if overdue else ""

        with st.container():
            st.markdown(f"""
                <div style="{style}">
                <b>Order:</b> {row['OrderNumber']} |
                <b>Current ID:</b> {row['CurrentID']} |
                <b>Needed ID:</b> {row['NeededID']} |
                <b>Oven:</b> {row['OvenNumber']} |
                <b>Material:</b> {row['Material']} |
                <b>Thickness:</b> {row['Thickness']}<br>
                <b>Loaded at:</b> {row['LoadTime'].strftime('%Y-%m-%d %H:%M:%S')} |
                <b>Elapsed:</b> {elapsed_minutes} min |
                <b>Estimate:</b> {row['EstimatedDuration']} min |
                <b>Operator:</b> {row['Operator']}<br>
                </div>
            """, unsafe_allow_html=True)
            st.button("Unload", key=f"unload_{i}", on_click=unload_cylinder, args=(i,))

st.divider()

# Cylinder entry form
with st.expander("➕ Add New Cylinder to Oven"):
    with st.form("add_form"):
        order_number = st.text_input("Order Number")
        current_id = st.text_input("Current Cylinder ID")
        needed_id = st.text_input("Needed Cylinder ID")

        # Oven dropdown
        oven_options = ["Oven 1", "Oven 2", "Oven 3"]
        oven_number = st.selectbox("Oven Number", oven_options)

        estimated_duration = st.number_input("Estimated Duration (minutes)", min_value=1, value=60)
        operator = st.text_input("Operator Name")

        # New fields
        material = st.text_input("Material")
        thickness = st.number_input("Thickness (mm)", min_value=0.0)

        submitted = st.form_submit_button("Add Cylinder")

        if submitted:
            if not all([order_number, current_id, needed_id, oven_number, operator, material]):
                st.error("⚠️ Please fill out all required fields.")
            else:
                new_entry = {
                    "OrderNumber": order_number,
                    "CurrentID": current_id,
                    "NeededID": needed_id,
                    "OvenNumber": oven_number,
                    "EstimatedDuration": estimated_duration,
                    "Operator": operator,
                    "Material": material,
                    "Thickness": thickness,
                    "LoadTime": datetime.now(),
                    "UnloadTime": pd.NaT
                }
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(df)
                st.success(f"✅ Cylinder {current_id} added to {oven_number}")
                st.rerun()

# Export download button (for all unloaded items)
if os.path.exists(EXPORT_FILE):
    with open(EXPORT_FILE, "rb") as f:
        st.download_button(
            label="⬇️ Download Unloaded Cylinders (Excel)",
            data=f,
            file_name="unloaded_cylinders.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
