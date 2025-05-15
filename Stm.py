import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import numpy as np

# Set page config
st.set_page_config(
    page_title="Farm Water Level Analysis",
    page_icon="😇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
    <style>
        .main {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .sidebar .sidebar-content {
            padding: 2rem 1rem;
        }
        h1 {
            color: #1f77b4;
        }
        .stButton>button {
            background-color: #1f77b4;
            color: white;
        }
        .stDownloadButton>button {
            background-color: #2ca02c;
            color: white;
        }
        .stFileUploader>div>div>div>div {
            color: #1f77b4;
        }
        .plot-container {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 1rem;
            margin-bottom: 2rem;
        }
        .stMultiSelect [data-baseweb=tag] {
            background-color: #1f77b4;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# App title
st.title("Farm Water Level Analysis")
st.markdown("Analyze water level measurements across different farms and pipes.")

# Initialize session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'farm_list' not in st.session_state:
    st.session_state.farm_list = []
if 'water_levels' not in st.session_state:
    st.session_state.water_levels = None

# Function to process water level data
def extract_pipe_code(col_name, pipe_codes):
    for code in pipe_codes:
        if code.lower() in col_name.lower():
            return code
    return col_name

def process_water_level_data(water_file_path, pipe_codes):
    """Process water level data and extract the relevant information"""
    try:
        # Load the CSV file
        df = pd.read_csv(water_file_path)

        # Filter relevant columns (Dates & Water Levels)
        cols_to_keep = []

        for i, col in enumerate(df.columns):
            if "Date" in col:
                cols_to_keep.append(col)
            if "Water level in pipe from bottom up" in col:
                cols_to_keep.append(col)
            if i > 0 and "Water level" in df.columns[i]:
                cols_to_keep.append(df.columns[i - 1])  # Include location or pipe code info

        df_filtered = df[cols_to_keep]

        # Rename water level columns to include pipe code
        for i, col in enumerate(df_filtered.columns[:-1]):
            if "Water level in pipe from bottom up - in millimeter" in col:
                next_col = df_filtered.columns[i + 1]
                df_filtered.columns.values[i] = next_col + " Water level in pipe from bottom up - in millimeter"

        # Keep only Date & Water level columns
        final_cols_to_keep = []

        for col in df_filtered.columns:
            if "Date" in col or "Water level in pipe from bottom up" in col:
                final_cols_to_keep.append(col)

        df_final = df_filtered[final_cols_to_keep]

        # Rename water level columns using pipe codes
        df_final.columns = [extract_pipe_code(col, pipe_codes) for col in df_final.columns]

        return df_final
    except Exception as e:
        st.error(f"Error processing water level data: {str(e)}")
        return None

# Main processing function
def process_data(farm_file, water_file):
    try:
        # Manually listed pipe codes
        pipe_codes = [
            "gurinder_1", "raghbir_2", "RAGHBIR_1", "Gurinder_2", "Gurdeep_1", "Gurdeep_2",
            "Gurdeep_3", "Gurdeep_4", "Gurkirat_1", "Gurwinder_4", "Satpal_1", "Gurtej_1",
            "Tarsem_2", "lakh_1", "sukh_1", "SATWI_1", "Jasmail_1", "manjeet_1", "MANGA_1",
            "MANGA_2", "PARMI_1", "Gurkirat_4", "Tarsem_1", "GURIN_1", "PARWI_1", "MANDE_1",
            "Rimp_01", "SANDE_1", "Varinder_1", "Gurkirat_2", "varinder_02", "Gurkirat_3",
            "jasmail_2", "Baljinder_1", "Mand_1", "Bhupinder_1", "Sandeep_1", "Hira_1",
            "RAMP_1", "TAHI_1", "PARG_1", "GURS_1", "GURD_1", "MAND_2", "Sahi_1",
            "Harwinder_1", "Bablu_1", "Kulwinder_1", "sarb_1", "Kulwinder_2", "Nirmal_1",
            "sarab_2", "Jaspal_1", "Jaspal_2", "Jaspal_3", "paramjit_1", "Yadwinder_1",
            "Charan_1", "Sarb_3", "Pragh_1", "NAIB_1", "Manin_1", "Iqbal_1", "Nazar_1",
            "Surjit_2", "Surjit_1", "Suri_1", "Sarab_4", "Gurwinder_3", "Gurwinder_2",
            "Gurwinder_1", "Pardeep_1", "Jasveer_3", "Jasveer_2", "Jasveer_1", "Hardeep_1",
            "Harinder_2", "Balkar_2", "BALKAR_1", "Nirbhah_1", "Jasveer_4", "Harpreet_1",
            "Newhardeep_2", "Newhardeep_3", "Balbir_1", "Pardeep_2", "Pardeep_6", "Pardeep_3",
            "Pardeep_4", "Pardeep_5", "Hardeep_3", "Jasveer_6", "Balkar_3", "Raj_1",
            "Newhardeep_1", "Harinder_1", "Harjit_1", "Jasveer_5", "Harpreet_2", "Jasveer_7",
            "Bharpur_1", "Jagd_1", "Hard_12", "Gaga_1", "Jagt_1", "Ram_1", "Satn_1",
            "Simr_1", "Hardeep_4", "Theru_1", "Theru_2", "balwin_1", "Navjot_1", "Navjot_2",
            "Navjot_3", "Karnail_1", "Gurpreet_1", "Rupinder_1", "Dhupinder_1", "Pritpal_1",
            "Navjot_4", "Navjot_5", "Amrik_2", "Amrik_3", "Amrik_1", "Avtar_1", "Avtar_2",
            "Daljinder_1", "Jagtar_1", "Daljinder_3", "Daljinder_5", "Daljinder_4",
            "avatar_1", "avatar_3", "avatar_2", "avatar_4", "Daljinder_2", "Harpal_2",
            "Harpal_4", "harpal_1", "avtar_12", "avtar_11", "Avtar_13", "Gurdarshan_3",
            "gurdarshan_2", "gurdarshan_1", "mukhtiar_2", "Mukhtiar_1", "Mukhtair_3",
            "Sukhwant_1", "Amrinder_1", "Sukhwinder_2", "Sukhwant_3", "Harjinder_2",
            "Harjinder_1", "Kuldeep_1", "Kuldeep_2", "Gurnam_1", "gurna_2", "Didar_1",
            "Didar_2", "Didar_3", "JAGTAR_1", "Chamkaur_1", "sharn_1", "netar_1", "Sukh_1",
            "Jasp_1", "Jasw_1", "Gurd_1", "harb_1", "Raghuveer_1", "Raghuveer_2",
            "Raghuveer_3", "Jaswinder_1", "Jaswinder_2", "Jaswinder_5", "Lal_1", "Lal_2",
            "Harwinder_02", "Amar_2", "Amar_1", "hardeep_10", "RAN_1", "RANJIT_1",
            "NAHAR_1", "jager_1", "jagdeep_1", "surjit_3", "sukh_2", "karam_1", "bhag_1",
            "PARA_1", "paver_1", "vash_1", "Satnam_1", "Satnam_2", "Satnam_4", "SATNAM_3",
            "Satnam_5", "Darshan_1", "Hakam_1", "Ogar_1", "satnam_1", "malkeet_1",
            "Avatar_1", "Gamdoor_1", "harinder_1"
        ]

        # Process water level data
        water_df = process_water_level_data(water_file, pipe_codes)
        if water_df is None:
            return None

        # Extract Date column
        date_col = [col for col in water_df.columns if "Date" in col][0]

        # Set date column as index for transposition
        water_df.set_index(date_col, inplace=True)

        # Transpose water_df: rows become pipes, columns become dates
        transposed = water_df.transpose()
        transposed.reset_index(inplace=True)
        transposed.rename(columns={'index': 'Pipe Code'}, inplace=True)

        # Load farm info from Excel sheets
        excel_file = pd.ExcelFile(farm_file)

        # Load sheets with explicit column specification
        pvc_pipes_kharif = pd.read_excel(excel_file, sheet_name='PVC Pipes Kharif24')
        kharif_2024 = pd.read_excel(excel_file, sheet_name='Kharif 2024')

        # Find sowing date column
        sowing_column = "Kharif 24 Paddy sowing (DSR)"
        if sowing_column not in kharif_2024.columns:
            possible_matches = [col for col in kharif_2024.columns if "sowing" in col.lower() or "dsr" in col.lower()]
            if possible_matches:
                sowing_column = possible_matches[0]
            else:
                st.warning("Could not find sowing date column in Kharif 2024 sheet")
                return None

        # Find farm ID columns
        farm_id_col_pvc = "Farm ID Kharif 24"
        if farm_id_col_pvc not in pvc_pipes_kharif.columns:
            possible_matches = [col for col in pvc_pipes_kharif.columns if "farm" in col.lower() and "id" in col.lower()]
            if possible_matches:
                farm_id_col_pvc = possible_matches[0]
            else:
                st.warning("Could not find farm ID column in PVC Pipes sheet")
                return None

        farm_id_col_kharif = "Kharif 24 FarmID"
        if farm_id_col_kharif not in kharif_2024.columns:
            possible_matches = [col for col in kharif_2024.columns if "farm" in col.lower() and "id" in col.lower()]
            if possible_matches:
                farm_id_col_kharif = possible_matches[0]
            else:
                st.warning("Could not find farm ID column in Kharif 2024 sheet")
                return None

        # Find pipe code column
        pipe_code_col = "Pipe Code Kharif 24"
        if pipe_code_col not in pvc_pipes_kharif.columns:
            possible_matches = [col for col in pvc_pipes_kharif.columns if "pipe" in col.lower() and "code" in col.lower()]
            if possible_matches:
                pipe_code_col = possible_matches[0]
            else:
                st.warning("Could not find pipe code column in PVC Pipes sheet")
                return None

        # Ensure consistent column naming for merging
        pvc_pipes_kharif = pvc_pipes_kharif.rename(columns={farm_id_col_pvc: 'Kharif 24 FarmID'})
        kharif_2024 = kharif_2024.rename(columns={farm_id_col_kharif: 'Kharif 24 FarmID'})

        # Merge farm info and sowing data
        kharif_subset = kharif_2024[['Kharif 24 FarmID', sowing_column]].copy()

        # Merge with pipe data
        merged_data = pd.merge(
            pvc_pipes_kharif,
            kharif_subset,
            on='Kharif 24 FarmID',
            how='left'
        )

        # Standardize pipe codes for merging
        merged_data[pipe_code_col] = merged_data[pipe_code_col].astype(str).str.strip().str.lower()
        transposed['Pipe Code'] = transposed['Pipe Code'].astype(str).str.strip().str.lower()

        # Merge on Pipe Code
        final_df = pd.merge(
            transposed,
            merged_data[['Kharif 24 FarmID', 'Village', sowing_column, pipe_code_col]],
            left_on='Pipe Code',
            right_on=pipe_code_col,
            how='inner'
        )

        # Rename columns for clarity
        final_df.rename(columns={
            'Kharif 24 FarmID': 'Farm ID',
            'Village': 'Location',
            sowing_column: 'Date of Sowing',
        }, inplace=True)

        # Convert sowing dates
        date_formats = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']
        for fmt in date_formats:
            try:
                final_df['Date of Sowing'] = pd.to_datetime(final_df['Date of Sowing'], format=fmt, errors='coerce')
                break
            except (ValueError, TypeError):
                continue

        # If all formats failed, try pandas auto-detection
        if not pd.api.types.is_datetime64_dtype(final_df['Date of Sowing']):
            final_df['Date of Sowing'] = pd.to_datetime(final_df['Date of Sowing'], errors='coerce')

        # Fill any missing dates with default
        default_date = pd.to_datetime("16/06/2024", format="%d/%m/%Y")
        final_df['Date of Sowing'].fillna(default_date, inplace=True)

        # Normalize columns (handle duplicate column names)
        normalized_columns = final_df.columns.to_series().apply(lambda x: x.split('.')[0])
        merged_df = pd.DataFrame()

        for col in normalized_columns.unique():
            matching_cols = final_df.loc[:, normalized_columns == col]
            merged_df[col] = matching_cols.bfill(axis=1).iloc[:, 0]

        return merged_df

    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return None

# Function to plot farm data
def plot_farm_data(selected_farm, df, selected_pipes=None, show_weekly=False):
    # Filter data for selected farm
    farm_data = df[df['Farm ID'] == selected_farm]

    if farm_data.empty:
        st.warning(f"No data found for farm {selected_farm}")
        return

    # Get sowing date (assuming same for all pipes in a farm)
    sowing_date = pd.to_datetime(farm_data['Date of Sowing'].iloc[0])

    # Prepare data for plotting
    pipe_data = {}
    date_columns = [col for col in df.columns if isinstance(col, str) and col.startswith('2024')]

    for _, row in farm_data.iterrows():
        pipe_code = row['Pipe Code']
        
        # Skip if pipe not selected
        if selected_pipes and pipe_code not in selected_pipes:
            continue
            
        measurements = []

        for date_col in date_columns:
            try:
                measurement_date = pd.to_datetime(date_col)
                water_level = row[date_col]

                if pd.notna(water_level):
                    days_from_sowing = (measurement_date - sowing_date).days
                    measurements.append({
                        'Date': measurement_date,
                        'Days from Sowing': days_from_sowing,
                        'Water Level': water_level
                    })
            except:
                continue

        if measurements:
            pipe_data[pipe_code] = pd.DataFrame(measurements)

    if not pipe_data:
        st.warning(f"No valid water level data for farm {selected_farm}")
        return

    # Create plots
    st.subheader(f"Water Level Analysis for Farm {selected_farm}")
    st.caption(f"Sowing Date: {sowing_date.strftime('%Y-%m-%d')}")
    
# In the plot_farm_data function, replace the weekly plots section with:

    if show_weekly:
        # Weekly average plots
        st.markdown("### Weekly Water Level Analysis")
        
        # Combine all pipe data
        all_data = pd.concat(pipe_data.values())
        
        # Calculate week numbers
        all_data['Week'] = (all_data['Days from Sowing'] // 7) + 1
        
        # Create two columns for weekly plots
        col1, col2 = st.columns(2)
        
        with col1:
            # Weekly measurements scatter plot
            st.markdown("#### Weekly Measurements by Pipe")
            fig_weekly_scatter, ax_weekly_scatter = plt.subplots(figsize=(10, 6))
            
            # Plot individual measurements as scatter points
            for pipe_code, data in pipe_data.items():
                data['Week'] = (data['Days from Sowing'] // 7) + 1
                ax_weekly_scatter.scatter(data['Week'], data['Water Level'],
                                        label=f'Pipe {pipe_code}', alpha=0.7)
            
            ax_weekly_scatter.set_xlabel('Weeks from Sowing', fontsize=12)
            ax_weekly_scatter.set_ylabel('Water Level (mm)', fontsize=12)
            ax_weekly_scatter.set_title(f'Weekly Measurements\nfor Farm {selected_farm}', fontsize=14)
            ax_weekly_scatter.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax_weekly_scatter.grid(True, alpha=0.3)
            plt.tight_layout()
            
            st.pyplot(fig_weekly_scatter)
            plt.close()
        
        with col2:
            # Weekly farm average plot
            st.markdown("#### Weekly Farm Average")
            fig_weekly_avg, ax_weekly_avg = plt.subplots(figsize=(10, 6))
            
            # Calculate and plot weekly averages
            weekly_avg_all = all_data.groupby('Week')['Water Level'].mean().reset_index()
            ax_weekly_avg.scatter(weekly_avg_all['Week'], weekly_avg_all['Water Level'],
                                color='k', s=100, label='Weekly Average')
            
            # Add overall average line
            overall_avg = all_data['Water Level'].mean()
            ax_weekly_avg.axhline(y=overall_avg, color='r', linestyle='--',
                                label=f'Overall Average: {overall_avg:.1f} mm')
            
            ax_weekly_avg.set_xlabel('Weeks from Sowing', fontsize=12)
            ax_weekly_avg.set_ylabel('Water Level (mm)', fontsize=12)
            ax_weekly_avg.set_title(f'Weekly Averages\nfor Farm {selected_farm}', fontsize=14)
            ax_weekly_avg.legend()
            ax_weekly_avg.grid(True, alpha=0.3)
            plt.tight_layout()
            
            st.pyplot(fig_weekly_avg)
            plt.close()
        
        # Show weekly averages table
        st.markdown("#### Weekly Averages Summary")
        weekly_table = all_data.groupby('Week')['Water Level'].agg(['mean', 'count', 'std']).reset_index()
        weekly_table.columns = ['Week', 'Average (mm)', 'Measurements', 'Std Dev']
        st.dataframe(weekly_table.style.format({
            'Average (mm)': '{:.1f}',
            'Std Dev': '{:.1f}'
        }))
    else:
        # Daily plots
        st.markdown("### Daily Water Level Analysis")
        
        # Create two columns for daily plots
        col1, col2 = st.columns(2)
        
        with col1:
            # Individual pipe measurements (scatter)
            st.markdown("#### Individual Pipe Measurements")
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            
            for pipe_code, data in pipe_data.items():
                ax1.scatter(data['Days from Sowing'], data['Water Level'],
                           label=f'Pipe {pipe_code}', alpha=0.7, s=100)

            ax1.set_xlabel('Days from Sowing', fontsize=12)
            ax1.set_ylabel('Water Level (mm)', fontsize=12)
            ax1.set_title(f'Daily Measurements\nfor Farm {selected_farm}', fontsize=14)
            ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax1.grid(True, alpha=0.3)
            plt.tight_layout()
            
            st.pyplot(fig1)
            plt.close()
        
        with col2:
            # Average water level over time
            st.markdown("#### Average Water Level Over Time")
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            
            # Combine all pipe data
            all_data = pd.concat(pipe_data.values())

            # Calculate daily averages
            daily_avg = all_data.groupby('Days from Sowing')['Water Level'].mean().reset_index()

            # Plot
            ax2.scatter(daily_avg['Days from Sowing'], daily_avg['Water Level'],
                        color='k', label='Daily Average')

            # Add overall average line
            overall_avg = all_data['Water Level'].mean()
            ax2.axhline(y=overall_avg, color='r', linestyle='--',
                        label=f'Overall Average: {overall_avg:.1f} mm')

            ax2.set_xlabel('Days from Sowing', fontsize=12)
            ax2.set_ylabel('Water Level (mm)', fontsize=12)
            ax2.set_title(f'Daily Averages\nfor Farm {selected_farm}', fontsize=14)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            plt.tight_layout()
            
            st.pyplot(fig2)
            plt.close()

    # Show data summary
    st.markdown("### Data Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Number of Pipes", len(pipe_data))
    
    with col2:
        all_data = pd.concat(pipe_data.values())
        st.metric("Total Measurements", len(all_data))
    
    with col3:
        overall_avg = all_data['Water Level'].mean()
        st.metric("Average Water Level (mm)", f"{overall_avg:.1f}")
    
    with col4:
        overall_std = all_data['Water Level'].std()
        st.metric("Standard Deviation (mm)", f"{overall_std:.1f}")

# Sidebar for file uploads
with st.sidebar:
    st.header("Upload Data Files")
    
    # File uploaders
    farm_file = st.file_uploader("Upload Farm Data (Excel)", type=['xlsx'])
    water_file = st.file_uploader("Upload Water Level Data (CSV)", type=['csv'])
    
    if st.button("Process Data"):
        if farm_file is not None and water_file is not None:
            with st.spinner("Processing data..."):
                processed_data = process_data(farm_file, water_file)
                if processed_data is not None:
                    st.session_state.processed_data = processed_data
                    st.session_state.farm_list = processed_data['Farm ID'].unique().tolist()
                    st.success("Data processed successfully!")
                else:
                    st.error("Failed to process data. Please check your files.")
        else:
            st.warning("Please upload both files before processing")

# Main content area
if st.session_state.processed_data is not None:
    st.header("Analyze Farm Data")
    
    # Farm selection
    selected_farm = st.selectbox(
        "Select a Farm to Analyze",
        options=st.session_state.farm_list,
        index=0,
        key="farm_selector"
    )
    
    # Get pipes for selected farm
    farm_pipes = st.session_state.processed_data[
        st.session_state.processed_data['Farm ID'] == selected_farm
    ]['Pipe Code'].unique().tolist()
    
    # Pipe selection (multi-select)
    selected_pipes = st.multiselect(
        "Select Pipes to Display (leave empty for all)",
        options=farm_pipes,
        default=None,
        key="pipe_selector"
    )
    
    # Toggle for weekly view
    show_weekly = st.checkbox("Show Weekly View", value=False)
    
    # Display plots
    plot_farm_data(selected_farm, st.session_state.processed_data, 
                  selected_pipes if selected_pipes else None, show_weekly)
    
    # Download button
    st.download_button(
        label="Download Processed Data (CSV)",
        data=st.session_state.processed_data.to_csv(index=False).encode('utf-8'),
        file_name="processed_water_level_data.csv",
        mime="text/csv"
    )
    
    # Show raw data
    if st.checkbox("Show processed data"):
        st.dataframe(st.session_state.processed_data)
else:
    st.info("Please upload and process your data files using the sidebar controls.")

# Add some app info
st.sidebar.markdown("---")
st.sidebar.markdown("""
**App Instructions:**
1. Upload the Farm Data (Excel) and Water Level Data (CSV) files
2. Click "Process Data" to prepare the data for analysis
3. Select a farm from the dropdown to view water level plots
4. Optionally select specific pipes to focus on
5. Toggle "Show Weekly View" to switch between daily and weekly views
""")