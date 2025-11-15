# Credit Risk KRI Dashboard - Comprehensive Documentation

## Project Overview

**Objective:** Build a production-ready Credit Risk Key Risk Indicators (KRI) dashboard for VPBank to monitor loan portfolio health and align with COSO ERM framework.

**Date:** November 15, 2025  
**Author:** VPBank Credit Risk Team  
**Framework:** COSO Enterprise Risk Management (ERM)

---

## 1. Executive Summary

This project delivers a comprehensive credit risk monitoring system that:

- **Generates realistic synthetic loan portfolio data** reflecting Vietnamese market characteristics
- **Calculates 15+ KRIs** including NPL ratios, PAR metrics, and concentration risks
- **Provides interactive dashboards** for real-time risk monitoring
- **Aligns with COSO ERM** Performance + Information, Communication & Reporting components
- **Exports to Excel/Power BI/Tableau** for business intelligence integration

### Key Metrics Tracked

| KRI | Current Value | Risk Appetite | Status |
|-----|--------------|---------------|---------|
| NPL Ratio | 0.77% | < 3.0% | ✓ PASS |
| PAR30 | 2.23% | < 5.0% | ✓ PASS |
| PAR90 | 0.77% | < 3.5% | ✓ PASS |
| Industry Concentration | 23.43% | < 25.0% | ✓ PASS |
| Province Concentration | 29.94% | < 40.0% | ✓ PASS |

**Portfolio Size:** 10,000 loans | 13,261.8B VND outstanding

---

## 2. Data Architecture

### 2.1 Synthetic Data Generation

**File:** `loan_portfolio_generator.py`

The data generator creates realistic loan portfolio data with Vietnamese market characteristics:

#### Key Features:
- **Geographic Distribution:** 10 provinces weighted by economic importance (HCMC 30%, Hanoi 25%, etc.)
- **Industry Sectors:** 9 major industries (Retail, Manufacturing, Services, Real Estate, etc.)
- **Loan Products:** Consumer, SME Business, Mortgages, Auto, Corporate
- **Customer Segments:** Prime (40%), Standard (35%), Sub-prime (20%), New-to-Bank (5%)
- **Seasonal Effects:** Tết (Lunar New Year) impact on delinquency patterns

#### Output Files:
- `loan_portfolio_current.csv` - Current portfolio snapshot (10,000 loans)
- `loan_portfolio_timeseries.csv` - 12 months historical data (101,539 records)

#### Data Fields:
```
loan_id                        - Unique loan identifier
customer_segment              - Risk segment (Prime/Standard/Sub-prime/NTB)
province                      - Geographic location
industry                      - Borrower industry
loan_type                     - Product type
origination_date              - Loan origination date
original_amount_vnd_mil       - Original loan amount (VND millions)
outstanding_balance_vnd_mil   - Current outstanding balance
term_months                   - Loan term
interest_rate_pct             - Annual interest rate
days_past_due                 - Current DPD (0 = current)
loan_classification           - 5-tier classification (Nhóm 1-5)
months_on_book               - Age of loan
utilization_pct              - % of original amount outstanding
vintage                       - Origination cohort (YYYYQQ)
```

### 2.2 Loan Classification System (Circular 02/2013/TT-NHNN)

Vietnamese banking regulation defines 5 loan classifications:

| Classification | DPD Range | NPL Status | Description |
|---------------|-----------|------------|-------------|
| Nhóm 1 - Bình thường | 0 days | No | Current, performing |
| Nhóm 2 - Cần chú ý | 1-30 days | No | Watch list, early delinquency |
| Nhóm 3 - Dưới tiêu chuẩn | 31-89 days | No | Substandard |
| Nhóm 4 - Nghi ngờ | 90-179 days | **Yes** | Doubtful |
| Nhóm 5 - Tổn thất | 180+ days | **Yes** | Loss |

**NPL Definition:** Nhóm 4 + Nhóm 5 (DPD ≥ 90 days)

---

## 3. KRI Calculator Engine

**File:** `kri_calculator.py`

### 3.1 Core KRI Metrics

#### A. NPL (Non-Performing Loan) Metrics

**Formula:** NPL Ratio = (NPL Balance / Total Outstanding Balance) × 100%

**Breakdown Dimensions:**
- By Customer Segment (Prime, Standard, Sub-prime, NTB)
- By Loan Product (Consumer, SME, Mortgage, Auto, Corporate)
- By Industry (9 sectors)
- By Province (10 regions)

