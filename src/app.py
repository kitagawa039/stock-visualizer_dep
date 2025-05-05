import streamlit as st

st.set_page_config(
    page_title="株価ビジュアライザー",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.subplots as sp
import os
import requests
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from utils.data_fetcher import get_stock_data_alpha_vantage, get_stock_data_jquants
    from utils.data_processor import calculate_returns, calculate_moving_averages, calculate_volatility, calculate_rsi
except ModuleNotFoundError as e:
    st.error(f"モジュールの読み込みに失敗しました: {e}")
    st.error("プロジェクトの構造を確認してください。")
    st.error(f"現在のPythonパス: {sys.path}")
    st.error(f"プロジェクトルート: {project_root}")
    st.error(f"utilsディレクトリの存在: {(project_root / 'utils').exists()}")
    st.stop()

# データディレクトリのパスを設定
data_dir = os.path.join(project_root, 'data')

# Excelファイルから日本株の会社名を読み込む
try:
    jp_stocks_df = pd.read_excel(os.path.join(data_dir, 'data_j.xlsx'))
    # コード列をstr型・ゼロ埋め4桁に統一
    jp_stocks_df['コード'] = jp_stocks_df['コード'].astype(str).str.zfill(4)
    JP_COMPANIES = dict(zip(jp_stocks_df['コード'], jp_stocks_df['銘柄名']))
except Exception as e:
    st.error(f"日本株データの読み込みに失敗しました: {e}")
    JP_COMPANIES = {}

# Excelファイルからアメリカ株の会社名を読み込む
try:
    us_stocks_df = pd.read_excel(os.path.join(data_dir, 'data_us.xlsx'))
    US_COMPANIES = dict(zip(us_stocks_df['ティッカーシンボル'], us_stocks_df['会社名']))
except Exception as e:
    st.error(f"アメリカ株データの読み込みに失敗しました: {e}")
    US_COMPANIES = {}

st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #1E88E5;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #111;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
        color: white;
    }
    .metric-card {
        background-color: #1E1E1E;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #888;
    }
    .positive {
        color: #4CAF50;
    }
    .negative {
        color: #F44336;
    }
