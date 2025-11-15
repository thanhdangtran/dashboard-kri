"""
Key Risk Indicators (KRI) Calculator for Credit Risk
Includes: NPL ratios, PAR metrics, migration matrix, and concentration risks
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class CreditRiskKRI:
    """Calculate comprehensive credit risk KRIs"""
    
    def __init__(self, df):
        """
        Initialize with loan portfolio dataframe
        
        Parameters:
        -----------
        df : pandas.DataFrame
            Loan portfolio data with required fields
        """
        self.df = df.copy()
        self.current_date = datetime(2025, 11, 15)
        
        # Risk appetite thresholds (VPBank policy)
        self.risk_appetite = {
            'npl_ratio_max': 3.0,           # NPL < 3%
            'par30_ratio_max': 5.0,          # PAR30 < 5%
            'par90_ratio_max': 3.5,          # PAR90 < 3.5%
            'single_borrower_max': 15.0,     # Single exposure < 15%
            'industry_concentration_max': 25.0,  # Industry < 25%
            'province_concentration_max': 40.0   # Province < 40%
        }
    
    def calculate_all_kris(self):
        """Calculate all KRI metrics"""
        
        kris = {}
        
        # Core NPL metrics
        kris['npl_metrics'] = self.calculate_npl_metrics()
        
        # PAR metrics
        kris['par_metrics'] = self.calculate_par_metrics()
        
        # Portfolio quality distribution
        kris['quality_distribution'] = self.calculate_quality_distribution()
        
        # Concentration risks
        kris['concentration_risk'] = self.calculate_concentration_risk()
        
        # Vintage analysis
        kris['vintage_analysis'] = self.calculate_vintage_analysis()
        
        # Segment performance
        kris['segment_performance'] = self.calculate_segment_performance()
        
        # Early warning indicators
        kris['early_warning'] = self.calculate_early_warning_indicators()
        
        return kris
    
    def calculate_npl_metrics(self):
        """Calculate NPL (Non-Performing Loan) metrics"""
        
        # Define NPL (Nhóm 4 + Nhóm 5 or DPD >= 90)
        npl_mask = (
            self.df['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất']) |
            (self.df['days_past_due'] >= 90)
        )
        
        total_loans = len(self.df)
        total_balance = self.df['outstanding_balance_vnd_mil'].sum()
        
        npl_loans = npl_mask.sum()
        npl_balance = self.df[npl_mask]['outstanding_balance_vnd_mil'].sum()
        
        metrics = {
            'npl_count': int(npl_loans),
            'npl_count_ratio': npl_loans / total_loans * 100,
            'npl_balance': npl_balance,
            'npl_balance_ratio': npl_balance / total_balance * 100,
            'total_loans': int(total_loans),
            'total_balance': total_balance,
            'within_risk_appetite': npl_balance / total_balance * 100 < self.risk_appetite['npl_ratio_max'],
            'risk_appetite_limit': self.risk_appetite['npl_ratio_max'],
            'risk_appetite_utilization': (npl_balance / total_balance * 100) / self.risk_appetite['npl_ratio_max'] * 100
        }
        
        # NPL by segment
        npl_by_segment = self.df.groupby('customer_segment').apply(
            lambda x: pd.Series({
                'total_balance': x['outstanding_balance_vnd_mil'].sum(),
                'npl_balance': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])]['outstanding_balance_vnd_mil'].sum(),
                'npl_ratio': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])]['outstanding_balance_vnd_mil'].sum() / x['outstanding_balance_vnd_mil'].sum() * 100 if x['outstanding_balance_vnd_mil'].sum() > 0 else 0
            })
        ).reset_index()
        
        metrics['by_segment'] = npl_by_segment
        
        # NPL by product
        npl_by_product = self.df.groupby('loan_type').apply(
            lambda x: pd.Series({
                'total_balance': x['outstanding_balance_vnd_mil'].sum(),
                'npl_balance': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])]['outstanding_balance_vnd_mil'].sum(),
                'npl_ratio': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])]['outstanding_balance_vnd_mil'].sum() / x['outstanding_balance_vnd_mil'].sum() * 100 if x['outstanding_balance_vnd_mil'].sum() > 0 else 0
            })
        ).reset_index()
        
        metrics['by_product'] = npl_by_product
        
        # NPL by industry
        npl_by_industry = self.df.groupby('industry').apply(
            lambda x: pd.Series({
                'total_balance': x['outstanding_balance_vnd_mil'].sum(),
                'npl_balance': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])]['outstanding_balance_vnd_mil'].sum(),
                'npl_ratio': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])]['outstanding_balance_vnd_mil'].sum() / x['outstanding_balance_vnd_mil'].sum() * 100 if x['outstanding_balance_vnd_mil'].sum() > 0 else 0
            })
        ).reset_index()
        
        metrics['by_industry'] = npl_by_industry
        
        # NPL by province
        npl_by_province = self.df.groupby('province').apply(
            lambda x: pd.Series({
                'total_balance': x['outstanding_balance_vnd_mil'].sum(),
                'npl_balance': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])]['outstanding_balance_vnd_mil'].sum(),
                'npl_ratio': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])]['outstanding_balance_vnd_mil'].sum() / x['outstanding_balance_vnd_mil'].sum() * 100 if x['outstanding_balance_vnd_mil'].sum() > 0 else 0
            })
        ).reset_index()
        
        metrics['by_province'] = npl_by_province
        
        return metrics
    
    def calculate_par_metrics(self):
        """Calculate Portfolio at Risk (PAR) metrics"""
        
        total_balance = self.df['outstanding_balance_vnd_mil'].sum()
        
        # PAR 30 (DPD >= 30)
        par30_mask = self.df['days_past_due'] >= 30
        par30_balance = self.df[par30_mask]['outstanding_balance_vnd_mil'].sum()
        par30_ratio = par30_balance / total_balance * 100
        
        # PAR 60 (DPD >= 60)
        par60_mask = self.df['days_past_due'] >= 60
        par60_balance = self.df[par60_mask]['outstanding_balance_vnd_mil'].sum()
        par60_ratio = par60_balance / total_balance * 100
        
        # PAR 90 (DPD >= 90)
        par90_mask = self.df['days_past_due'] >= 90
        par90_balance = self.df[par90_mask]['outstanding_balance_vnd_mil'].sum()
        par90_ratio = par90_balance / total_balance * 100
        
        # PAR 180 (DPD >= 180)
        par180_mask = self.df['days_past_due'] >= 180
        par180_balance = self.df[par180_mask]['outstanding_balance_vnd_mil'].sum()
        par180_ratio = par180_balance / total_balance * 100
        
        metrics = {
            'par30': {
                'balance': par30_balance,
                'ratio': par30_ratio,
                'count': int(par30_mask.sum()),
                'within_risk_appetite': par30_ratio < self.risk_appetite['par30_ratio_max'],
                'risk_appetite_limit': self.risk_appetite['par30_ratio_max']
            },
            'par60': {
                'balance': par60_balance,
                'ratio': par60_ratio,
                'count': int(par60_mask.sum())
            },
            'par90': {
                'balance': par90_balance,
                'ratio': par90_ratio,
                'count': int(par90_mask.sum()),
                'within_risk_appetite': par90_ratio < self.risk_appetite['par90_ratio_max'],
                'risk_appetite_limit': self.risk_appetite['par90_ratio_max']
            },
            'par180': {
                'balance': par180_balance,
                'ratio': par180_ratio,
                'count': int(par180_mask.sum())
            }
        }
        
        # PAR by segment
        par_by_segment = self.df.groupby('customer_segment').apply(
            lambda x: pd.Series({
                'par30_ratio': x[x['days_past_due'] >= 30]['outstanding_balance_vnd_mil'].sum() / x['outstanding_balance_vnd_mil'].sum() * 100 if x['outstanding_balance_vnd_mil'].sum() > 0 else 0,
                'par90_ratio': x[x['days_past_due'] >= 90]['outstanding_balance_vnd_mil'].sum() / x['outstanding_balance_vnd_mil'].sum() * 100 if x['outstanding_balance_vnd_mil'].sum() > 0 else 0
            })
        ).reset_index()
        
        metrics['by_segment'] = par_by_segment
        
        return metrics
    
    def calculate_quality_distribution(self):
        """Calculate distribution across loan classifications"""
        
        total_balance = self.df['outstanding_balance_vnd_mil'].sum()
        
        distribution = self.df.groupby('loan_classification').agg({
            'loan_id': 'count',
            'outstanding_balance_vnd_mil': 'sum'
        }).reset_index()
        
        distribution.columns = ['classification', 'count', 'balance']
        distribution['count_pct'] = distribution['count'] / distribution['count'].sum() * 100
        distribution['balance_pct'] = distribution['balance'] / distribution['balance'].sum() * 100
        
        # Sort by classification order
        class_order = [
            'Nhóm 1 - Bình thường',
            'Nhóm 2 - Cần chú ý',
            'Nhóm 3 - Dưới tiêu chuẩn',
            'Nhóm 4 - Nghi ngờ',
            'Nhóm 5 - Tổn thất'
        ]
        
        distribution['sort_order'] = distribution['classification'].map({c: i for i, c in enumerate(class_order)})
        distribution = distribution.sort_values('sort_order').drop('sort_order', axis=1)
        
        return distribution
    
    def calculate_concentration_risk(self):
        """Calculate concentration risk metrics"""
        
        total_balance = self.df['outstanding_balance_vnd_mil'].sum()
        
        # Industry concentration
        industry_conc = self.df.groupby('industry')['outstanding_balance_vnd_mil'].sum().sort_values(ascending=False)
        industry_conc_pct = industry_conc / total_balance * 100
        
        top_industry = industry_conc_pct.iloc[0]
        top_3_industries = industry_conc_pct.iloc[:3].sum()
        
        # Province concentration
        province_conc = self.df.groupby('province')['outstanding_balance_vnd_mil'].sum().sort_values(ascending=False)
        province_conc_pct = province_conc / total_balance * 100
        
        top_province = province_conc_pct.iloc[0]
        top_3_provinces = province_conc_pct.iloc[:3].sum()
        
        # Product concentration
        product_conc = self.df.groupby('loan_type')['outstanding_balance_vnd_mil'].sum().sort_values(ascending=False)
        product_conc_pct = product_conc / total_balance * 100
        
        # Segment concentration
        segment_conc = self.df.groupby('customer_segment')['outstanding_balance_vnd_mil'].sum().sort_values(ascending=False)
        segment_conc_pct = segment_conc / total_balance * 100
        
        # HHI (Herfindahl-Hirschman Index) - measure of concentration
        # HHI = sum of squared market shares; closer to 10000 = more concentrated
        industry_hhi = (industry_conc_pct ** 2).sum()
        province_hhi = (province_conc_pct ** 2).sum()
        
        metrics = {
            'industry': {
                'top_industry': top_industry,
                'top_3_total': top_3_industries,
                'hhi': industry_hhi,
                'concentration_level': 'High' if industry_hhi > 2500 else 'Moderate' if industry_hhi > 1500 else 'Low',
                'within_risk_appetite': top_industry < self.risk_appetite['industry_concentration_max'],
                'details': industry_conc_pct.to_dict()
            },
            'province': {
                'top_province': top_province,
                'top_3_total': top_3_provinces,
                'hhi': province_hhi,
                'concentration_level': 'High' if province_hhi > 2500 else 'Moderate' if province_hhi > 1500 else 'Low',
                'within_risk_appetite': top_province < self.risk_appetite['province_concentration_max'],
                'details': province_conc_pct.to_dict()
            },
            'product': {
                'details': product_conc_pct.to_dict()
            },
            'segment': {
                'details': segment_conc_pct.to_dict()
            }
        }
        
        return metrics
    
    def calculate_vintage_analysis(self):
        """Analyze performance by vintage (origination cohort)"""
        
        vintage_perf = self.df.groupby('vintage').apply(
            lambda x: pd.Series({
                'total_loans': len(x),
                'total_balance': x['outstanding_balance_vnd_mil'].sum(),
                'npl_count': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])].shape[0],
                'npl_balance': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])]['outstanding_balance_vnd_mil'].sum(),
                'npl_ratio': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])]['outstanding_balance_vnd_mil'].sum() / x['outstanding_balance_vnd_mil'].sum() * 100 if x['outstanding_balance_vnd_mil'].sum() > 0 else 0,
                'avg_dpd': x['days_past_due'].mean()
            })
        ).reset_index()
        
        return vintage_perf
    
    def calculate_segment_performance(self):
        """Detailed performance by customer segment"""
        
        segment_perf = self.df.groupby('customer_segment').apply(
            lambda x: pd.Series({
                'total_loans': len(x),
                'total_balance': x['outstanding_balance_vnd_mil'].sum(),
                'avg_loan_size': x['outstanding_balance_vnd_mil'].mean(),
                'avg_interest_rate': x['interest_rate_pct'].mean(),
                'npl_count': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])].shape[0],
                'npl_ratio': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])]['outstanding_balance_vnd_mil'].sum() / x['outstanding_balance_vnd_mil'].sum() * 100 if x['outstanding_balance_vnd_mil'].sum() > 0 else 0,
                'par30_ratio': x[x['days_past_due'] >= 30]['outstanding_balance_vnd_mil'].sum() / x['outstanding_balance_vnd_mil'].sum() * 100 if x['outstanding_balance_vnd_mil'].sum() > 0 else 0,
                'avg_dpd': x['days_past_due'].mean(),
                'avg_months_on_book': x['months_on_book'].mean()
            })
        ).reset_index()
        
        return segment_perf
    
    def calculate_early_warning_indicators(self):
        """Calculate early warning signals"""
        
        # Loans with increasing DPD (early delinquency)
        early_delinquency_mask = (self.df['days_past_due'] > 0) & (self.df['days_past_due'] < 30)
        early_delinquency_count = early_delinquency_mask.sum()
        early_delinquency_balance = self.df[early_delinquency_mask]['outstanding_balance_vnd_mil'].sum()
        
        # Watch list (Nhóm 2)
        watch_list_mask = self.df['loan_classification'] == 'Nhóm 2 - Cần chú ý'
        watch_list_count = watch_list_mask.sum()
        watch_list_balance = self.df[watch_list_mask]['outstanding_balance_vnd_mil'].sum()
        
        # Recently originated loans (< 6 months) with issues
        new_loans_mask = self.df['months_on_book'] < 6
        new_loans_with_issues = self.df[new_loans_mask & (self.df['days_past_due'] > 0)]
        
        total_balance = self.df['outstanding_balance_vnd_mil'].sum()
        
        indicators = {
            'early_delinquency': {
                'count': int(early_delinquency_count),
                'balance': early_delinquency_balance,
                'ratio': early_delinquency_balance / total_balance * 100
            },
            'watch_list': {
                'count': int(watch_list_count),
                'balance': watch_list_balance,
                'ratio': watch_list_balance / total_balance * 100
            },
            'new_loans_issues': {
                'count': len(new_loans_with_issues),
                'balance': new_loans_with_issues['outstanding_balance_vnd_mil'].sum(),
                'ratio': new_loans_with_issues['outstanding_balance_vnd_mil'].sum() / total_balance * 100
            }
        }
        
        return indicators
    
    def calculate_migration_matrix(self, df_historical):
        """
        Calculate migration matrix between loan classifications
        
        Parameters:
        -----------
        df_historical : DataFrame
            Historical loan data with snapshot_date
        """
        
        # Get two consecutive snapshots
        snapshots = sorted(df_historical['snapshot_date'].unique(), reverse=True)
        
        if len(snapshots) < 2:
            return None
        
        current_snapshot = snapshots[0]
        previous_snapshot = snapshots[1]
        
        df_current = df_historical[df_historical['snapshot_date'] == current_snapshot][['loan_id', 'loan_classification']]
        df_previous = df_historical[df_historical['snapshot_date'] == previous_snapshot][['loan_id', 'loan_classification']]
        
        df_current.columns = ['loan_id', 'current_class']
        df_previous.columns = ['loan_id', 'previous_class']
        
        # Merge to get transitions
        df_transitions = pd.merge(df_previous, df_current, on='loan_id', how='inner')
        
        # Create migration matrix
        migration_matrix = pd.crosstab(
            df_transitions['previous_class'],
            df_transitions['current_class'],
            normalize='index'
        ) * 100  # Convert to percentages
        
        # Ensure all classes are present
        all_classes = [
            'Nhóm 1 - Bình thường',
            'Nhóm 2 - Cần chú ý',
            'Nhóm 3 - Dưới tiêu chuẩn',
            'Nhóm 4 - Nghi ngờ',
            'Nhóm 5 - Tổn thất'
        ]
        
        for cls in all_classes:
            if cls not in migration_matrix.index:
                migration_matrix.loc[cls] = 0
            if cls not in migration_matrix.columns:
                migration_matrix[cls] = 0
        
        migration_matrix = migration_matrix.loc[all_classes, all_classes]
        
        return migration_matrix


def generate_kri_report(df, df_timeseries=None):
    """Generate comprehensive KRI report"""
    
    print("=" * 80)
    print("CREDIT RISK KRI REPORT")
    print("=" * 80)
    print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Portfolio as of: 2025-11-15")
    print()
    
    # Initialize KRI calculator
    kri_calc = CreditRiskKRI(df)
    kris = kri_calc.calculate_all_kris()
    
    # 1. NPL Metrics
    print("\n" + "=" * 80)
    print("1. NPL (NON-PERFORMING LOAN) METRICS")
    print("=" * 80)
    
    npl = kris['npl_metrics']
    print(f"\nOverall NPL Ratio: {npl['npl_balance_ratio']:.2f}%")
    print(f"Risk Appetite Limit: {npl['risk_appetite_limit']:.2f}%")
    print(f"Status: {'✓ PASS' if npl['within_risk_appetite'] else '✗ BREACH'}")
    print(f"Utilization: {npl['risk_appetite_utilization']:.1f}% of limit")
    
    print(f"\nNPL Count: {npl['npl_count']:,} loans ({npl['npl_count_ratio']:.2f}%)")
    print(f"NPL Balance: {npl['npl_balance']/1e6:,.2f}B VND")
    
    print("\nNPL by Segment:")
    print(npl['by_segment'].sort_values('npl_ratio', ascending=False).to_string(index=False))
    
    print("\nNPL by Product:")
    print(npl['by_product'].sort_values('npl_ratio', ascending=False).to_string(index=False))
    
    # 2. PAR Metrics
    print("\n" + "=" * 80)
    print("2. PORTFOLIO AT RISK (PAR) METRICS")
    print("=" * 80)
    
    par = kris['par_metrics']
    print(f"\nPAR30: {par['par30']['ratio']:.2f}% | Limit: {par['par30']['risk_appetite_limit']:.2f}% | {'✓ PASS' if par['par30']['within_risk_appetite'] else '✗ BREACH'}")
    print(f"PAR60: {par['par60']['ratio']:.2f}%")
    print(f"PAR90: {par['par90']['ratio']:.2f}% | Limit: {par['par90']['risk_appetite_limit']:.2f}% | {'✓ PASS' if par['par90']['within_risk_appetite'] else '✗ BREACH'}")
    print(f"PAR180: {par['par180']['ratio']:.2f}%")
    
    print("\nPAR by Segment:")
    print(par['by_segment'].to_string(index=False))
    
    # 3. Portfolio Quality
    print("\n" + "=" * 80)
    print("3. PORTFOLIO QUALITY DISTRIBUTION")
    print("=" * 80)
    
    quality = kris['quality_distribution']
    print(quality.to_string(index=False))
    
    # 4. Concentration Risk
    print("\n" + "=" * 80)
    print("4. CONCENTRATION RISK")
    print("=" * 80)
    
    conc = kris['concentration_risk']
    print(f"\nIndustry Concentration:")
    print(f"  Top Industry: {conc['industry']['top_industry']:.2f}% | Limit: {kri_calc.risk_appetite['industry_concentration_max']:.2f}%")
    print(f"  Top 3 Industries: {conc['industry']['top_3_total']:.2f}%")
    print(f"  HHI: {conc['industry']['hhi']:.0f} ({conc['industry']['concentration_level']})")
    print(f"  Status: {'✓ PASS' if conc['industry']['within_risk_appetite'] else '✗ BREACH'}")
    
    print(f"\nProvince Concentration:")
    print(f"  Top Province: {conc['province']['top_province']:.2f}% | Limit: {kri_calc.risk_appetite['province_concentration_max']:.2f}%")
    print(f"  Top 3 Provinces: {conc['province']['top_3_total']:.2f}%")
    print(f"  HHI: {conc['province']['hhi']:.0f} ({conc['province']['concentration_level']})")
    print(f"  Status: {'✓ PASS' if conc['province']['within_risk_appetite'] else '✗ BREACH'}")
    
    # 5. Early Warning Indicators
    print("\n" + "=" * 80)
    print("5. EARLY WARNING INDICATORS")
    print("=" * 80)
    
    ewi = kris['early_warning']
    print(f"\nEarly Delinquency (1-29 DPD):")
    print(f"  Count: {ewi['early_delinquency']['count']:,}")
    print(f"  Ratio: {ewi['early_delinquency']['ratio']:.2f}%")
    
    print(f"\nWatch List (Nhóm 2):")
    print(f"  Count: {ewi['watch_list']['count']:,}")
    print(f"  Ratio: {ewi['watch_list']['ratio']:.2f}%")
    
    print(f"\nNew Loans with Issues (< 6 months):")
    print(f"  Count: {ewi['new_loans_issues']['count']:,}")
    print(f"  Ratio: {ewi['new_loans_issues']['ratio']:.2f}%")
    
    # 6. Migration Matrix
    if df_timeseries is not None:
        print("\n" + "=" * 80)
        print("6. MIGRATION MATRIX (% transition between classes)")
        print("=" * 80)
        
        migration = kri_calc.calculate_migration_matrix(df_timeseries)
        if migration is not None:
            print("\nFrom (rows) → To (columns):")
            print(migration.round(1).to_string())
    
    print("\n" + "=" * 80)
    print("END OF KRI REPORT")
    print("=" * 80)
    
    return kris


if __name__ == "__main__":
    # Load data
    df = pd.read_csv('/mnt/user-data/outputs/loan_portfolio_current.csv')
    df_ts = pd.read_csv('/mnt/user-data/outputs/loan_portfolio_timeseries.csv')
    
    # Generate KRI report
    kris = generate_kri_report(df, df_ts)