**Risk Appetite:** NPL Ratio < 3.0%

#### B. PAR (Portfolio at Risk) Metrics

Measures percentage of portfolio with any delinquency:

- **PAR30:** Loans with DPD ≥ 30 days (Risk Appetite: < 5.0%)
- **PAR60:** Loans with DPD ≥ 60 days
- **PAR90:** Loans with DPD ≥ 90 days (Risk Appetite: < 3.5%)
- **PAR180:** Loans with DPD ≥ 180 days

**Formula:** PARx = (Balance with DPD ≥ x / Total Outstanding) × 100%

#### C. Portfolio Quality Distribution

Distribution across 5 loan classifications:
- Count distribution (% of loans)
- Balance distribution (% of outstanding)

#### D. Concentration Risk

**Industry Concentration:**
- Top industry exposure %
- Top 3 industries total %
- HHI (Herfindahl-Hirschman Index) for concentration measurement
- Risk Appetite: Single industry < 25%

**Geographic Concentration:**
- Top province exposure %
- Top 3 provinces total %
- HHI index
- Risk Appetite: Single province < 40%

**HHI Interpretation:**
- < 1,500: Low concentration
- 1,500 - 2,500: Moderate concentration
- > 2,500: High concentration

#### E. Early Warning Indicators

- **Early Delinquency:** Loans with 1-29 DPD (% of portfolio)
- **Watch List:** Nhóm 2 loans (% of portfolio)
- **New Loan Issues:** Loans < 6 months old with delinquency

#### F. Vintage Analysis

Performance metrics by origination cohort (Year-Quarter):
- Total loans and balance per vintage
- NPL count and ratio per vintage
- Average DPD per vintage

Helps identify:
- Underwriting quality changes over time
- Seasoning effects
- Portfolio deterioration patterns

#### G. Migration Matrix

Transition probabilities between loan classifications over time:

```
          Current Classification
          Nhóm 1  Nhóm 2  Nhóm 3  Nhóm 4  Nhóm 5
Previous
Nhóm 1     95.0%    3.0%    1.5%    0.3%    0.2%
Nhóm 2     10.0%   70.0%   15.0%    3.0%    2.0%
Nhóm 3      5.0%   10.0%   65.0%   15.0%    5.0%
Nhóm 4      2.0%    3.0%   10.0%   70.0%   15.0%
Nhóm 5      0.0%    0.0%    0.0%   10.0%   90.0%
```

**Key Insights:**
- Diagonal values (stability): % staying in same class
- Right movement (deterioration): Portfolio quality worsening
- Left movement (improvement): Portfolio quality improving

### 3.2 Risk Appetite Framework

| Metric | Threshold | Current | Utilization |
|--------|-----------|---------|-------------|
| NPL Ratio | 3.0% | 0.77% | 25.6% |
| PAR30 | 5.0% | 2.23% | 44.6% |
| PAR90 | 3.5% | 0.77% | 22.0% |
| Single Industry | 25.0% | 23.43% | 93.7% |
| Single Province | 40.0% | 29.94% | 74.9% |

---

## 4. Dashboard & Visualization

### 4.1 Interactive HTML Dashboard

**File:** `kri_dashboard.html`

**Components:**

1. **KPI Cards** - Executive summary with gauges
   - NPL Ratio with risk appetite threshold
   - PAR30 and PAR90 metrics
   - Total portfolio size
   - Watch list and early delinquency counts

2. **NPL Trend Chart** - 12-month time series
   - NPL ratio over time
   - PAR30 and PAR90 trends
   - Risk appetite threshold line

3. **NPL Breakdown Charts**
   - By customer segment (bar chart)
   - By loan product (bar chart)
   - Color-coded by performance (green/yellow/red)

4. **Geographic & Industry Heatmaps**
   - Province heatmap showing NPL by region
   - Industry heatmap showing NPL by sector
   - Color intensity indicates risk level

5. **Portfolio Quality Distribution**
   - Dual charts: by count and by balance
   - All 5 loan classifications
   - Color-coded by risk level

6. **Concentration Risk**
   - Industry concentration pie chart
   - Province concentration pie chart
   - Shows top exposures

7. **Migration Matrix Heatmap**
   - Transition probabilities
   - Color-coded: green (stability), red (deterioration)

