import pandas as pd
import numpy as np

def preprocess_data(df):
    """Preprocess the dataset with flexible column handling"""
    if df is None or df.empty:
        return None
    
    df = df.copy()
    
    # ========== DATA CLEANING ==========
    df = df.replace(['N/A', 'n/a', 'N/a', 'NA', 'na'], np.nan)
    
    # Handle missing values in categorical columns (only if columns exist)
    if 'Helmet_Worn' in df.columns:
        df['Helmet_Worn'] = df['Helmet_Worn'].fillna('Not Applicable')
    if 'Seatbelt_Worn' in df.columns:
        df['Seatbelt_Worn'] = df['Seatbelt_Worn'].fillna('Not Applicable')
    if 'Comments' in df.columns:
        df['Comments'] = df['Comments'].fillna('No Comments')
    if 'Breathalyzer_Result' in df.columns and 'Alcohol_Level' in df.columns:
        mask = (df['Breathalyzer_Result'].isna()) & ((df['Alcohol_Level'] == 0) | (df['Alcohol_Level'].isna()))
        df.loc[mask, 'Breathalyzer_Result'] = 'Not Conducted'
    
    # ========== DATA TYPE CONVERSIONS ==========
    # Try different date formats
    if 'Date' in df.columns:
        if df['Date'].dtype == 'object':
            # Try multiple date formats
            for fmt in ['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    df['Date'] = pd.to_datetime(df['Date'], format=fmt, errors='coerce')
                    if df['Date'].notna().sum() > 0:
                        break
                except:
                    continue
            # If all formats fail, try auto-detection
            if df['Date'].isna().all():
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    if 'Time' in df.columns:
        try:
            df['Hour'] = pd.to_datetime(df['Time'], format='%H:%M', errors='coerce').dt.hour
        except:
            try:
                df['Hour'] = pd.to_datetime(df['Time'], errors='coerce').dt.hour
            except:
                df['Hour'] = None
    
    # Convert numeric columns (only if they exist)
    numeric_cols = ['Fine_Amount', 'Driver_Age', 'Penalty_Points', 'Speed_Limit', 
                    'Recorded_Speed', 'Alcohol_Level', 'Number_of_Passengers', 
                    'Previous_Violations', 'Vehicle_Model_Year']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # ========== DERIVED FEATURES ==========
    # Temporal features (only if Date column exists)
    if 'Date' in df.columns and df['Date'].notna().any():
        df['Day_of_Week'] = df['Date'].dt.day_name()
        df['Month'] = df['Date'].dt.month_name()
        df['Year'] = df['Date'].dt.year
        df['Quarter'] = df['Date'].dt.quarter
        df['Day_of_Month'] = df['Date'].dt.day
        
        if 'Hour' in df.columns and df['Hour'].notna().any():
            df['Time_of_Day'] = pd.cut(df['Hour'],bins=[-1, 11, 17, 20, 23],
                labels=['Morning (00-11)','Afternoon (12-17)','Evening (18-20)','Night (21-23)'],
            include_lowest=True)
    
    # Speed analysis (only if both columns exist)
    if 'Recorded_Speed' in df.columns and 'Speed_Limit' in df.columns:
        df['Speed_Violation'] = df['Recorded_Speed'] > df['Speed_Limit']
        df['Speed_Excess'] = np.where(df['Speed_Violation'], 
                                      df['Recorded_Speed'] - df['Speed_Limit'], 0)
        if 'Speed_Limit' in df.columns:
            df['Speed_Excess_Percentage'] = np.where(df['Speed_Limit'] > 0,
                                                    (df['Speed_Excess'] / df['Speed_Limit']) * 100, 0)
    
    # Age groups (only if Driver_Age exists)
    if 'Driver_Age' in df.columns:
        df['Age_Group'] = pd.cut(df['Driver_Age'], bins=[0, 25, 35, 50, 65, 100], 
                                labels=['18-25', '26-35', '36-50', '51-65', '65+'], 
                                include_lowest=True)
    
    # Fine categories (only if Fine_Amount exists)
    if 'Fine_Amount' in df.columns:
        df['Fine_Category'] = pd.cut(df['Fine_Amount'], bins=[0, 1000, 2500, 4000, float('inf')],
                                     labels=['Low (0-1K)', 'Medium (1K-2.5K)', 'High (2.5K-4K)', 'Very High (4K+)'],
                                     include_lowest=True)
    
    # Alcohol categories (only if Alcohol_Level exists)
    if 'Alcohol_Level' in df.columns:
        df['Alcohol_Category'] = pd.cut(df['Alcohol_Level'], bins=[-0.01, 0.01, 0.08, 0.15, float('inf')],
                                        labels=['None (0)', 'Low (0-0.08)', 'Medium (0.08-0.15)', 'High (0.15+)'],
                                        include_lowest=True)
    
    # Repeat offender (only if Previous_Violations exists)
    if 'Previous_Violations' in df.columns:
        df['Is_Repeat_Offender'] = df['Previous_Violations'] > 0
        df['Repeat_Offender_Category'] = pd.cut(df['Previous_Violations'], 
                                                bins=[-0.5, 0.5, 2.5, 5.5, float('inf')],
                                                labels=['First Time', 'Low (1-2)', 'Medium (3-5)', 'High (5+)'],
                                                include_lowest=True)
    
    # Vehicle age (only if both columns exist)
    if 'Vehicle_Model_Year' in df.columns and 'Date' in df.columns:
        current_year = df['Date'].dt.year.max() if df['Date'].notna().any() else 2023
        df['Vehicle_Age'] = current_year - df['Vehicle_Model_Year']
        df['Vehicle_Age_Group'] = pd.cut(df['Vehicle_Age'], bins=[0, 5, 10, 15, float('inf')],
                                         labels=['New (0-5)', 'Moderate (5-10)', 'Old (10-15)', 'Very Old (15+)'],
                                         include_lowest=True)
    
    # Risk score (composite metric) - only if required columns exist
    if all(col in df.columns for col in ['Previous_Violations', 'License_Validity', 'Violation_Type', 
                                         'Speed_Excess', 'Court_Appearance_Required', 'Alcohol_Level']):
        risk_score = 0
        if 'Previous_Violations' in df.columns:
            risk_score += (df['Previous_Violations'] > 3).astype(int) * 3
        if 'License_Validity' in df.columns:
            risk_score += (df['License_Validity'] != 'Valid').astype(int) * 2
        if 'Violation_Type' in df.columns:
            risk_score += (df['Violation_Type'] == 'Drunk Driving').astype(int) * 4
        if 'Speed_Excess' in df.columns:
            risk_score += (df['Speed_Excess'] > 30).astype(int) * 2
        if 'Court_Appearance_Required' in df.columns:
            risk_score += (df['Court_Appearance_Required'] == 'Yes').astype(int) * 1
        if 'Alcohol_Level' in df.columns:
            risk_score += (df['Alcohol_Level'] > 0.08).astype(int) * 3
        df['Risk_Score'] = risk_score
        df['Risk_Category'] = pd.cut(df['Risk_Score'], bins=[-0.5, 2.5, 5.5, 8.5, float('inf')],
                                    labels=['Low Risk', 'Medium Risk', 'High Risk', 'Very High Risk'],
                                    include_lowest=True)
    
    # Compliance flags
    if 'Helmet_Worn' in df.columns:
        df['Helmet_Compliance'] = df['Helmet_Worn'].apply(lambda x: 'Compliant' if x == 'Yes' 
                                                          else 'Non-Compliant' if x == 'No' else 'N/A')
    if 'Seatbelt_Worn' in df.columns:
        df['Seatbelt_Compliance'] = df['Seatbelt_Worn'].apply(lambda x: 'Compliant' if x == 'Yes' 
                                                              else 'Non-Compliant' if x == 'No' else 'N/A')
    
    # ========== DATA VALIDATION ==========
    # Remove rows with invalid dates (if Date column exists)
    if 'Date' in df.columns:
        df = df[df['Date'].notna()]
    
    # Ensure age is within reasonable range (if Driver_Age exists)
    if 'Driver_Age' in df.columns:
        df = df[(df['Driver_Age'] >= 18) & (df['Driver_Age'] <= 100)]
    
    # Ensure speeds are non-negative (if columns exist)
    if 'Recorded_Speed' in df.columns:
        df['Recorded_Speed'] = df['Recorded_Speed'].clip(lower=0)
    if 'Speed_Limit' in df.columns:
        df['Speed_Limit'] = df['Speed_Limit'].clip(lower=0)
    
    # Ensure fine amount is non-negative (if column exists)
    if 'Fine_Amount' in df.columns:
        df['Fine_Amount'] = df['Fine_Amount'].clip(lower=0)
    
    # Ensure alcohol level is non-negative (if column exists)
    if 'Alcohol_Level' in df.columns:
        df['Alcohol_Level'] = df['Alcohol_Level'].clip(lower=0)
    
    # ========== FINAL CLEANUP ==========
    # Sort by date if Date column exists
    if 'Date' in df.columns:
        df = df.sort_values('Date').reset_index(drop=True)
    else:
        df = df.reset_index(drop=True)
    
    return df

def generate_cleaned_dataset():
    """
    Load raw dataset, preprocess it, and save as cleaned CSV.
    """
    print("Loading raw traffic violations dataset...")
    try:
        # Load the raw dataset
        df_raw = pd.read_csv('Indian_Traffic_Violations.csv')
        print(f"✓ Raw data loaded: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns")
        
        print("\nPreprocessing data...")
        # Apply preprocessing
        df_cleaned = preprocess_data(df_raw)
        print(f"✓ Data preprocessed: {df_cleaned.shape[0]} rows, {df_cleaned.shape[1]} columns")
        
        # Save to cleaned CSV
        output_file = 'Indian_Traffic_Violations_Dataset.csv'
        df_cleaned.to_csv(output_file, index=False)
        print(f"\n✓ Cleaned dataset saved to: {output_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("PREPROCESSING SUMMARY")
        print("="*60)
        print(f"Original columns: {df_raw.shape[1]}")
        print(f"Cleaned columns: {df_cleaned.shape[1]}")
        print(f"New derived features: {df_cleaned.shape[1] - df_raw.shape[1]}")
        print(f"Original rows: {df_raw.shape[0]}")
        print(f"Cleaned rows: {df_cleaned.shape[0]}")
        print(f"Rows removed: {df_raw.shape[0] - df_cleaned.shape[0]}")
        print("="*60)
        
        return df_cleaned
        
    except FileNotFoundError:
        print("Error: Indian_Traffic_Violations.csv not found!")
        return None
    except Exception as e:
        print(f"Error during preprocessing: {str(e)}")
        return None

if __name__ == "__main__":
    generate_cleaned_dataset()