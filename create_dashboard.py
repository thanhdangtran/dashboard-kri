"""
Credit Risk KRI Dashboard - Interactive Visualization
Creates comprehensive dashboard with Plotly and exports to HTML + Excel
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import KRI calculator
import sys
sys.path.append('/home/claude')
from kri_calculator import CreditRiskKRI


class KRIDashboard:
    """Create interactive dashboard for credit risk KRIs"""
    
    def __init__(self, df, df_timeseries=None):
        self.df = df
        self.df_timeseries = df_timeseries
        self.kri_calc = CreditRiskKRI(df)
        self.kris = self.kri_calc.calculate_all_kris()
        
        # Color scheme
        self.colors = {
            'primary': '#1f77b4',
            'success': '#2ca02c',
            'warning': '#ff7f0e',
            'danger': '#d62728',
            'info': '#17becf',
            'neutral': '#7f7f7f'
        }
    
    def create_kpi_cards(self):
        """Create KPI summary cards"""
        
        npl = self.kris['npl_metrics']
        par = self.kris['par_metrics']
        
        # Create figure with cards
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                'NPL Ratio',
                'PAR30',
                'PAR90',
                'Total Portfolio',
                'Watch List',
                'Early Delinquency'
            ),
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}],
                   [{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]]
        )
        
        # NPL Ratio
        fig.add_trace(
            go.Indicator(
                mode="number+delta+gauge",
                value=npl['npl_balance_ratio'],
                delta={'reference': npl['risk_appetite_limit'], 'relative': False},
                gauge={
                    'axis': {'range': [0, 5]},
                    'bar': {'color': self.colors['danger'] if npl['npl_balance_ratio'] > npl['risk_appetite_limit'] else self.colors['success']},
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': npl['risk_appetite_limit']
                    }
                },
                number={'suffix': '%', 'font': {'size': 40}},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=1, col=1
        )
        
        # PAR30
        fig.add_trace(
            go.Indicator(
                mode="number+gauge",
                value=par['par30']['ratio'],
                gauge={
                    'axis': {'range': [0, 8]},
                    'bar': {'color': self.colors['warning'] if par['par30']['ratio'] > par['par30']['risk_appetite_limit'] else self.colors['success']},
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': par['par30']['risk_appetite_limit']
                    }
                },
                number={'suffix': '%', 'font': {'size': 40}},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=1, col=2
        )
        
        # PAR90
        fig.add_trace(
            go.Indicator(
                mode="number+gauge",
                value=par['par90']['ratio'],
                gauge={
                    'axis': {'range': [0, 5]},
                    'bar': {'color': self.colors['warning'] if par['par90']['ratio'] > par['par90']['risk_appetite_limit'] else self.colors['success']},
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': par['par90']['risk_appetite_limit']
                    }
                },
                number={'suffix': '%', 'font': {'size': 40}},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=1, col=3
        )
        
        # Total Portfolio
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=npl['total_balance'] / 1e6,
                number={'suffix': 'B VND', 'font': {'size': 36}},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=2, col=1
        )
        
        # Watch List
        ewi = self.kris['early_warning']
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=ewi['watch_list']['ratio'],
                number={'suffix': '%', 'font': {'size': 36}},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=2, col=2
        )
        
        # Early Delinquency
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=ewi['early_delinquency']['ratio'],
                number={'suffix': '%', 'font': {'size': 36}},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=2, col=3
        )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            title_text="<b>Key Risk Indicators - Executive Summary</b>",
            title_font_size=24
        )
        
        return fig
    
    def create_npl_trend_chart(self):
        """Create NPL trend over time"""
        
        if self.df_timeseries is None:
            return None
        
        # Calculate NPL by snapshot
        npl_trend = self.df_timeseries.groupby('snapshot_date').apply(
            lambda x: pd.Series({
                'npl_ratio': x[x['loan_classification'].isin(['Nhóm 4 - Nghi ngờ', 'Nhóm 5 - Tổn thất'])]['outstanding_balance_vnd_mil'].sum() / x['outstanding_balance_vnd_mil'].sum() * 100,
                'par30_ratio': x[x['days_past_due'] >= 30]['outstanding_balance_vnd_mil'].sum() / x['outstanding_balance_vnd_mil'].sum() * 100,
                'par90_ratio': x[x['days_past_due'] >= 90]['outstanding_balance_vnd_mil'].sum() / x['outstanding_balance_vnd_mil'].sum() * 100
            })
        ).reset_index()
        
        npl_trend = npl_trend.sort_values('snapshot_date')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=npl_trend['snapshot_date'],
            y=npl_trend['npl_ratio'],
            mode='lines+markers',
            name='NPL Ratio',
            line=dict(color=self.colors['danger'], width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=npl_trend['snapshot_date'],
            y=npl_trend['par30_ratio'],
            mode='lines+markers',
            name='PAR30',
            line=dict(color=self.colors['warning'], width=2),
            marker=dict(size=6)
        ))
        
        fig.add_trace(go.Scatter(
            x=npl_trend['snapshot_date'],
            y=npl_trend['par90_ratio'],
            mode='lines+markers',
            name='PAR90',
            line=dict(color=self.colors['info'], width=2),
            marker=dict(size=6)
        ))
        
        # Add risk appetite line
        fig.add_hline(
            y=3.0,
            line_dash="dash",
            line_color="red",
            annotation_text="NPL Risk Appetite (3%)",
            annotation_position="right"
        )
        
        fig.update_layout(
            title="<b>NPL & PAR Trend Analysis (12 Months)</b>",
            xaxis_title="Date",
            yaxis_title="Ratio (%)",
            hovermode='x unified',
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_npl_by_segment_chart(self):
        """Create NPL breakdown by segment"""
        
        npl_segment = self.kris['npl_metrics']['by_segment'].copy()
        npl_segment = npl_segment.sort_values('npl_ratio', ascending=False)
        
        fig = go.Figure()
        
        # Bar chart for NPL ratio
        fig.add_trace(go.Bar(
            x=npl_segment['customer_segment'],
            y=npl_segment['npl_ratio'],
            text=npl_segment['npl_ratio'].round(2).astype(str) + '%',
            textposition='outside',
            marker_color=[self.colors['danger'] if x > 1.0 else self.colors['success'] for x in npl_segment['npl_ratio']],
            name='NPL Ratio'
        ))
        
        # Add risk appetite line
        fig.add_hline(
            y=3.0,
            line_dash="dash",
            line_color="red",
            annotation_text="Risk Appetite (3%)",
            annotation_position="right"
        )
        
        fig.update_layout(
            title="<b>NPL Ratio by Customer Segment</b>",
            xaxis_title="Customer Segment",
            yaxis_title="NPL Ratio (%)",
            height=450,
            showlegend=False
        )
        
        return fig
    
    def create_npl_by_product_chart(self):
        """Create NPL breakdown by product"""
        
        npl_product = self.kris['npl_metrics']['by_product'].copy()
        npl_product = npl_product.sort_values('npl_ratio', ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=npl_product['loan_type'],
            y=npl_product['npl_ratio'],
            text=npl_product['npl_ratio'].round(2).astype(str) + '%',
            textposition='outside',
            marker_color=[self.colors['danger'] if x > 1.5 else self.colors['warning'] if x > 0.8 else self.colors['success'] for x in npl_product['npl_ratio']],
            name='NPL Ratio'
        ))
        
        fig.update_layout(
            title="<b>NPL Ratio by Loan Product</b>",
            xaxis_title="Loan Product",
            yaxis_title="NPL Ratio (%)",
            height=450,
            showlegend=False
        )
        
        return fig
    
    def create_geography_heatmap(self):
        """Create geographic heatmap of NPL"""
        
        npl_province = self.kris['npl_metrics']['by_province'].copy()
        npl_province = npl_province.sort_values('npl_ratio', ascending=False)
        
        fig = go.Figure(data=go.Heatmap(
            z=[npl_province['npl_ratio'].values],
            x=npl_province['province'],
            y=['NPL Ratio'],
            colorscale='RdYlGn_r',
            text=npl_province['npl_ratio'].round(2).astype(str) + '%',
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title="NPL %")
        ))
        
        fig.update_layout(
            title="<b>NPL Heatmap by Province</b>",
            height=300,
            xaxis_title="Province",
            yaxis_title=""
        )
        
        return fig
    
    def create_industry_heatmap(self):
        """Create industry heatmap of NPL"""
        
        npl_industry = self.kris['npl_metrics']['by_industry'].copy()
        npl_industry = npl_industry.sort_values('npl_ratio', ascending=False)
        
        fig = go.Figure(data=go.Heatmap(
            z=[npl_industry['npl_ratio'].values],
            x=npl_industry['industry'],
            y=['NPL Ratio'],
            colorscale='RdYlGn_r',
            text=npl_industry['npl_ratio'].round(2).astype(str) + '%',
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title="NPL %")
        ))
        
        fig.update_layout(
            title="<b>NPL Heatmap by Industry</b>",
            height=300,
            xaxis_title="Industry",
            yaxis_title=""
        )
        
        return fig
    
    def create_portfolio_quality_distribution(self):
        """Create portfolio quality distribution chart"""
        
        quality = self.kris['quality_distribution'].copy()
        
        # Create stacked bar showing count and balance
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('By Count', 'By Balance'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        colors_map = {
            'Nhóm 1 - Bình thường': self.colors['success'],
            'Nhóm 2 - Cần chú ý': '#90EE90',
            'Nhóm 3 - Dưới tiêu chuẩn': self.colors['warning'],
            'Nhóm 4 - Nghi ngờ': '#FF6347',
            'Nhóm 5 - Tổn thất': self.colors['danger']
        }
        
        # Count chart
        fig.add_trace(
            go.Bar(
                x=quality['classification'],
                y=quality['count_pct'],
                text=quality['count_pct'].round(1).astype(str) + '%',
                textposition='outside',
                marker_color=[colors_map.get(c, self.colors['neutral']) for c in quality['classification']],
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Balance chart
        fig.add_trace(
            go.Bar(
                x=quality['classification'],
                y=quality['balance_pct'],
                text=quality['balance_pct'].round(1).astype(str) + '%',
                textposition='outside',
                marker_color=[colors_map.get(c, self.colors['neutral']) for c in quality['classification']],
                showlegend=False
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title="<b>Portfolio Quality Distribution</b>",
            height=450,
            showlegend=False
        )
        
        fig.update_yaxes(title_text="Percentage (%)", row=1, col=1)
        fig.update_yaxes(title_text="Percentage (%)", row=1, col=2)
        
        return fig
    
    def create_concentration_charts(self):
        """Create concentration risk charts"""
        
        conc = self.kris['concentration_risk']
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Industry Concentration', 'Province Concentration'),
            specs=[[{'type': 'pie'}, {'type': 'pie'}]]
        )
        
        # Industry pie
        industry_data = pd.Series(conc['industry']['details']).sort_values(ascending=False)
        fig.add_trace(
            go.Pie(
                labels=industry_data.index,
                values=industry_data.values,
                textinfo='label+percent',
                textposition='outside',
                marker=dict(line=dict(color='white', width=2))
            ),
            row=1, col=1
        )
        
        # Province pie
        province_data = pd.Series(conc['province']['details']).sort_values(ascending=False)
        fig.add_trace(
            go.Pie(
                labels=province_data.index,
                values=province_data.values,
                textinfo='label+percent',
                textposition='outside',
                marker=dict(line=dict(color='white', width=2))
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title="<b>Concentration Risk Analysis</b>",
            height=500,
            showlegend=True
        )
        
        return fig
    
    def create_migration_matrix_heatmap(self):
        """Create migration matrix heatmap"""
        
        if self.df_timeseries is None:
            return None
        
        migration = self.kri_calc.calculate_migration_matrix(self.df_timeseries)
        
        if migration is None:
            return None
        
        fig = go.Figure(data=go.Heatmap(
            z=migration.values,
            x=migration.columns,
            y=migration.index,
            colorscale='RdYlGn',
            reversescale=False,
            text=migration.round(1).astype(str) + '%',
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="% Migration")
        ))
        
        fig.update_layout(
            title="<b>Migration Matrix (Previous → Current Classification)</b>",
            xaxis_title="Current Classification",
            yaxis_title="Previous Classification",
            height=500,
            xaxis={'side': 'bottom'}
        )
        
        return fig
    
    def create_vintage_analysis_chart(self):
        """Create vintage analysis chart"""
        
        vintage = self.kris['vintage_analysis'].copy()
        vintage = vintage.sort_values('vintage')
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # NPL ratio bars
        fig.add_trace(
            go.Bar(
                x=vintage['vintage'],
                y=vintage['npl_ratio'],
                name='NPL Ratio',
                text=vintage['npl_ratio'].round(1).astype(str) + '%',
                textposition='outside',
                marker_color=self.colors['danger']
            ),
            secondary_y=False
        )
        
        # Total balance line
        fig.add_trace(
            go.Scatter(
                x=vintage['vintage'],
                y=vintage['total_balance'] / 1e6,
                name='Total Balance',
                mode='lines+markers',
                line=dict(color=self.colors['primary'], width=2),
                marker=dict(size=8)
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title="<b>Vintage Analysis - NPL Performance by Origination Cohort</b>",
            height=500,
            hovermode='x unified'
        )
        
        fig.update_xaxes(title_text="Vintage (Year-Quarter)")
        fig.update_yaxes(title_text="NPL Ratio (%)", secondary_y=False)
        fig.update_yaxes(title_text="Total Balance (B VND)", secondary_y=True)
        
        return fig
    
    def create_full_dashboard(self):
        """Create complete dashboard with all visualizations"""
        
        print("Creating comprehensive KRI dashboard...")
        
        # Create all charts
        charts = {
            'kpi_cards': self.create_kpi_cards(),
            'npl_trend': self.create_npl_trend_chart(),
            'npl_by_segment': self.create_npl_by_segment_chart(),
            'npl_by_product': self.create_npl_by_product_chart(),
            'geography_heatmap': self.create_geography_heatmap(),
            'industry_heatmap': self.create_industry_heatmap(),
            'quality_distribution': self.create_portfolio_quality_distribution(),
            'concentration': self.create_concentration_charts(),
            'migration_matrix': self.create_migration_matrix_heatmap(),
            'vintage_analysis': self.create_vintage_analysis_chart()
        }
        
        # Save individual charts as HTML
        html_parts = []
        
        html_parts.append("""
        <html>
        <head>
            <title>VPBank Credit Risk KRI Dashboard</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }
                .header {
                    background-color: #003366;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    margin-bottom: 30px;
                    border-radius: 5px;
                }
                .section {
                    background-color: white;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .chart-container {
                    margin: 20px 0;
                }
                .footer {
                    text-align: center;
                    color: #666;
                    padding: 20px;
                    margin-top: 30px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>VPBank Credit Risk Dashboard</h1>
                <h3>Key Risk Indicators (KRI) - Executive Report</h3>
                <p>Report Date: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            </div>
        """)
        
        # Add each chart
        for chart_name, fig in charts.items():
            if fig is not None:
                html_parts.append(f'<div class="section"><div class="chart-container">')
                html_parts.append(fig.to_html(full_html=False, include_plotlyjs='cdn'))
                html_parts.append('</div></div>')
        
        # Add COSO ERM context
        html_parts.append("""
            <div class="section">
                <h2>COSO ERM Framework Alignment</h2>
                <h3>Performance + Information, Communication & Reporting</h3>
                <ul>
                    <li><b>Performance Monitoring:</b> Continuous tracking of NPL, PAR metrics against risk appetite</li>
                    <li><b>Information & Communication:</b> Real-time KRI dashboard provides actionable insights</li>
                    <li><b>Risk Governance:</b> Automated alerts for risk appetite breaches</li>
                    <li><b>Decision Support:</b> Segment, product, and geographic risk breakdown</li>
                    <li><b>Trend Analysis:</b> Historical trends and migration patterns for predictive insights</li>
                </ul>
            </div>
        """)
        
        html_parts.append("""
            <div class="footer">
                <p>© 2025 VPBank - Credit Risk Management | Dashboard auto-generated</p>
            </div>
        </body>
        </html>
        """)
        
        # Combine and save
        full_html = '\n'.join(html_parts)
        
        html_file = '/mnt/user-data/outputs/kri_dashboard.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"✓ Dashboard saved to: {html_file}")
        
        return charts


def main():
    """Generate complete dashboard"""
    
    print("=" * 80)
    print("CREDIT RISK KRI DASHBOARD GENERATOR")
    print("=" * 80)
    print()
    
    # Load data
    print("Loading data...")
    df = pd.read_csv('/mnt/user-data/outputs/loan_portfolio_current.csv')
    df_ts = pd.read_csv('/mnt/user-data/outputs/loan_portfolio_timeseries.csv')
    
    # Parse dates
    df['origination_date'] = pd.to_datetime(df['origination_date'])
    df_ts['origination_date'] = pd.to_datetime(df_ts['origination_date'])
    df_ts['snapshot_date'] = pd.to_datetime(df_ts['snapshot_date'])
    
    print(f"✓ Loaded {len(df):,} current loans")
    print(f"✓ Loaded {len(df_ts):,} time series records")
    print()
    
    # Create dashboard
    dashboard = KRIDashboard(df, df_ts)
    charts = dashboard.create_full_dashboard()
    
    print()
    print("=" * 80)
    print("DASHBOARD GENERATION COMPLETE")
    print("=" * 80)
    print()
    print("Files created:")
    print("  1. /mnt/user-data/outputs/loan_portfolio_current.csv")
    print("  2. /mnt/user-data/outputs/loan_portfolio_timeseries.csv")
    print("  3. /mnt/user-data/outputs/kri_dashboard.html (Interactive)")
    print()
    print("Next: Open kri_dashboard.html in browser for interactive visualizations")


if __name__ == "__main__":
    main()
