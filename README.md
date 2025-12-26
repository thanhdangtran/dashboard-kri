# Credit Risk KRI Dashboard

## Tổng quan dự án

Hệ thống dashboard KRI (Key Risk Indicators) toàn diện cho quản lý rủi ro tín dụng, được thiết kế đặc biệt cho các đặc điểm thị trường Việt Nam.

### Dữ liệu Synthetic
- **10,000 khoản vay** với đặc điểm thị trường Việt Nam
- **12 tháng dữ liệu lịch sử** (101,539 records)
- Phân bố theo tỉnh/thành, ngành nghề, sản phẩm, phân khúc khách hàng
- Hiệu ứng mùa Tết, đặc điểm rủi ro địa phương

### KRI Metrics (15+ chỉ số)
- **NPL Ratio:** 0.77% (Risk Appetite: < 3.0%) ✅ PASS
- **PAR30:** 2.23% (Risk Appetite: < 5.0%) ✅ PASS  
- **PAR90:** 0.77% (Risk Appetite: < 3.5%) ✅ PASS
- **Industry Concentration:** 23.43% (Limit: < 25%) ✅ PASS
- **Province Concentration:** 29.94% (Limit: < 40%) ✅ PASS

### Dashboard & Reports
- **Interactive HTML Dashboard** - Real-time visualization
- **Excel Report** - 15 worksheets với charts & formatting
- **Power BI/Tableau Ready** - Time series data prepared

---

## Files được tạo ra

### 1. Dữ liệu
```
loan_portfolio_current.csv      - Danh mục cho vay hiện tại (10,000 loans)
loan_portfolio_timeseries.csv   - Dữ liệu 12 tháng (101,539 records)
```

### 2. Dashboard & Reports
```
kri_dashboard.html              - Interactive dashboard (Mở bằng browser)
kri_report.xlsx                 - Excel report (15 worksheets)
```

### 3. Source Code
```
loan_portfolio_generator.py     - Tạo dữ liệu synthetic
kri_calculator.py              - Tính toán KRI metrics
create_dashboard.py            - Tạo HTML dashboard
create_excel_report.py         - Tạo Excel report
```

### 4. Documentation
```
PROJECT_DOCUMENTATION.md        - Tài liệu chi tiết (60+ pages)
README.md                      - File này
```

---

## Quick Start

### Bước 1: Xem Dashboard
```bash
# Mở file HTML trong browser
open kri_dashboard.html
```

### Bước 2: Xem Excel Report
```bash
# Mở file Excel
open kri_report.xlsx
```

### Bước 3: Chạy lại để tạo dữ liệu mới
```bash
# Generate new synthetic data
python loan_portfolio_generator.py

# Create new dashboard
python create_dashboard.py

# Create new Excel report
python create_excel_report.py
```

---

## Dashboard Components

### 1. Executive Summary (KPI Cards)
- NPL Ratio với gauge chart
- PAR30, PAR90 metrics
- Total Portfolio size
- Watch List & Early Delinquency

### 2. NPL Analysis
- **Trend Chart:** 12-month NPL/PAR trend
- **By Segment:** Prime, Standard, Sub-prime, NTB
- **By Product:** Consumer, SME, Mortgage, Auto, Corporate
- **By Geography:** 10 tỉnh/thành
- **By Industry:** 9 ngành nghề

### 3. Portfolio Quality
- Distribution across 5 loan classifications
- Count % và Balance %
- Color-coded risk levels

### 4. Concentration Risk
- **Industry:** Pie chart + HHI index
- **Province:** Geographic distribution
- Risk appetite monitoring

### 5. Risk Monitoring
- **Migration Matrix:** Transition between classifications
- **Vintage Analysis:** Performance by cohort
- **Early Warning:** Watch list, early delinquency

---

## Excel Report Structure

### Worksheets:
1. **Executive Summary** - KRI overview với traffic light
2. **NPL by Segment** - Chi tiết theo phân khúc
3. **NPL by Product** - Chi tiết theo sản phẩm
4. **NPL by Industry** - Chi tiết theo ngành
5. **NPL by Province** - Chi tiết theo tỉnh/thành
6. **PAR Analysis** - PAR30/60/90/180 metrics
7. **Portfolio Quality** - 5-tier classification
8. **Concentration - Industry** - Industry exposure
9. **Concentration - Province** - Geographic exposure
10. **Vintage Analysis** - Cohort performance
11. **Segment Performance** - Detailed segment metrics
12. **Migration Matrix** - Transition probabilities
13. **Time Series** - Historical data for Power BI
14. **Raw Data (Sample)** - Loan-level data
15. **Instructions** - User guide & COSO alignment

## Power BI / Tableau Integration

### Import Data:
1. Open `kri_report.xlsx`
2. Use **"Time Series"** sheet for trends
3. Use **"Raw Data (Sample)"** for details
4. Import to Power BI: Get Data > Excel

### Recommended Visuals:
- **KPI Cards:** NPL, PAR30, PAR90
- **Line Chart:** NPL trend over time
- **Heatmap:** NPL by segment × product
- **Map:** Geographic distribution (Vietnam)
- **Waterfall:** Migration matrix
- 
---

## COSO ERM Framework Alignment

### Performance Component
- ✅ Risk appetite clearly defined
- ✅ Continuous KPI monitoring
- ✅ Automated breach alerts
- ✅ Performance tracking vs targets

### Information, Communication & Reporting
- ✅ Real-time dashboard for stakeholders
- ✅ Multi-dimensional risk breakdown
- ✅ Historical trends for decision-making
- ✅ Export to Excel/Power BI for sharing

### Risk Governance
- ✅ Transparent calculation methodology
- ✅ Standardized KRI definitions
- ✅ Automated, objective calculations
- ✅ Clear accountability for breaches

### Event Identification & Risk Assessment
- ✅ Early warning indicators
- ✅ Migration matrix for trend detection
- ✅ Concentration monitoring
- ✅ Vintage analysis for underwriting quality

---

## KRI Metrics Reference

| KRI | Formula | Threshold | Current |
|-----|---------|-----------|---------|
| NPL Ratio | (NPL Balance / Total) × 100% | < 3.0% | 0.77% ✅ |
| PAR30 | (DPD≥30 Balance / Total) × 100% | < 5.0% | 2.23% ✅ |
| PAR90 | (DPD≥90 Balance / Total) × 100% | < 3.5% | 0.77% ✅ |
| Industry Conc. | Top Industry % | < 25.0% | 23.43% ✅ |
| Province Conc. | Top Province % | < 40.0% | 29.94% ✅ |

---

## Loan Classification System

Theo Circular 02/2013/TT-NHNN:

| Classification | DPD | NPL | Description |
|---------------|-----|-----|-------------|
| Nhóm 1 - Bình thường | 0 | No | Current, performing |
| Nhóm 2 - Cần chú ý | 1-30 | No | Watch list |
| Nhóm 3 - Dưới tiêu chuẩn | 31-89 | No | Substandard |
| Nhóm 4 - Nghi ngờ | 90-179 | **Yes** | Doubtful |
| Nhóm 5 - Tổn thất | 180+ | **Yes** | Loss |

**NPL = Nhóm 4 + Nhóm 5**
