"""
Excel Report Generator for KRI Dashboard
Creates formatted Excel workbook with metrics, charts, and Power BI ready data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
sys.path.append('/home/claude')
from kri_calculator import CreditRiskKRI
import warnings
warnings.filterwarnings('ignore')


def create_excel_report(df, df_timeseries):
    """Create comprehensive Excel report with KRI metrics"""
    
    print("Creating Excel report...")
    
    # Initialize KRI calculator
    kri_calc = CreditRiskKRI(df)
    kris = kri_calc.calculate_all_kris()
    
    # Create Excel writer
    excel_file = '/mnt/user-data/outputs/kri_report.xlsx'
    writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    workbook = writer.book
    
    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#003366',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'bg_color': '#E0E0E0',
        'border': 1
    })
    
    number_format = workbook.add_format({'num_format': '#,##0.00'})
    percent_format = workbook.add_format({'num_format': '0.00%'})
    currency_format = workbook.add_format({'num_format': '#,##0'})
    
    green_format = workbook.add_format({
        'bg_color': '#C6EFCE',
        'font_color': '#006100'
    })
    
    red_format = workbook.add_format({
        'bg_color': '#FFC7CE',
        'font_color': '#9C0006'
    })
    
    yellow_format = workbook.add_format({
        'bg_color': '#FFEB9C',
        'font_color': '#9C6500'
    })
    
    # 1. Executive Summary
    print("  Creating Executive Summary...")
    summary_data = []
    
    npl = kris['npl_metrics']
    par = kris['par_metrics']
    conc = kris['concentration_risk']
    ewi = kris['early_warning']
    
    summary_data.append(['KRI Metric', 'Current Value', 'Risk Appetite', 'Status', 'Utilization %'])
    summary_data.append(['NPL Ratio', npl['npl_balance_ratio'] / 100, npl['risk_appetite_limit'] / 100, 
                         'PASS' if npl['within_risk_appetite'] else 'BREACH',
                         npl['risk_appetite_utilization'] / 100])
    summary_data.append(['PAR30', par['par30']['ratio'] / 100, par['par30']['risk_appetite_limit'] / 100,
                         'PASS' if par['par30']['within_risk_appetite'] else 'BREACH',
                         (par['par30']['ratio'] / par['par30']['risk_appetite_limit'])])
    summary_data.append(['PAR90', par['par90']['ratio'] / 100, par['par90']['risk_appetite_limit'] / 100,
                         'PASS' if par['par90']['within_risk_appetite'] else 'BREACH',
                         (par['par90']['ratio'] / par['par90']['risk_appetite_limit'])])
    summary_data.append(['Industry Concentration', conc['industry']['top_industry'] / 100, 
                         kri_calc.risk_appetite['industry_concentration_max'] / 100,
                         'PASS' if conc['industry']['within_risk_appetite'] else 'BREACH',
                         (conc['industry']['top_industry'] / kri_calc.risk_appetite['industry_concentration_max'])])
    summary_data.append(['Province Concentration', conc['province']['top_province'] / 100,
                         kri_calc.risk_appetite['province_concentration_max'] / 100,
                         'PASS' if conc['province']['within_risk_appetite'] else 'BREACH',
                         (conc['province']['top_province'] / kri_calc.risk_appetite['province_concentration_max'])])
    
    summary_df = pd.DataFrame(summary_data[1:], columns=summary_data[0])
    summary_df.to_excel(writer, sheet_name='Executive Summary', index=False, startrow=2)
    
    worksheet = writer.sheets['Executive Summary']
    worksheet.write(0, 0, 'CREDIT RISK KRI - EXECUTIVE SUMMARY', title_format)
    worksheet.write(1, 0, f'Report Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    
    # Format headers
    for col_num, value in enumerate(summary_df.columns.values):
        worksheet.write(2, col_num, value, header_format)
    
    # Format values
    worksheet.set_column('B:B', 15, percent_format)
    worksheet.set_column('C:C', 15, percent_format)
    worksheet.set_column('E:E', 15, percent_format)
    
    # Conditional formatting for status
    for row in range(3, 3 + len(summary_df)):
        status = summary_df.iloc[row-3]['Status']
        if status == 'PASS':
            worksheet.write(row, 3, status, green_format)
        else:
            worksheet.write(row, 3, status, red_format)
        
        # Utilization color
        util = summary_df.iloc[row-3]['Utilization %']
        if util < 0.7:
            worksheet.write(row, 4, util, green_format)
        elif util < 0.9:
            worksheet.write(row, 4, util, yellow_format)
        else:
            worksheet.write(row, 4, util, red_format)
    
    # Add portfolio overview
    worksheet.write(10, 0, 'Portfolio Overview', title_format)
    overview_data = [
        ['Total Loans', npl['total_loans']],
        ['Total Outstanding', f"{npl['total_balance']/1e6:.2f}B VND"],
        ['NPL Count', npl['npl_count']],
        ['NPL Balance', f"{npl['npl_balance']/1e6:.2f}B VND"],
        ['Early Delinquency (1-29 DPD)', ewi['early_delinquency']['count']],
        ['Watch List (Nhóm 2)', ewi['watch_list']['count']]
    ]
    
    for idx, (metric, value) in enumerate(overview_data):
        worksheet.write(11 + idx, 0, metric)
        if isinstance(value, str):
            worksheet.write(11 + idx, 1, value)
        else:
            worksheet.write(11 + idx, 1, value, currency_format)
    
    # 2. NPL Analysis
    print("  Creating NPL Analysis...")
    
    # NPL by Segment
    npl['by_segment'].to_excel(writer, sheet_name='NPL by Segment', index=False)
    worksheet = writer.sheets['NPL by Segment']
    for col_num, value in enumerate(npl['by_segment'].columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('B:C', 18, number_format)
    worksheet.set_column('D:D', 12, number_format)
    
    # NPL by Product
    npl['by_product'].to_excel(writer, sheet_name='NPL by Product', index=False)
    worksheet = writer.sheets['NPL by Product']
    for col_num, value in enumerate(npl['by_product'].columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('B:C', 18, number_format)
    worksheet.set_column('D:D', 12, number_format)
    
    # NPL by Industry
    npl['by_industry'].to_excel(writer, sheet_name='NPL by Industry', index=False)
    worksheet = writer.sheets['NPL by Industry']
    for col_num, value in enumerate(npl['by_industry'].columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('B:C', 18, number_format)
    worksheet.set_column('D:D', 12, number_format)
    
    # NPL by Province
    npl['by_province'].to_excel(writer, sheet_name='NPL by Province', index=False)
    worksheet = writer.sheets['NPL by Province']
    for col_num, value in enumerate(npl['by_province'].columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('B:C', 18, number_format)
    worksheet.set_column('D:D', 12, number_format)
    
    # 3. PAR Analysis
    print("  Creating PAR Analysis...")
    par_summary = par['by_segment'].copy()
    par_summary.to_excel(writer, sheet_name='PAR Analysis', index=False)
    
    worksheet = writer.sheets['PAR Analysis']
    for col_num, value in enumerate(par_summary.columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('B:C', 15, number_format)
    
    # 4. Portfolio Quality
    print("  Creating Portfolio Quality...")
    quality = kris['quality_distribution']
    quality.to_excel(writer, sheet_name='Portfolio Quality', index=False)
    
    worksheet = writer.sheets['Portfolio Quality']
    for col_num, value in enumerate(quality.columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('C:C', 18, number_format)
    worksheet.set_column('D:E', 12, number_format)
    
    # 5. Concentration Risk
    print("  Creating Concentration Risk...")
    
    # Industry concentration
    industry_conc = pd.DataFrame(list(conc['industry']['details'].items()), 
                                 columns=['Industry', 'Concentration %'])
    industry_conc = industry_conc.sort_values('Concentration %', ascending=False)
    industry_conc.to_excel(writer, sheet_name='Concentration - Industry', index=False)
    
    worksheet = writer.sheets['Concentration - Industry']
    for col_num, value in enumerate(industry_conc.columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('B:B', 18, number_format)
    
    # Province concentration
    province_conc = pd.DataFrame(list(conc['province']['details'].items()),
                                 columns=['Province', 'Concentration %'])
    province_conc = province_conc.sort_values('Concentration %', ascending=False)
    province_conc.to_excel(writer, sheet_name='Concentration - Province', index=False)
    
    worksheet = writer.sheets['Concentration - Province']
    for col_num, value in enumerate(province_conc.columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('B:B', 18, number_format)
    
    # 6. Vintage Analysis
    print("  Creating Vintage Analysis...")
    vintage = kris['vintage_analysis']
    vintage.to_excel(writer, sheet_name='Vintage Analysis', index=False)
    
    worksheet = writer.sheets['Vintage Analysis']
    for col_num, value in enumerate(vintage.columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('C:D', 18, number_format)
    worksheet.set_column('E:F', 12, number_format)
    
    # 7. Segment Performance
    print("  Creating Segment Performance...")
    segment_perf = kris['segment_performance']
    segment_perf.to_excel(writer, sheet_name='Segment Performance', index=False)
    
    worksheet = writer.sheets['Segment Performance']
    for col_num, value in enumerate(segment_perf.columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('C:D', 18, number_format)
    worksheet.set_column('E:H', 12, number_format)
    
    # 8. Migration Matrix
    print("  Creating Migration Matrix...")
    if df_timeseries is not None:
        migration = kri_calc.calculate_migration_matrix(df_timeseries)
        if migration is not None:
            migration.to_excel(writer, sheet_name='Migration Matrix')
            
            worksheet = writer.sheets['Migration Matrix']
            worksheet.write(0, 0, 'From Class (rows) → To Class (columns)', title_format)
            worksheet.set_column('B:F', 20, number_format)
    
    # 9. Time Series Data for Power BI
    print("  Creating Time Series data...")
    
    # Calculate metrics by snapshot
    ts_metrics = df_timeseries.groupby('snapshot_date').apply(
        lambda x: pd.Series({
            'total_loans': len(x),
            'total_balance': x['outstanding_balance_vnd_mil'].sum(),
            'npl_count': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])].shape[0],
            'npl_balance': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])]['outstanding_balance_vnd_mil'].sum(),
            'npl_ratio': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])]['outstanding_balance_vnd_mil'].sum() / x['outstanding_balance_vnd_mil'].sum() * 100,
            'par30_count': x[x['days_past_due'] >= 30].shape[0],
            'par30_balance': x[x['days_past_due'] >= 30]['outstanding_balance_vnd_mil'].sum(),
            'par30_ratio': x[x['days_past_due'] >= 30]['outstanding_balance_vnd_mil'].sum() / x['outstanding_balance_vnd_mil'].sum() * 100,
            'par90_count': x[x['days_past_due'] >= 90].shape[0],
            'par90_balance': x[x['days_past_due'] >= 90]['outstanding_balance_vnd_mil'].sum(),
            'par90_ratio': x[x['days_past_due'] >= 90]['outstanding_balance_vnd_mil'].sum() / x['outstanding_balance_vnd_mil'].sum() * 100
        })
    ).reset_index()
    
    ts_metrics.to_excel(writer, sheet_name='Time Series', index=False)
    
    worksheet = writer.sheets['Time Series']
    for col_num, value in enumerate(ts_metrics.columns.values):
        worksheet.write(0, col_num, value, header_format)
    worksheet.set_column('B:K', 15, number_format)
    
    # 10. Raw Data for Power BI
    print("  Creating Raw Data...")
    df_sample = df.head(1000)  # Sample for Excel size
    df_sample.to_excel(writer, sheet_name='Raw Data (Sample)', index=False)
    
    worksheet = writer.sheets['Raw Data (Sample)']
    for col_num, value in enumerate(df_sample.columns.values):
        worksheet.write(0, col_num, value, header_format)
    
    # 11. Instructions & COSO Alignment
    print("  Creating Instructions...")
    instructions = [
        ['CREDIT RISK KRI DASHBOARD - USER GUIDE'],
        [''],
        ['Dashboard Components:'],
        ['1. Executive Summary - Key metrics vs risk appetite'],
        ['2. NPL Analysis - Non-performing loan breakdown by segment/product/geography'],
        ['3. PAR Analysis - Portfolio at Risk (30/60/90/180 days)'],
        ['4. Portfolio Quality - Distribution across 5 loan classifications'],
        ['5. Concentration Risk - Industry and geographic exposure'],
        ['6. Vintage Analysis - Performance by origination cohort'],
        ['7. Segment Performance - Detailed metrics by customer segment'],
        ['8. Migration Matrix - Transition between loan classifications'],
        ['9. Time Series - Historical trends for Power BI/Tableau'],
        ['10. Raw Data - Sample loan-level data'],
        [''],
        ['COSO ERM Framework Alignment:'],
        [''],
        ['Performance Component:'],
        ['- Continuous monitoring of credit risk through quantitative KRIs'],
        ['- NPL ratio, PAR metrics tracked against risk appetite thresholds'],
        ['- Automated alerts when metrics breach defined limits'],
        [''],
        ['Information, Communication & Reporting:'],
        ['- Real-time dashboard provides actionable insights to stakeholders'],
        ['- Multi-dimensional risk breakdown (segment, product, geography, vintage)'],
        ['- Migration matrix shows portfolio quality trends over time'],
        ['- Excel format enables easy sharing and integration with existing systems'],
        [''],
        ['Risk Governance:'],
        ['- Risk appetite framework clearly defined (e.g., NPL < 3%, PAR30 < 5%)'],
        ['- Traffic light system (PASS/BREACH) for immediate risk identification'],
        ['- Utilization % shows proximity to limits for early warning'],
        [''],
        ['Decision Support:'],
        ['- Concentration metrics identify over-exposure to industries/provinces'],
        ['- Vintage analysis reveals cohorts requiring attention'],
        ['- Segment performance guides pricing and underwriting strategy'],
        [''],
        ['Power BI / Tableau Integration:'],
        ['- Use "Time Series" sheet for trend visualizations'],
        ['- Use "Raw Data" sheet for detailed drill-down analysis'],
        ['- All metrics pre-calculated for easy charting'],
        [''],
        ['Contact: VPBank Credit Risk Team'],
        [f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}']
    ]
    
    instructions_df = pd.DataFrame(instructions)
    instructions_df.to_excel(writer, sheet_name='Instructions', index=False, header=False)
    
    worksheet = writer.sheets['Instructions']
    worksheet.set_column('A:A', 80)
    
    # Close writer
    writer.close()
    
    print(f"✓ Excel report saved to: {excel_file}")
    
    return excel_file


def main():
    """Generate Excel report"""
    
    print("=" * 80)
    print("EXCEL KRI REPORT GENERATOR")
    print("=" * 80)
    print()
    
    # Load data
    df = pd.read_csv('/mnt/user-data/outputs/loan_portfolio_current.csv')
    df_ts = pd.read_csv('/mnt/user-data/outputs/loan_portfolio_timeseries.csv')
    
    # Parse dates
    df['origination_date'] = pd.to_datetime(df['origination_date'])
    df_ts['origination_date'] = pd.to_datetime(df_ts['origination_date'])
    df_ts['snapshot_date'] = pd.to_datetime(df_ts['snapshot_date'])
    
    # Create Excel report
    excel_file = create_excel_report(df, df_ts)
    
    print()
    print("=" * 80)
    print("EXCEL REPORT GENERATION COMPLETE")
    print("=" * 80)
    print()
    print("The report includes:")
    print("  • Executive Summary with risk appetite status")
    print("  • NPL analysis by segment/product/industry/province")
    print("  • PAR metrics (30/60/90/180 days)")
    print("  • Portfolio quality distribution")
    print("  • Concentration risk analysis")
    print("  • Vintage and segment performance")
    print("  • Migration matrix")
    print("  • Time series data for Power BI/Tableau")
    print("  • COSO ERM framework alignment documentation")
    print()
    print("Open in Excel or import to Power BI/Tableau for interactive analysis")


if __name__ == "__main__":
    main()