8. **Vintage Analysis**
   - NPL ratio by origination cohort
   - Portfolio balance trend
   - Identifies problematic cohorts

### 4.2 Excel Report

**File:** `kri_report.xlsx`

**Worksheets:**

1. **Executive Summary** - KRI overview with traffic light status
2. **NPL by Segment** - Detailed NPL breakdown
3. **NPL by Product** - Product-level analysis
4. **NPL by Industry** - Industry exposure
5. **NPL by Province** - Geographic risk
6. **PAR Analysis** - PAR metrics by segment
7. **Portfolio Quality** - 5-tier classification distribution
8. **Concentration - Industry** - Industry concentration details
9. **Concentration - Province** - Geographic concentration
10. **Vintage Analysis** - Cohort performance
11. **Segment Performance** - Customer segment metrics
12. **Migration Matrix** - Transition probabilities
13. **Time Series** - Historical metrics for Power BI
14. **Raw Data (Sample)** - Loan-level data sample
15. **Instructions** - User guide and COSO alignment

**Features:**
- Formatted headers and color-coding
- Conditional formatting (green/yellow/red)
- Pre-calculated metrics ready for charting
- Power BI / Tableau integration ready

---

## 5. COSO ERM Framework Alignment

### 5.1 Performance Component

**COSO Principle:** Organizations hold themselves accountable to defined performance measures

**Implementation:**
- **Risk Appetite Defined:** Clear thresholds for NPL (3%), PAR30 (5%), PAR90 (3.5%)
- **KPIs Established:** 15+ quantitative metrics tracking credit risk
- **Continuous Monitoring:** Real-time dashboard updates
- **Automated Alerts:** Traffic light system flags breaches

**Evidence in Dashboard:**
- Executive Summary shows current vs. appetite
- Utilization % shows proximity to limits
- Status column (PASS/BREACH) for immediate visibility

### 5.2 Information, Communication & Reporting

**COSO Principle:** Relevant information is identified, captured, and communicated in a timely manner

**Implementation:**
- **Multi-Stakeholder Access:** HTML dashboard for executives, Excel for analysts
- **Real-Time Visibility:** Current portfolio status always available
- **Drill-Down Capability:** Executive summary → detailed segment analysis
- **Historical Context:** 12-month trends show trajectory

**Dashboard Features:**
- **Interactive Charts:** Hover for details, click to filter
- **Multiple Dimensions:** Segment, product, geography, vintage
- **Export Options:** HTML, Excel, CSV for different use cases
- **Sharing:** Single HTML file easily distributed

### 5.3 Governance & Culture

**COSO Principle:** The organization's commitment to integrity and ethical values influences decision-making

**Implementation:**
- **Transparency:** All calculation methods documented
- **Consistency:** Standardized KRI definitions across organization
- **Objectivity:** Automated calculations eliminate bias
- **Accountability:** Clear ownership of risk appetite breaches

### 5.4 Strategy & Objective-Setting

**COSO Principle:** Risk appetite is established and aligned with strategy

**Implementation:**
- **Strategic Alignment:** NPL targets support VPBank's growth objectives
- **Segment Strategy:** Different risk tolerance by customer segment
- **Product Strategy:** Monitor concentration to avoid over-exposure
- **Geographic Strategy:** Provincial limits prevent regional concentration

### 5.5 Event Identification & Risk Assessment

**COSO Principle:** Risks and opportunities affecting strategy achievement are identified

**Implementation:**
- **Early Warning Indicators:** Watch list, early delinquency tracking
- **Migration Matrix:** Identifies deteriorating portfolio quality trends
- **Concentration Monitoring:** Prevents systemic industry/regional shocks
- **Vintage Analysis:** Detects underwriting quality issues early

**Predictive Capabilities:**
- Watch List (Nhóm 2) predicts future NPL
- New loan issues (< 6 months) signals underwriting problems
- Migration matrix shows flow to NPL before it occurs

### 5.6 Control Activities

**COSO Principle:** Controls are established and executed to mitigate risks

**Implementation:**
- **Concentration Limits:** Industry < 25%, Province < 40%
- **Risk Appetite Enforcement:** Automated flagging of breaches
- **Segregation:** Different thresholds by customer segment
- **Review Cadence:** Daily dashboard updates

### 5.7 Review & Revision

**COSO Principle:** The organization reviews its performance and revises ERM components

