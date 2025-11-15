"""
Synthetic Loan Portfolio Data Generator for VPBank
Includes Vietnamese market characteristics: provinces, industries, Tet seasonality
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

class LoanPortfolioGenerator:
    """Generate realistic loan portfolio data for Vietnamese market"""
    
    def __init__(self, n_loans=10000):
        self.n_loans = n_loans
        self.current_date = datetime(2025, 11, 15)
        
        # Vietnamese provinces with economic weights
        self.provinces = {
            'TP. Hồ Chí Minh': 0.30,
            'Hà Nội': 0.25,
            'Bình Dương': 0.08,
            'Đồng Nai': 0.06,
            'Bà Rịa-Vũng Tàu': 0.04,
            'Hải Phòng': 0.05,
            'Đà Nẵng': 0.04,
            'Cần Thơ': 0.03,
            'Khánh Hòa': 0.02,
            'Khác': 0.13
        }
        
        # Industry sectors
        self.industries = {
            'Bán lẻ': 0.20,
            'Sản xuất': 0.18,
            'Dịch vụ': 0.15,
            'Bất động sản': 0.12,
            'Xây dựng': 0.10,
            'Nông nghiệp': 0.08,
            'Vận tải': 0.07,
            'F&B': 0.06,
            'Công nghệ': 0.04
        }
        
        # Loan products
        self.loan_types = {
            'Tiêu dùng': 0.35,
            'Kinh doanh SME': 0.30,
            'Thế chấp nhà': 0.20,
            'Ô tô': 0.10,
            'Corporate': 0.05
        }
        
        # Risk segments based on VPBank data
        self.segments = {
            'Prime': 0.40,      # Low risk, strong credit history
            'Standard': 0.35,   # Medium risk
            'Sub-prime': 0.20,  # Higher risk, thin file
            'NTB': 0.05        # New to bank, limited history
        }
        
    def generate_portfolio(self):
        """Generate complete loan portfolio"""
        
        # Basic loan information
        loan_ids = [f"LOAN{str(i).zfill(8)}" for i in range(1, self.n_loans + 1)]
        
        # Customer segments
        segments = np.random.choice(
            list(self.segments.keys()),
            size=self.n_loans,
            p=list(self.segments.values())
        )
        
        # Geographic distribution
        provinces = np.random.choice(
            list(self.provinces.keys()),
            size=self.n_loans,
            p=list(self.provinces.values())
        )
        
        # Industry distribution
        industries = np.random.choice(
            list(self.industries.keys()),
            size=self.n_loans,
            p=list(self.industries.values())
        )
        
        # Loan types
        loan_types = np.random.choice(
            list(self.loan_types.keys()),
            size=self.n_loans,
            p=list(self.loan_types.values())
        )
        
        # Loan amounts (VND millions) - vary by product type
        loan_amounts = []
        for lt in loan_types:
            if lt == 'Corporate':
                amount = np.random.lognormal(16, 1.5)  # 5-100B VND
            elif lt == 'Thế chấp nhà':
                amount = np.random.lognormal(14, 1)    # 500M-5B VND
            elif lt == 'Kinh doanh SME':
                amount = np.random.lognormal(13, 1.2)  # 200M-3B VND
            elif lt == 'Ô tô':
                amount = np.random.lognormal(12.5, 0.8) # 200M-1B VND
            else:  # Tiêu dùng
                amount = np.random.lognormal(11, 1)     # 50M-500M VND
            loan_amounts.append(amount)
        
        loan_amounts = np.array(loan_amounts)
        
        # Origination dates (last 36 months)
        days_ago = np.random.randint(0, 1095, self.n_loans)
        origination_dates = [self.current_date - timedelta(days=int(d)) for d in days_ago]
        
        # Terms (months)
        terms = []
        for lt in loan_types:
            if lt == 'Corporate':
                term = np.random.choice([36, 48, 60], p=[0.3, 0.4, 0.3])
            elif lt == 'Thế chấp nhà':
                term = np.random.choice([120, 180, 240], p=[0.3, 0.5, 0.2])
            elif lt == 'Kinh doanh SME':
                term = np.random.choice([12, 24, 36], p=[0.3, 0.4, 0.3])
            elif lt == 'Ô tô':
                term = np.random.choice([36, 48, 60], p=[0.4, 0.4, 0.2])
            else:  # Tiêu dùng
                term = np.random.choice([12, 24, 36], p=[0.4, 0.4, 0.2])
            terms.append(term)
        
        # Interest rates (% per year)
        interest_rates = []
        for seg, lt in zip(segments, loan_types):
            base_rate = {
                'Corporate': 7.5,
                'Thế chấp nhà': 9.0,
                'Kinh doanh SME': 12.0,
                'Ô tô': 10.5,
                'Tiêu dùng': 15.0
            }[lt]
            
            segment_premium = {
                'Prime': 0,
                'Standard': 1.5,
                'Sub-prime': 3.0,
                'NTB': 2.0
            }[seg]
            
            rate = base_rate + segment_premium + np.random.uniform(-0.5, 0.5)
            interest_rates.append(rate)
        
        # Current outstanding balance (% of original)
        outstanding_pct = []
        for orig_date, term in zip(origination_dates, terms):
            months_elapsed = (self.current_date - orig_date).days / 30.44
            if months_elapsed >= term:
                pct = 0  # Fully paid
            else:
                # Linear amortization assumption
                pct = 1 - (months_elapsed / term)
                pct = max(0, min(1, pct))
            outstanding_pct.append(pct)
        
        outstanding_balance = loan_amounts * np.array(outstanding_pct)
        
        # Generate delinquency status
        dpd, loan_class = self._generate_delinquency(
            segments, industries, provinces, 
            np.array([(self.current_date - d).days for d in origination_dates])
        )
        
        # Create DataFrame
        df = pd.DataFrame({
            'loan_id': loan_ids,
            'customer_segment': segments,
            'province': provinces,
            'industry': industries,
            'loan_type': loan_types,
            'origination_date': origination_dates,
            'original_amount_vnd_mil': loan_amounts,
            'outstanding_balance_vnd_mil': outstanding_balance,
            'term_months': terms,
            'interest_rate_pct': interest_rates,
            'days_past_due': dpd,
            'loan_classification': loan_class
        })
        
        # Add derived fields
        df['months_on_book'] = df['origination_date'].apply(
            lambda x: (self.current_date - x).days / 30.44
        )
        
        df['utilization_pct'] = (df['outstanding_balance_vnd_mil'] / 
                                  df['original_amount_vnd_mil'] * 100)
        
        # Add vintage (year-quarter of origination)
        df['vintage'] = df['origination_date'].apply(
            lambda x: f"{x.year}Q{(x.month-1)//3 + 1}"
        )
        
        return df
    
    def _generate_delinquency(self, segments, industries, provinces, days_on_book):
        """Generate realistic delinquency patterns"""
        
        n = len(segments)
        dpd = np.zeros(n)
        loan_class = np.array(['Nhóm 1 - Bình thường'] * n)
        
        # Base default probability by segment
        base_pd = {
            'Prime': 0.02,
            'Standard': 0.05,
            'Sub-prime': 0.12,
            'NTB': 0.08
        }
        
        # Industry risk factors
        industry_risk = {
            'Bán lẻ': 1.2,
            'Sản xuất': 1.0,
            'Dịch vụ': 1.3,
            'Bất động sản': 1.5,
            'Xây dựng': 1.4,
            'Nông nghiệp': 1.1,
            'Vận tải': 1.2,
            'F&B': 1.3,
            'Công nghệ': 0.9
        }
        
        # Provincial risk (simplified)
        province_risk = {
            'TP. Hồ Chí Minh': 0.9,
            'Hà Nội': 0.9,
            'Khác': 1.2
        }
        
        for i in range(n):
            # Calculate PD for this loan
            pd = base_pd[segments[i]]
            pd *= industry_risk.get(industries[i], 1.0)
            pd *= province_risk.get(provinces[i], 1.0)
            
            # Seasoning effect (lower risk for older loans that survived)
            if days_on_book[i] > 365:
                pd *= 0.7
            elif days_on_book[i] < 90:
                pd *= 1.3  # New loans riskier
            
            # Tet effect (Q1 has higher delinquency)
            current_quarter = (self.current_date.month - 1) // 3 + 1
            if current_quarter == 1:
                pd *= 1.15
            
            # Determine if loan is delinquent
            if np.random.random() < pd:
                # Generate DPD based on severity
                severity = np.random.random()
                if severity < 0.4:  # Early delinquency
                    dpd[i] = np.random.randint(1, 30)
                    loan_class[i] = 'Nhóm 2 - Cần chú ý'
                elif severity < 0.7:  # Moderate
                    dpd[i] = np.random.randint(30, 90)
                    loan_class[i] = 'Nhóm 3 - Dưới tiêu chuẩn'
                elif severity < 0.9:  # Serious
                    dpd[i] = np.random.randint(90, 180)
                    loan_class[i] = 'Nhóm 4 - Nghi ngờ'
                else:  # NPL
                    dpd[i] = np.random.randint(180, 365)
                    loan_class[i] = 'Nhóm 5 - Tổn thất'
        
        return dpd, loan_class
    
    def add_time_series(self, df, n_months=12):
        """Add historical snapshots for trend analysis"""
        
        snapshots = []
        
        for i in range(n_months):
            snapshot_date = self.current_date - timedelta(days=30 * i)
            
            # Filter loans that existed at snapshot date
            df_snapshot = df[df['origination_date'] <= snapshot_date].copy()
            df_snapshot['snapshot_date'] = snapshot_date
            
            # Recalculate DPD and classification for historical point
            # Simplified: add some random variation
            df_snapshot['days_past_due'] = df_snapshot['days_past_due'] + np.random.randint(-10, 10, len(df_snapshot))
            df_snapshot['days_past_due'] = df_snapshot['days_past_due'].clip(lower=0)
            
            snapshots.append(df_snapshot)
        
        return pd.concat(snapshots, ignore_index=True)


def main():
    """Generate and save loan portfolio data"""
    
    print("=" * 80)
    print("VPBANK LOAN PORTFOLIO - SYNTHETIC DATA GENERATION")
    print("=" * 80)
    print()
    
    # Generate portfolio
    generator = LoanPortfolioGenerator(n_loans=10000)
    print("Generating 10,000 loan portfolio...")
    df = generator.generate_portfolio()
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("PORTFOLIO SUMMARY")
    print("=" * 80)
    
    print(f"\nTotal Loans: {len(df):,}")
    print(f"Total Outstanding: {df['outstanding_balance_vnd_mil'].sum()/1e6:,.1f}B VND")
    print(f"Average Loan Size: {df['outstanding_balance_vnd_mil'].mean():,.0f}M VND")
    
    print("\n--- Loan Classification ---")
    print(df['loan_classification'].value_counts().sort_index())
    
    print("\n--- NPL Analysis ---")
    npl_count = df[df['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])].shape[0]
    npl_amount = df[df['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])]['outstanding_balance_vnd_mil'].sum()
    npl_ratio = npl_amount / df['outstanding_balance_vnd_mil'].sum() * 100
    
    print(f"NPL Count: {npl_count:,} ({npl_count/len(df)*100:.2f}%)")
    print(f"NPL Amount: {npl_amount/1e6:,.2f}B VND")
    print(f"NPL Ratio: {npl_ratio:.2f}%")
    
    print("\n--- By Segment ---")
    segment_summary = df.groupby('customer_segment').agg({
        'loan_id': 'count',
        'outstanding_balance_vnd_mil': 'sum'
    }).round(0)
    segment_summary.columns = ['Count', 'Outstanding (M VND)']
    print(segment_summary)
    
    print("\n--- By Product ---")
    product_summary = df.groupby('loan_type').agg({
        'loan_id': 'count',
        'outstanding_balance_vnd_mil': 'sum'
    }).round(0)
    product_summary.columns = ['Count', 'Outstanding (M VND)']
    print(product_summary)
    
    # Save to CSV
    output_file = '/mnt/user-data/outputs/loan_portfolio_current.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ Current portfolio saved to: {output_file}")
    
    # Generate time series data
    print("\nGenerating 12-month historical time series...")
    df_timeseries = generator.add_time_series(df, n_months=12)
    
    timeseries_file = '/mnt/user-data/outputs/loan_portfolio_timeseries.csv'
    df_timeseries.to_csv(timeseries_file, index=False, encoding='utf-8-sig')
    print(f"✓ Time series data saved to: {timeseries_file}")
    
    print("\n" + "=" * 80)
    print("DATA GENERATION COMPLETE")
    print("=" * 80)
    
    return df, df_timeseries


if __name__ == "__main__":
    df, df_ts = main()