</style>
""", unsafe_allow_html=True)

def get_company_name(code: str, market: str) -> str:
    """
    証券コードから会社名を取得する関数
    """
    code = code.strip().upper()
    if market == "jp":
        import re
        m = re.match(r"(\d{4})", code)
        if m:
            key = m.group(1).zfill(4)
            return JP_COMPANIES.get(key, code)
        return JP_COMPANIES.get(code.replace('.T', '').zfill(4), code)
    else:
        return US_COMPANIES.get(code, code)

def normalize_stock_code(code: str, market: str) -> str:
    """
    証券コードを正規化する関数
    
    Parameters:
    -----------
    code : str
        証券コード
    market : str
        市場（"jp" または "us"）
        
    Returns:
    --------
    str
        正規化された証券コード
    """
    code = code.strip().upper()
    
    if market == "jp":
        if code.isdigit() and len(code) == 4:
            return f"{code}.T"
        return code
    else:
        return code

st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="color: #1E88E5; font-size: 1.6em;">📈 Stock Visualizer</h1>
    <p>株価データ可視化ツール</p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("ページ選択", ["株式チャート", "投資信託特設ページ"])

if page == "株式チャート":
    # タイトルは表示しない

    st.sidebar.header("市場選択")
    market = st.sidebar.radio(
        "市場:",
        ["日本株 (J-Quants)", "米国株 (Alpha Vantage)"],
        index=0
    )
    
    market_code = "jp" if "日本株" in market else "us"
    
    st.sidebar.header("銘柄選択")
    
    if market_code == "jp":
        input_code = st.sidebar.text_input(
            "証券コードを入力（例: 7203, 1321.T, 9984）:",
            value="7203"
        )
        placeholder_text = "トヨタ自動車(7203)、ソフトバンクグループ(9984)など"
    else:
        input_code = st.sidebar.text_input(
            "ティッカーシンボルを入力（例: AAPL, MSFT, GOOGL）:",
            value="AAPL"
        )
        placeholder_text = "Apple(AAPL)、Microsoft(MSFT)、Amazon(AMZN)など"
    
    stock_code = normalize_stock_code(input_code, market_code)
    
    st.sidebar.subheader("期間選択")
    period = st.sidebar.selectbox(
        "期間:",
        ["1週間", "1ヶ月", "3ヶ月", "6ヶ月", "1年", "2年"],
        index=5
    )
    period_map = {
        "1週間": 7,
        "1ヶ月": 30,
        "3ヶ月": 90,
        "6ヶ月": 180,
        "1年": 365,
        "2年": 365*2
    }
    days = period_map[period]
    today = datetime.now().date()
    from_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    
    st.sidebar.subheader("テクニカル指標")
    show_ma = st.sidebar.checkbox("移動平均線", value=True)
    show_volume = st.sidebar.checkbox("出来高", value=True)
    show_rsi = st.sidebar.checkbox("RSI", value=False)
    show_volatility = st.sidebar.checkbox("ボラティリティ", value=False)
    
    with st.spinner(f"データを取得中... ({stock_code})"):
        try:
            if market_code == "jp":
                data = get_stock_data_jquants(stock_code, from_date=from_date, to_date=to_date)
            else:
                data = get_stock_data_alpha_vantage(stock_code)
                data = data.loc[from_date:to_date] if not data.empty else data
            
            if not pd.api.types.is_datetime64_any_dtype(data.index):
                data.index = pd.to_datetime(data.index)
            
            close_col = data['Close']
            open_col = data['Open']
            high_col = data['High']
            low_col = data['Low']
            volume_col = data['Volume'] if 'Volume' in data.columns else None
            
            if show_ma:
                data = calculate_moving_averages(data, windows=[5, 25, 75])
                ma5 = data['MA_5']
                ma25 = data['MA_25']
                ma75 = data['MA_75']
            
            if show_rsi or show_volatility:
                data = calculate_returns(data)
                
            if show_rsi:
                data = calculate_rsi(data)
                
            if show_volatility:
                data = calculate_volatility(data)
                
        except Exception as e:
            st.error(f"データ取得エラー: {e}")
            st.info(f"ヒント: {placeholder_text}")
            st.stop()
    
    if data is None or data.empty or close_col.dropna().empty:
        st.error("データが取得できませんでした。証券コードを確認してください。")
        st.info(f"ヒント: {placeholder_text}")
    else:
        tabs = st.tabs(["価格チャート", "テクニカル分析", "データテーブル"])
        
        currency_symbol = "¥" if market_code == "jp" else "$"
        
        with tabs[0]:
            company_name = get_company_name(stock_code, market_code)
            # 日本株の場合は.Tを除去して表示
            display_code = stock_code.replace('.T', '') if market_code == "jp" else stock_code
            # 銘柄名が取得できなかった場合はコードのみ表示
            if company_name and company_name != display_code:
                display_name = f"{display_code} {company_name}"
            else:
                display_name = display_code
            st.subheader(f"{display_name}")
            
            n_rows = 1 + (1 if show_volume else 0)
            row_heights = [0.7, 0.3] if show_volume else [1.0]
            subplot_titles = ["", ""] if show_volume else [""]
            
            fig = sp.make_subplots(
                rows=n_rows, cols=1, shared_xaxes=True, vertical_spacing=0.04,
                row_heights=row_heights,
                subplot_titles=subplot_titles
            )
            
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=open_col,
                    high=high_col,
                    low=low_col,
                    close=close_col,
                    name='ローソク足',
                    increasing_line_color='#FF5252',  # 陽線
                    decreasing_line_color='#4CAF50',  # 陰線
                    showlegend=True,
                    legendgroup='candlestick'
                ),
                row=1, col=1
            )
            
            if show_ma:
                fig.add_trace(go.Scatter(
                    x=data.index, y=ma5, mode='lines', name='MA(5日)',
                    line=dict(color='#FFC107', width=1.5), showlegend=True), row=1, col=1)
                fig.add_trace(go.Scatter(
                    x=data.index, y=ma25, mode='lines', name='MA(25日)',
                    line=dict(color='#FF5722', width=1.5), showlegend=True), row=1, col=1)
                fig.add_trace(go.Scatter(
                    x=data.index, y=ma75, mode='lines', name='MA(75日)',
                    line=dict(color='#2196F3', width=1.5), showlegend=True), row=1, col=1)
            
            if show_volume and volume_col is not None:
                fig.add_trace(
                    go.Bar(
                        x=data.index,
                        y=volume_col,
                        name='出来高',
                        marker_color='rgba(100,181,246,0.5)',
                        showlegend=True
                    ),
                    row=2, col=1
                )
            
            fig.update_xaxes(
                tickformat='%y/%-m',
                tickangle=0,
                nticks=12,
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                row=1, col=1
            )
            
            if show_volume:
                fig.update_xaxes(
                    tickformat='%y/%-m',
                    tickangle=45,
                    nticks=12,
                    showgrid=False,
                    row=2, col=1
                )
                fig.update_yaxes(title_text="", showgrid=True, gridcolor='rgba(255,255,255,0.1)', row=2, col=1)
            
            fig.update_yaxes(title_text="", showgrid=True, gridcolor='rgba(255,255,255,0.1)', row=1, col=1)
            
            fig.update_layout(
                legend=dict(
                    title="凡例",
                    orientation="h",
                    yanchor="top",
                    y=1.13,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=12),
                    bgcolor="rgba(0,0,0,0.5)",
                    bordercolor="rgba(255,255,255,0.2)"
                ),
                template="plotly_dark",
                margin=dict(t=120, b=60, l=60, r=40),
                plot_bgcolor='rgba(25,25,25,1)',
                paper_bgcolor='rgba(25,25,25,1)',
                height=600,
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">現在値</div>
                    <div class="metric-value">{currency_symbol}{close_col.iloc[-1]:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                daily_return = (close_col.iloc[-1] / close_col.iloc[-2] - 1) * 100 if len(close_col) > 1 else 0
                color_class = "positive" if daily_return >= 0 else "negative"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">日次リターン</div>
                    <div class="metric-value {color_class}">{daily_return:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                total_return = ((close_col.iloc[-1] / close_col.iloc[0]) - 1) * 100
                color_class = "positive" if total_return >= 0 else "negative"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">期間リターン</div>
                    <div class="metric-value {color_class}">{total_return:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                high_low_ratio = ((high_col.max() / low_col.min()) - 1) * 100
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">高値/安値レンジ</div>
                    <div class="metric-value">{high_low_ratio:.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
        
        with tabs[1]:
            company_name = get_company_name(stock_code, market_code)
            display_code = stock_code.replace('.T', '') if market_code == "jp" else stock_code
            if company_name and company_name != display_code:
                display_name = f"{display_code} {company_name}"
            else:
                display_name = display_code
            st.subheader(f"{display_name} テクニカル分析")
            
            n_rows = 1 + sum([show_rsi, show_volatility])
            row_heights = [0.6] + [0.2] * sum([show_rsi, show_volatility])
            
            subplot_titles = [""]
            if show_rsi:
                subplot_titles.append("")
            if show_volatility:
                subplot_titles.append("")
            
            tech_fig = sp.make_subplots(
                rows=n_rows, cols=1, shared_xaxes=True, vertical_spacing=0.04,
                row_heights=row_heights,
                subplot_titles=subplot_titles
            )
            
            tech_fig.add_trace(
                go.Scatter(
                    x=data.index, y=close_col, mode='lines', name='終値',
                    line=dict(color='#2196F3', width=2), showlegend=True
                ),
                row=1, col=1
            )
            
            if show_ma:
                tech_fig.add_trace(go.Scatter(
                    x=data.index, y=ma5, mode='lines', name='MA(5日)',
                    line=dict(color='#FFC107', width=1.5), showlegend=True), row=1, col=1)
                tech_fig.add_trace(go.Scatter(
                    x=data.index, y=ma25, mode='lines', name='MA(25日)',
                    line=dict(color='#FF5722', width=1.5), showlegend=True), row=1, col=1)
                tech_fig.add_trace(go.Scatter(
                    x=data.index, y=ma75, mode='lines', name='MA(75日)',
                    line=dict(color='#2196F3', width=1.5), showlegend=True), row=1, col=1)
            
            current_row = 2
            if show_rsi:
                tech_fig.add_trace(
                    go.Scatter(
                        x=data.index, y=data['RSI'], mode='lines', name='RSI (14)',
                        line=dict(color='#9C27B0', width=1.5), showlegend=True
                    ),
                    row=current_row, col=1
                )
                
                tech_fig.add_trace(
                    go.Scatter(
                        x=[data.index[0], data.index[-1]], y=[70, 70], mode='lines', name='過買い (70)',
                        line=dict(color='rgba(255,82,82,0.5)', width=1, dash='dash'), showlegend=True
                    ),
                    row=current_row, col=1
                )
                tech_fig.add_trace(
                    go.Scatter(
                        x=[data.index[0], data.index[-1]], y=[30, 30], mode='lines', name='過売り (30)',
                        line=dict(color='rgba(76,175,80,0.5)', width=1, dash='dash'), showlegend=True
                    ),
                    row=current_row, col=1
                )
                current_row += 1
            
            if show_volatility:
                tech_fig.add_trace(
                    go.Scatter(
                        x=data.index, y=data['Volatility'], mode='lines', name='ボラティリティ (20日)',
                        line=dict(color='#FF9800', width=1.5), showlegend=True
                    ),
                    row=current_row, col=1
                )
            
            tech_fig.update_xaxes(
                tickformat='%y/%-m',
                tickangle=0,
                nticks=12,
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                row=1, col=1
            )
            
            tech_fig.update_yaxes(title_text="", showgrid=True, gridcolor='rgba(255,255,255,0.1)', row=1, col=1)
            
            if show_rsi:
                tech_fig.update_yaxes(
                    title_text="", showgrid=True, gridcolor='rgba(255,255,255,0.1)',
                    range=[0, 100], row=2, col=1
                )
            
            if show_volatility:
                volatility_row = 2 if not show_rsi else 3
                tech_fig.update_yaxes(
                    title_text="", showgrid=True, gridcolor='rgba(255,255,255,0.1)',
                    row=volatility_row, col=1
                )
            
            tech_fig.update_layout(
                legend=dict(
                    title="凡例",
                    orientation="h",
                    yanchor="top",
                    y=1.13,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=12),
                    bgcolor="rgba(0,0,0,0.5)",
                    bordercolor="rgba(255,255,255,0.2)"
                ),
                template="plotly_dark",
                margin=dict(t=120, b=60, l=60, r=40),
                plot_bgcolor='rgba(25,25,25,1)',
                paper_bgcolor='rgba(25,25,25,1)',
                height=700,
                hovermode="x unified"
            )
            
            st.plotly_chart(tech_fig, use_container_width=True)
        
        with tabs[2]:
            company_name = get_company_name(stock_code, market_code)
            display_code = stock_code.replace('.T', '') if market_code == "jp" else stock_code
            if company_name and company_name != display_code:
                display_name = f"{display_code} {company_name}"
            else:
                display_name = display_code
            st.subheader(f"{display_name} データテーブル")
            
            display_data = data.copy()
            display_data.index = pd.to_datetime(display_data.index)
            display_data.index = display_data.index.strftime('%Y-%m-%d')
            display_data = display_data.sort_index(ascending=False)
            
            columns_to_display = ['Open', 'High', 'Low', 'Close', 'Volume']
            if show_ma:
                columns_to_display.extend(['MA_5', 'MA_25', 'MA_75'])
            if show_rsi:
                columns_to_display.append('RSI')
            if show_volatility:
                columns_to_display.append('Volatility')
            if 'Daily_Return' in display_data.columns:
                columns_to_display.append('Daily_Return')
            
            available_columns = [col for col in columns_to_display if col in display_data.columns]
            
            column_names = {
                'Open': '始値',
                'High': '高値',
                'Low': '安値',
                'Close': '終値',
                'Volume': '出来高',
                'MA_5': '移動平均(5日)',
                'MA_25': '移動平均(25日)',
                'MA_75': '移動平均(75日)',
                'RSI': 'RSI(14)',
                'Volatility': 'ボラティリティ(20日)',
                'Daily_Return': '日次リターン(%)'
            }
            
            display_data = display_data[available_columns]
            display_data.columns = [column_names.get(col, col) for col in display_data.columns]
            
            st.dataframe(display_data.style.format('{:.2f}'), use_container_width=True)
            
            csv = display_data.to_csv()
            st.download_button(
                label="CSVダウンロード",
                data=csv,
                file_name=f"{stock_code}_data.csv",
                mime="text/csv",
            )
    
    st.markdown("---")
    if market_code == "jp":
        st.caption("データソース: J-Quants API")
    else:
        st.caption("データソース: Alpha Vantage API")
    st.caption("最終更新日: " + datetime.now().strftime("%Y年%m月%d日"))

elif page == "投資信託特設ページ":
    st.header("人気投資信託の値動き特設ページ")
    
    fund_dict = {
        "オルカン（eMAXIS Slim 全世界株式）": "2559.T",
        "S&P500（eMAXIS Slim）": "2558.T",
        "日経225インデックス": "1321.T",
    }
    
    selected_fund = st.selectbox("投資信託を選択:", list(fund_dict.keys()))
    fund_code = fund_dict[selected_fund]
    
    period = st.selectbox(
        "期間:",
        ["1ヶ月", "3ヶ月", "6ヶ月", "1年", "2年"],
        index=4
    )
    
    period_map = {
        "1ヶ月": 30,
        "3ヶ月": 90,
        "6ヶ月": 180,
        "1年": 365,
        "2年": 365*2
    }
    
    days = period_map[period]
    today = datetime.now().date()
    from_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    
    with st.spinner("データを取得中..."):
        try:
            data = get_stock_data_jquants(fund_code, from_date=from_date, to_date=to_date)
            if not pd.api.types.is_datetime64_any_dtype(data.index):
                data.index = pd.to_datetime(data.index)
            close_col = data['Close']
            
            data = calculate_moving_averages(data, windows=[5, 20, 60])
            ma5 = data['MA_5']
            ma20 = data['MA_20']
            ma60 = data['MA_60']
            
            data = calculate_returns(data)
            
        except Exception as e:
            st.error(f"データ取得エラー: {e}")
            st.stop()
    
    if data is None or data.empty or close_col.dropna().empty:
        st.error("データが取得できませんでした。")
    else:
        tabs = st.tabs(["基準価額チャート", "パフォーマンス分析", "データテーブル"])
        
        with tabs[0]:
            st.subheader(f"{selected_fund}の基準価額推移")
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=data.index,
                y=close_col,
                mode='lines',
                name='基準価額',
                line=dict(color='#2196F3', width=2.5)
            ))
            
            fig.add_trace(go.Scatter(
                x=data.index, y=ma5, mode='lines', name='MA(5日)',
                line=dict(color='#FFC107', width=1.5)
            ))
            fig.add_trace(go.Scatter(
                x=data.index, y=ma20, mode='lines', name='MA(20日)',
                line=dict(color='#FF5722', width=1.5)
            ))
            fig.add_trace(go.Scatter(
                x=data.index, y=ma60, mode='lines', name='MA(60日)',
                line=dict(color='#9C27B0', width=1.5)
            ))
            
            fig.update_layout(
                legend=dict(
                    title="凡例",
                    orientation="h",
                    yanchor="top",
                    y=1.13,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=12),
                    bgcolor="rgba(0,0,0,0.5)",
                    bordercolor="rgba(255,255,255,0.2)"
                ),
                template="plotly_dark",
                margin=dict(t=120, b=60, l=60, r=40),
                plot_bgcolor='rgba(25,25,25,1)',
                paper_bgcolor='rgba(25,25,25,1)',
                height=600,
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">現在基準価額</div>
                    <div class="metric-value">¥{close_col.iloc[-1]:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                daily_return = (close_col.iloc[-1] / close_col.iloc[-2] - 1) * 100 if len(close_col) > 1 else 0
                color_class = "positive" if daily_return >= 0 else "negative"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">日次リターン</div>
                    <div class="metric-value {color_class}">{daily_return:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                total_return = ((close_col.iloc[-1] / close_col.iloc[0]) - 1) * 100
                color_class = "positive" if total_return >= 0 else "negative"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">期間リターン</div>
                    <div class="metric-value {color_class}">{total_return:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
        
        with tabs[1]:
            st.subheader(f"{selected_fund}のパフォーマンス分析")
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Cumulative_Return'],
                mode='lines',
                name='累積リターン',
                line=dict(color='#4CAF50', width=2)
            ))
            
            fig.update_layout(
                legend=dict(
                    title="凡例",
                    orientation="h",
                    yanchor="top",
                    y=1.13,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=12),
                    bgcolor="rgba(0,0,0,0.5)",
                    bordercolor="rgba(255,255,255,0.2)"
                ),
                template="plotly_dark",
                margin=dict(t=120, b=60, l=60, r=40),
                plot_bgcolor='rgba(25,25,25,1)',
                paper_bgcolor='rgba(25,25,25,1)',
                height=400,
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            monthly_returns = data['Daily_Return'].resample('M').sum()
            monthly_returns.index = monthly_returns.index.strftime('%Y-%m')
            
            fig = go.Figure()
            
            colors = ['#4CAF50' if x >= 0 else '#F44336' for x in monthly_returns]
            
            fig.add_trace(go.Bar(
                x=monthly_returns.index,
                y=monthly_returns,
                name='月次リターン',
                marker_color=colors
            ))
            
            fig.update_layout(
                legend=dict(
                    title="凡例",
                    orientation="h",
                    yanchor="top",
                    y=1.13,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=12),
                    bgcolor="rgba(0,0,0,0.5)",
                    bordercolor="rgba(255,255,255,0.2)"
                ),
                template="plotly_dark",
                margin=dict(t=120, b=60, l=60, r=40),
                plot_bgcolor='rgba(25,25,25,1)',
                paper_bgcolor='rgba(25,25,25,1)',
                height=400,
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tabs[2]:
            st.subheader(f"{selected_fund}のデータテーブル")
            
            display_data = data.copy()
            display_data.index = pd.to_datetime(display_data.index)
            display_data.index = display_data.index.strftime('%Y-%m-%d')
            display_data = display_data.sort_index(ascending=False)
            
            columns_to_display = ['Close', 'MA_5', 'MA_20', 'MA_60', 'Daily_Return', 'Cumulative_Return']
            
            available_columns = [col for col in columns_to_display if col in display_data.columns]
            
            column_names = {
                'Close': '基準価額',
                'MA_5': '移動平均(5日)',
                'MA_20': '移動平均(20日)',
                'MA_60': '移動平均(60日)',
                'Daily_Return': '日次リターン(%)',
                'Cumulative_Return': '累積リターン(%)'
            }
            
            display_data = display_data[available_columns]
            display_data.columns = [column_names.get(col, col) for col in display_data.columns]
            
            st.dataframe(display_data.style.format('{:.2f}'), use_container_width=True)
            
            csv = display_data.to_csv()
            st.download_button(
                label="CSVダウンロード",
                data=csv,
                file_name=f"{selected_fund}_data.csv",
                mime="text/csv",
            )
    
    st.markdown("---")
    st.caption("データソース: J-Quants API")
    st.caption("最終更新日: " + datetime.now().strftime("%Y年%m月%d日"))