**Implementation:**
- **Historical Trends:** 12-month time series enables pattern recognition
- **Vintage Analysis:** Evaluates changes in underwriting quality
- **Migration Tracking:** Monitors effectiveness of collection efforts
- **Quarterly Reviews:** Update risk appetite based on performance

---

## 6. Power BI / Tableau Integration Guide

### 6.1 Data Import

**Excel Integration:**
1. Open `kri_report.xlsx`
2. Use "Time Series" sheet for historical metrics
3. Use "Raw Data (Sample)" for loan-level details
4. Import to Power BI using "Get Data > Excel"

**CSV Integration:**
1. Import `loan_portfolio_current.csv` for current snapshot
2. Import `loan_portfolio_timeseries.csv` for trends
3. Create relationships on `loan_id` field

### 6.2 Recommended Visualizations

**Executive Dashboard:**
- KPI Cards: NPL Ratio, PAR30, PAR90
- Line Chart: NPL trend over time
- Gauge Charts: Utilization vs. risk appetite

**Portfolio Analysis:**
- Stacked Bar: Quality distribution
- Treemap: Industry/Province concentration
- Heat Map: NPL by segment × product matrix

**Risk Monitoring:**
- Waterfall: Migration between classifications
- Scatter: Vintage vs. NPL ratio
- Map: Geographic NPL distribution (Vietnam map)

### 6.3 Sample DAX Measures

```dax
NPL_Ratio = 
DIVIDE(
    CALCULATE(
        SUM('Portfolio'[outstanding_balance_vnd_mil]),
        'Portfolio'[loan_classification] IN {"Nhóm 4 - Nghi ngờ", "Nhóm 5 - Tổn thất"}
    ),
    SUM('Portfolio'[outstanding_balance_vnd_mil])
)

PAR30_Ratio = 
DIVIDE(
    CALCULATE(
        SUM('Portfolio'[outstanding_balance_vnd_mil]),
        'Portfolio'[days_past_due] >= 30
    ),
    SUM('Portfolio'[outstanding_balance_vnd_mil])
)

Risk_Appetite_Status = 
IF(
    [NPL_Ratio] < 0.03,
    "PASS",
    "BREACH"
)

YoY_NPL_Change = 
[NPL_Ratio] - 
CALCULATE(
    [NPL_Ratio],
    DATEADD('Calendar'[Date], -1, YEAR)
)
```

### 6.4 Filters & Slicers

Recommended interactive filters:
- **Date Range:** Select time period for analysis
- **Customer Segment:** Filter by Prime/Standard/Sub-prime/NTB
- **Province:** Geographic drill-down
- **Industry:** Sector analysis
- **Loan Type:** Product comparison
- **Vintage:** Cohort analysis

---

## 7. Production Deployment Guide

### 7.1 System Requirements

**Python Environment:**
- Python 3.8+
- pandas >= 1.3.0
- numpy >= 1.21.0
- plotly >= 5.0.0
- xlsxwriter >= 3.0.0
- openpyxl >= 3.0.0

**Installation:**
```bash
pip install pandas numpy plotly xlsxwriter openpyxl
```

### 7.2 Running the System

**Step 1: Generate Loan Portfolio Data**
```bash
python loan_portfolio_generator.py
```
Output:
- `loan_portfolio_current.csv`
- `loan_portfolio_timeseries.csv`

**Step 2: Calculate KRIs**
```bash
python kri_calculator.py
```
Output: Console report with all KRI metrics

**Step 3: Generate HTML Dashboard**
```bash
python create_dashboard.py
```
Output: `kri_dashboard.html`

**Step 4: Generate Excel Report**
```bash
python create_excel_report.py
```
Output: `kri_report.xlsx`

### 7.3 Automation Schedule

**Recommended Update Frequency:**
- **Daily:** For operational monitoring
- **Weekly:** For management reporting
- **Monthly:** For board reporting

**Automation Script (Linux/Mac):**
```bash
#!/bin/bash
# Daily KRI Dashboard Update

cd /path/to/project

# Generate fresh data (or replace with actual data load)
python loan_portfolio_generator.py

# Create dashboard
python create_dashboard.py

# Create Excel report
python create_excel_report.py

# Email dashboard (optional)
mail -s "Daily KRI Dashboard" -a kri_dashboard.html risk-team@vpbank.com.vn < /dev/null
```

**Windows Task Scheduler:**
1. Create batch file `run_kri_dashboard.bat`
2. Add to Task Scheduler
3. Set to run daily at 7:00 AM

