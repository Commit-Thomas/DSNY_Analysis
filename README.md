# ♻️ DSNY Recycling Performance Forecasting
By Thomas Segal & Vincet Perez
---

![DSNY Logo](https://upload.wikimedia.org/wikipedia/en/thumb/5/59/New_York_City_Department_of_Sanitation_logo.svg/2560px-New_York_City_Department_of_Sanitation_logo.svg.png)

## 1. Project Overview

This project forecasts recycling performance for NYC community districts using time series analysis. An interactive Streamlit application automatically selects the best forecasting model (Baseline, ARIMA, or SARIMA) for each district based on RMSE, helping DSNY predict monthly recycling proportions one month in advance.

**Context**: DSNY collects 24 million pounds of recyclables, trash, and compost materials daily across 59 district garages in NYC's 5 boroughs. District-level analysis reveals significant variation—in 2024, Manhattan District 8 collected **1,576 more tons** of recyclables than Brooklyn District 16, highlighting the need for targeted forecasting.

**Key Innovation**: Rather than forcing a single model across all districts, our system recognizes that recycling patterns vary significantly by location and automatically selects the most accurate approach for each community district.

![Streamlit App Demo](projectdemo.mp4)

---

## 2. Business Objectives

**Primary Goal**: Provide DSNY's operations department with predictive insights to allocate resources efficiently and budget for expected peaks in recycling activity.

1. **Performance Forecasting**: Predict monthly recycling proportions at the district level
2. **Model Comparison**: Automatically select optimal forecasting approach per district
3. **Resource Optimization**: Enable proactive allocation based on predicted trends
4. **District Analysis**: Identify high and low performers for targeted interventions

**Core Problem**: DSNY needs to distinguish between districts that recycle as a function of total waste collection to allocate educational resources, identify potential infrastructure issues, and track progress toward sustainability goals.

**Stakeholders**:
* **DSNY Operations Department**: Primary user for resource allocation and budget planning
* **Environmental NGOs**: Advocacy groups can compare district trends and promote recycling campaigns
* **Community Organizations**: Local groups can use insights to drive education and habit formation

---

## 3. Dataset

**Source**: [NYC Open Data - DSNY Monthly Tonnage](https://data.cityofnewyork.us/City-Government/DSNY-Monthly-Tonnage-Data/ebb7-mvp5/about_data)

* **Coverage**: ~24,647 monthly observations (Jan 2022 - Oct 2025)
* **Geographic Scope**: 59 community districts across 5 boroughs

**Key Columns**:

| Column | Description | Type |
| --- | --- | --- |
| MONTH | Reporting month | DateTime |
| BOROUGH | NYC borough | Categorical |
| COMMUNITYDISTRICT | District number (1-18) | Integer |
| REFUSETONSCOLLECTED | Non-recyclable tons | Float |
| PAPERTONSCOLLECTED | Paper recyclables (tons) | Float |
| MGPTONSCOLLECTED | Metal/Glass/Plastic (tons) | Float |
| proportionrefuse* | (Paper + MGP) / Total Waste | Float [0-1] |
| id* | Borough + District (e.g., "bronx1") | String |

*Engineered features

---

## 4. Setup & Installation
```bash
# Clone and setup
git clone https://github.com/Commit-Thomas/DSNY_Analysis.git
cd DSNY_Analysis
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Download data
# Place DSNY_Monthly_Tonnage_Data.csv in data/ folder

# Run notebooks in order (01_eda → 02_baseline → 03_simple → 04_tuned)

# Launch app
cd app
streamlit run streamlit_app.py
```

---

## 5. Key EDA Insights

* **Temporal Patterns**: Clear seasonal trends across all boroughs (2022-2025)
* **District Variability**: Recycling proportions vary significantly; Manhattan District 8 leads with 1,884 tons recyclables
* **Distribution**: Right-skewed waste tonnage with high inter-district variability
* **Top Performers**: Manhattan and Queens districts consistently show higher recycling rates
* **Target Variable**: Recycling proportion = (Paper + MGP) / (Paper + MGP + Refuse)

**Critical Finding**: The gap between highest and lowest performing districts in 2024 was ~30% (308 tons vs 1,884 tons in raw recyclables), demonstrating the need for district-level analysis rather than borough-wide aggregation.

---

## 6. Modeling Approach

### Three-Model Comparison Strategy

We use all three models simultaneously because RMSE varies significantly depending on the unique borough/district combination. Rather than selecting one "best" model globally, we let each district's data determine its optimal forecasting approach.

**Baseline (Naive Forecast)**
* **Method**: Most naive approach—assumes yesterday's recycling percentage remains the same
* **Best for**: Highly stable time series with minimal variation

**ARIMA(1,1,1)**
* **Method**: Slightly less naive—assumes yesterday's tonnage influences today's
* **Advantage**: More robust because it accounts for errors in past predictions
* **Best for**: Series with trends, no strong seasonality

**SARIMA(1,1,1)(1,1,1,12)**
* **Method**: Most complex—like ARIMA but accounts for seasonal changes (12-month cycle)
* **Advantage**: Captures yearly patterns in recycling behavior
* **Best for**: Series with yearly cycles

### Model Selection
* **Metric**: Root Mean Squared Error (RMSE)
* **Strategy**: Automatically select lowest RMSE per district
* **Split**: 70% train (2023) / 30% test (2024)

---

## 7. Streamlit Application

**Features**:
* Enter district ID (format: `bronx1`, `manhattan8`, etc.)
* Automatic RMSE calculation for all three models
* Visual forecast with training data, actual values, and predictions
* Highlights best-performing model
* **District-level aggregation**: Provides detailed analysis for individual borough/district combinations

**Usage**:
```bash
cd app
streamlit run streamlit_app.py
```

**Tool Capabilities**:
* **Predictive**: Forecasts future percentage of recycled waste using time series data
* **Comparative**: Finds percent of recycled waste compared to total waste (tons)
* **Granular**: Operates at district level for targeted resource allocation

---

## 8. Results

**Example: Bronx District 1**

| Model | RMSE | Selected |
| --- | --- | --- |
| Baseline | 0.008 | ✓ |
| ARIMA(1,1,1) | 0.008 | ✓ |
| SARIMA(1,1,1)(1,1,1,12) | 0.011 | |

**Key Finding**: No single model dominates across all districts. Adaptive selection ensures optimal accuracy for each location's unique patterns.

---

## 9. Business Impact

**Operational Benefits**:
* Proactive resource allocation to underperforming districts
* Budget planning through volume forecasts
* Performance monitoring to measure program effectiveness

**Strategic Insights**:
* High performers: Manhattan and Queens districts
* Improvement opportunities: Several Bronx and Brooklyn districts
* Stable districts: Baseline models indicate consistent community behavior

**Practical Applications**:
* **Educational Campaigns**: Target districts predicted to underperform with recycling education
* **Infrastructure Planning**: Identify if low performance correlates with collection logistics
* **Policy Evaluation**: Track impact of new recycling initiatives by comparing forecasts to actuals
* **Resource Reallocation**: Shift successful strategies from high-performing to low-performing districts

---

## 10. Limitations & Future Work

**Current Limitations**:
* **Comparison Constraints**: Can only compare within groups—no per capita data to properly scale across districts of different sizes
* **Limited Features**: Few variables in dataset restrict model complexity and explanatory power
* **Readability**: Current percentage-based output could be converted to raw tons for better legibility
* **Domain Knowledge Required**: Tool currently most usable by those familiar with DSNY operations
* **Grouping Challenges**: K-means clustering did not reveal distinct district behavior patterns
* **Monthly Granularity**: Single-step ahead forecasting (1 month only)
* **External Factors**: Weather, policy changes, and events not explicitly modeled

**Future Enhancements**:
* **Per Capita Normalization**: Incorporate population data for fair cross-district comparison
* **Feature Expansion**: Add demographic, infrastructure, and policy variables
* **Output Options**: Toggle between percentage and raw tonnage displays
* **Multi-step Forecasting**: Extend prediction horizon for longer-term planning
* **User Interface**: Simplify for non-technical DSNY staff
* **Advanced Modeling**: Auto-ARIMA, LSTM, Prophet for improved accuracy
* **Confidence Intervals**: Provide uncertainty bounds for predictions
* **Multicollinearity Analysis**: Address potential feature correlation issues

**Known Challenges**:
* Tracking district-level improvements over time requires careful consideration of external factors (e.g., policy changes, infrastructure upgrades)
* Closing the performance gap between high and low recyclers may require interventions beyond prediction capabilities
* Different districts may require fundamentally different strategies based on demographics, building types, and local culture

---

## 11. Project Structure
```
DSNY_Analysis/
├── app/
│   └── streamlit_app.py          # Interactive forecasting tool
├── data/
│   └── DSNY_Monthly_Tonnage_Data.csv
├── models/
│   ├── baseline.pkl              # Baseline predictions
│   ├── modeling_simple.pkl       # ARIMA models
│   └── modeling_tuned.pkl        # SARIMA models
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_modeling_baseline.ipynb
│   ├── 03_modeling_simple.ipynb
│   └── 04_modeling_tuned.ipynb
├── requirements.txt
└── README.md
```

---

**Last Updated**: December 2025