### 7.4 Data Refresh Process

**For Production Use:**

Replace synthetic data generation with actual data extraction:

```python
# Instead of generating synthetic data:
# generator = LoanPortfolioGenerator(n_loans=10000)
# df = generator.generate_portfolio()

# Load from production database:
import pyodbc

conn = pyodbc.connect('DSN=VPBank_DW;UID=user;PWD=pass')

query = """
SELECT 
    loan_id,
    customer_segment,
    province,
    industry,
    loan_type,
    origination_date,
    original_amount_vnd / 1000000 as original_amount_vnd_mil,
    outstanding_balance_vnd / 1000000 as outstanding_balance_vnd_mil,
    term_months,
    interest_rate_pct,
    days_past_due,
    loan_classification,
    DATEDIFF(month, origination_date, GETDATE()) as months_on_book,
    (outstanding_balance_vnd / original_amount_vnd * 100) as utilization_pct,
    CONCAT(YEAR(origination_date), 'Q', CEILING(MONTH(origination_date)/3.0)) as vintage
FROM 
    credit_risk.vw_loan_portfolio
WHERE 
    status = 'ACTIVE'
    AND snapshot_date = CAST(GETDATE() AS DATE)
"""

df = pd.read_sql(query, conn)
conn.close()
```

---

## 8. Customization Guide

### 8.1 Modifying Risk Appetite

Edit `kri_calculator.py`:

```python
self.risk_appetite = {
    'npl_ratio_max': 3.0,           # Change threshold here
    'par30_ratio_max': 5.0,          
    'par90_ratio_max': 3.5,          
    'single_borrower_max': 15.0,     
    'industry_concentration_max': 25.0,  
    'province_concentration_max': 40.0   
}
```

### 8.2 Adding New KRIs

Add to `CreditRiskKRI` class:

```python
def calculate_lcr_ratio(self):
    """Calculate Loan Coverage Ratio"""
    
    npl_balance = self.df[
        self.df['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])
    ]['outstanding_balance_vnd_mil'].sum()
    
    # Assume provision data available
    total_provisions = self.df['provision_amount_vnd_mil'].sum()
    
    lcr = total_provisions / npl_balance * 100
    
    return {
        'lcr_ratio': lcr,
        'npl_balance': npl_balance,
        'total_provisions': total_provisions,
        'within_risk_appetite': lcr >= 100.0  # 100% coverage target
    }
```

### 8.3 Custom Segments

Modify in `loan_portfolio_generator.py`:

```python
self.segments = {
    'VIP': 0.10,           # Add VIP segment
    'Prime': 0.35,
    'Standard': 0.30,
    'Sub-prime': 0.20,
    'NTB': 0.05
}
```

---

## 9. Maintenance & Support

### 9.1 Troubleshooting

**Issue: Empty dashboard**
- Check that CSV files exist in `/mnt/user-data/outputs/`
- Verify data types (dates should be datetime)
- Check for NaN values in key fields

**Issue: Excel file won't open**
- Ensure xlsxwriter package installed
- Check file permissions
- Verify enough disk space

**Issue: KRI values seem wrong**
- Verify loan_classification mapping
- Check DPD field for negative values
- Validate outstanding_balance > 0

### 9.2 Performance Optimization

**For Large Portfolios (> 100K loans):**

1. Use chunking for data processing:
```python
chunksize = 10000
for chunk in pd.read_csv('large_file.csv', chunksize=chunksize):
    process_chunk(chunk)
```

2. Use categorical data types:
```python
df['customer_segment'] = df['customer_segment'].astype('category')
```

3. Index key columns:
```python
df = df.set_index('loan_id')
```

### 9.3 Quality Assurance Checks

Before production deployment:

1. **Data Validation:**
   - All loan_ids unique
   - No negative balances
   - DPD >= 0
   - Dates in valid range

2. **KRI Validation:**
   - NPL ratio = (NPL count / total count) should be similar magnitude
   - Sum of classification % = 100%
   - Migration matrix rows sum to 100%

3. **Dashboard Validation:**
   - All charts render correctly
   - Tooltips show accurate data
   - Links work in HTML file

---

## 10. Future Enhancements

### Phase 2 Enhancements:

1. **Predictive Analytics:**
   - Machine learning model for NPL prediction
   - Early warning score (0-100)
   - Expected credit loss (ECL) forecasting

2. **Advanced Segmentation:**
   - Behavioral segmentation
   - RFM analysis (Recency, Frequency, Monetary)
   - Customer lifetime value integration

3. **Real-Time Alerts:**
   - Email notifications for breaches
   - SMS alerts for critical thresholds
   - Slack/Teams integration

4. **API Development:**
   - REST API for KRI queries
   - WebSocket for real-time updates
   - Mobile app integration

5. **Advanced Visualizations:**
   - 3D scatter plots
   - Network graphs for connected exposures
   - Animated time series

---

## 11. References

### Vietnamese Banking Regulations:
- **Circular 02/2013/TT-NHNN** - Loan classification and provisioning
- **Circular 41/2016/TT-NHNN** - Prudential ratios
- **Decision 493/QD-NHNN** - Credit institution risk management

### COSO Framework:
- **COSO ERM Framework (2017)** - Enterprise Risk Management—Integrating with Strategy and Performance
- **COSO Internal Control (2013)** - Integrated Framework

### Technical Resources:
- **Pandas Documentation:** https://pandas.pydata.org/docs/
- **Plotly Documentation:** https://plotly.com/python/
- **Power BI Documentation:** https://docs.microsoft.com/power-bi/

---

## 12. Contact & Support

**Project Owner:** VPBank Credit Risk Team  
**Technical Lead:** Chief Data Architect  
**Email:** creditrisk@vpbank.com.vn  
**Documentation Version:** 1.0  
**Last Updated:** November 15, 2025

---

## Appendix A: Data Dictionary

### Loan Portfolio Fields

| Field Name | Data Type | Description | Example |
|-----------|-----------|-------------|---------|
| loan_id | String | Unique identifier | LOAN00001234 |
| customer_segment | String | Risk category | Prime / Standard / Sub-prime / NTB |
| province | String | Geographic location | TP. Hồ Chí Minh |
| industry | String | Borrower industry | Bán lẻ |
| loan_type | String | Product category | Tiêu dùng |
| origination_date | DateTime | Loan start date | 2024-01-15 |
| original_amount_vnd_mil | Float | Original principal (VND millions) | 500.0 |
| outstanding_balance_vnd_mil | Float | Current balance (VND millions) | 375.5 |
| term_months | Integer | Loan duration | 36 |
| interest_rate_pct | Float | Annual interest rate | 15.5 |
| days_past_due | Integer | Current delinquency | 0 |
| loan_classification | String | 5-tier classification | Nhóm 1 - Bình thường |
| months_on_book | Float | Loan age | 18.5 |
| utilization_pct | Float | % of original outstanding | 75.1 |
| vintage | String | Origination cohort | 2024Q1 |

### KRI Metrics Dictionary

| KRI Name | Formula | Threshold | Frequency |
|----------|---------|-----------|-----------|
| NPL Ratio | (NPL Balance / Total Balance) × 100% | < 3.0% | Daily |
| PAR30 | (Balance DPD≥30 / Total) × 100% | < 5.0% | Daily |
| PAR90 | (Balance DPD≥90 / Total) × 100% | < 3.5% | Daily |
| Industry HHI | Σ(Market Share²) | < 2500 | Weekly |
| Province HHI | Σ(Market Share²) | < 2500 | Weekly |
| Watch List Ratio | (Nhóm 2 Balance / Total) × 100% | Monitor | Daily |
| Early Delinquency | (1-29 DPD Balance / Total) × 100% | Monitor | Daily |

---

## Appendix B: Glossary

**DPD:** Days Past Due - Number of days payment is overdue

**NPL:** Non-Performing Loan - Loans in Nhóm 4 or Nhóm 5 (DPD ≥ 90)

**PAR:** Portfolio at Risk - Percentage of portfolio with delinquency

**HHI:** Herfindahl-Hirschman Index - Measure of concentration (sum of squared market shares)

**Risk Appetite:** Maximum risk the organization is willing to accept

**Vintage:** Cohort of loans originated in same time period (e.g., 2024Q1)

**Migration Matrix:** Transition probabilities between loan classifications

**Watch List:** Loans in Nhóm 2 requiring close monitoring

**Thin File:** Customer with limited credit history

**NTB:** New to Bank - Customer without prior relationship

**COSO ERM:** Committee of Sponsoring Organizations Enterprise Risk Management framework

**LCR:** Loan Coverage Ratio - Provisions / NPL (target ≥ 100%)

---

*End of Documentation*
