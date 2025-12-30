import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import datetime
import os
import json 
import matplotlib.font_manager as fm

# --- 網頁設定 ---
st.set_page_config(page_title="Trader 資金戰情室", page_icon="💰", layout="wide") 

# ==========================================
# 🔧 字型修復專區
# ==========================================
def set_chinese_font():
    font_path = "NotoSansTC-VariableFont_wght.ttf" 
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()
    else:
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS'] 
    plt.rcParams['axes.unicode_minus'] = False

set_chinese_font()

# ==========================================
# 💾 系統記憶功能 (存檔/讀檔)
# ==========================================
st.sidebar.title("⚙️ 系統設定")
st.sidebar.caption("雲端會重置資料，請善用存檔。")

# 1. 存檔
current_data = {
    "portfolio": st.session_state.get('portfolio', []),
    "asset_bank": st.session_state.get('asset_bank', []),
    "asset_crypto": st.session_state.get('asset_crypto', []),
    "asset_stock": st.session_state.get('asset_stock', []),
    "settings": {
        "income": st.session_state.get('user_income', 43000),
        "p_life": st.session_state.get('p_life', 40),
        "p_invest": st.session_state.get('p_invest', 35),
        "p_random": st.session_state.get('p_random', 20),
        "p_kid": st.session_state.get('p_kid', 5)
    }
}
json_str = json.dumps(current_data, ensure_ascii=False, indent=4)

st.sidebar.download_button(
    label="💾 下載備份檔 (Save)",
    data=json_str,
    file_name="trader_data_backup.json",
    mime="application/json"
)

st.sidebar.divider()

# 2. 讀檔
uploaded_file = st.sidebar.file_uploader("📂 載入備份檔 (Load)", type=["json"])

if uploaded_file is not None:
    try:
        loaded_data = json.load(uploaded_file)
        
        # 覆蓋資料
        st.session_state.portfolio = loaded_data.get("portfolio", [])
        st.session_state.asset_bank = loaded_data.get("asset_bank", [])
        st.session_state.asset_crypto = loaded_data.get("asset_crypto", [])
        st.session_state.asset_stock = loaded_data.get("asset_stock", [])
        
        # 載入設定值 (寫入 session_state)
        settings = loaded_data.get("settings", {})
        st.session_state.user_income = settings.get("income", 43000)
        st.session_state.p_life = settings.get("p_life", 40)
        st.session_state.p_invest = settings.get("p_invest", 35)
        st.session_state.p_random = settings.get("p_random", 20)
        st.session_state.p_kid = settings.get("p_kid", 5)

        st.sidebar.success("✅ 讀取成功！(請稍候或手動調整任一數值以刷新畫面)")
        
    except Exception as e:
        st.sidebar.error(f"讀取失敗：{e}")

# ==========================================
# 0. 初始化 Session State (設定預設值)
# ==========================================
# 這裡先設定好預設值，下面的 widget 就會自動抓取，不需要再寫 value=...
if 'user_income' not in st.session_state: st.session_state.user_income = 43000
if 'p_life' not in st.session_state: st.session_state.p_life = 40
if 'p_invest' not in st.session_state: st.session_state.p_invest = 35
if 'p_random' not in st.session_state: st.session_state.p_random = 20
if 'p_kid' not in st.session_state: st.session_state.p_kid = 5

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"商品": "006208", "金額": 6000},
        {"商品": "Bitcoin", "金額": 6000},
        {"商品": "VOO", "金額": 3000}
    ]

if 'asset_bank' not in st.session_state:
    st.session_state.asset_bank = [
        {"項目": "緊急預備金(定存)", "金額": 400000},
        {"項目": "生活費活存", "金額": 200000},
        {"項目": "小孩帳戶", "金額": 0}
    ]

if 'asset_crypto' not in st.session_state:
    st.session_state.asset_crypto = [
        {"項目": "冷錢包 (BTC)", "金額": 0},
        {"項目": "交易所 (USDT)", "金額": 0}
    ]

if 'asset_stock' not in st.session_state:
    st.session_state.asset_stock = [
        {"項目": "台股證券戶", "金額": 0},
        {"項目": "美股證券戶", "金額": 0},
        {"項目": "期貨保證金", "金額": 90000}
    ]

st.title("💰 Trader 資金戰情室")
st.caption("目標：專職交易 | 嚴格風控 | 資產增值")

# ==========================================
# 1. 流量管理 (本月收入)
# ==========================================
with st.container():
    st.header("1. 流量管理 (Income Flow)")
    
    col_inc, col_ratio = st.columns([1, 3])
    with col_inc:
        # 🔥 修正點：這裡移除了 value=...，因為 key 已經存在
        income = st.number_input("本月收入 (TWD)", step=1000, key="user_income")
    
    with col_ratio:
        c1, c2, c3, c4 = st.columns(4)
        # 🔥 修正點：這裡也都移除了 value=...
        with c1: p_life = st.number_input("生活費 %", key="p_life")
        with c2: p_invest = st.number_input("投資 %", key="p_invest")
        with c3: p_random = st.number_input("隨機 %", key="p_random")
        with c4: p_kid = st.number_input("小孩 %", key="p_kid")

    total_percent = p_life + p_invest + p_random + p_kid
    
    if total_percent != 100:
        st.error(f"⚠️ 比例錯誤！目前總和為 {total_percent}% (必須等於 100%)")
        b_life = b_invest = b_random = b_kid = 0 
    else:
        b_life = int(income * (p_life / 100))
        b_invest = int(income * (p_invest / 100))
        b_random = int(income * (p_random / 100))
        b_kid = int(income * (p_kid / 100))
        
        st.write("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(f"🏠 生活 ({p_life}%)", f"${b_life:,}")
        m2.metric(f"📈 投資 ({p_invest}%)", f"${b_invest:,}")
        m3.metric(f"🎲 隨機 ({p_random}%)", f"${b_random:,}")
        m4.metric(f"👶 小孩 ({p_kid}%)", f"${b_kid:,}")

# ==========================================
# 2. 策略管理 (定期定額)
# ==========================================
st.divider()
st.header("2. 策略管理 (DCA Strategy)")

if total_percent == 100:
    with st.expander("⚙️ 調整定期定額項目 (新增/刪除)", expanded=False):
        c_dca1, c_dca2, c_dca3 = st.columns([2, 2, 1])
        with c_dca1: dca_item = st.text_input("DCA 商品名稱")
        with c_dca2: dca_val = st.number_input("DCA 金額", value=3000, step=1000)
        with c_dca3: 
            st.write(""); st.write("")
            if st.button("新增 DCA"):
                if dca_item:
                    st.session_state.portfolio.append({"商品": dca_item, "金額": dca_val})
                    st.rerun()
        
        if st.session_state.portfolio:
            dca_list = [f"{i['商品']} (${i['金額']})" for i in st.session_state.portfolio]
            del_dca = st.selectbox("刪除 DCA 項目", dca_list)
            if st.button("刪除 DCA"):
                st.session_state.portfolio.pop(dca_list.index(del_dca))
                st.rerun()

    if st.session_state.portfolio:
        df_dca = pd.DataFrame(st.session_state.portfolio)
        st.dataframe(df_dca.T, use_container_width=True)
        
        dca_total = df_dca["金額"].sum()
        dca_rem = b_invest - dca_total
        
        if dca_rem >= 0:
            st.success(f"✅ 投資預算 ${b_invest:,} - 設定扣款 ${dca_total:,} = 剩餘閒置 **${dca_rem:,}**")
        else:
            st.error(f"⚠️ 預算透支！超支金額：**${abs(dca_rem):,}**")
else:
    st.warning("請先修正上方收入分配比例至 100%")

# ==========================================
# 3. 存量管理 (總資產盤點)
# ==========================================
st.divider()
st.header("3. 存量管理 (Net Worth)")

col_bank, col_crypto, col_stock = st.columns(3)

def manage_asset_section(title, session_key, icon):
    st.subheader(f"{icon} {title}")
    current_list = st.session_state[session_key]
    df = pd.DataFrame(current_list)
    if not df.empty:
        total = df["金額"].sum()
        st.metric(f"{title} 總值", f"${total:,}")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        total = 0
        st.metric(f"{title} 總值", "$0")
        st.warning("無項目")

    with st.expander(f"✏️ 編輯 {title}"):
        with st.form(key=f"add_{session_key}"):
            new_item = st.text_input("項目名稱")
            new_val = st.number_input("目前市值", value=0, step=1000)
            if st.form_submit_button("新增"):
                st.session_state[session_key].append({"項目": new_item, "金額": new_val})
                st.rerun()
        
        if current_list:
            del_list = [f"{i['項目']} (${i['金額']})" for i in current_list]
            to_del = st.selectbox(f"刪除 {title} 項目", del_list, key=f"del_sel_{session_key}")
            if st.button("刪除", key=f"del_btn_{session_key}"):
                idx = del_list.index(to_del)
                st.session_state[session_key].pop(idx)
                st.rerun()
    return total

with col_bank: sum_bank = manage_asset_section("銀行 (Bank)", "asset_bank", "🏦")
with col_crypto: sum_crypto = manage_asset_section("幣圈 (Crypto)", "asset_crypto", "₿")
with col_stock: sum_stock = manage_asset_section("股票 (Stock)", "asset_stock", "📈")

net_worth = sum_bank + sum_crypto + sum_stock
st.write("---")
st.header(f"💰 總資產 (Net Worth): ${net_worth:,}")

c_chart1, c_chart2 = st.columns(2)
with c_chart1:
    st.subheader("資產類別佔比")
    if net_worth > 0:
        labels = ['銀行', '幣圈', '股票']
        sizes = [sum_bank, sum_crypto, sum_stock]
        colors = ['#66b3ff', '#ffcc99', '#ff9999']
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax1.axis('equal')
        st.pyplot(fig1)

with c_chart2:
    st.subheader("風險屬性分析")
    if net_worth > 0:
        risk_assets = sum_crypto + sum_stock
        safe_assets = sum_bank
        st.progress(risk_assets / net_worth, text=f"⚔️ 攻擊型 (Crypto+Stock): {risk_assets/net_worth*100:.1f}%")
        st.progress(safe_assets / net_worth, text=f"🛡️ 防禦型 (Bank): {safe_assets/net_worth*100:.1f}%")

# ==========================================
# 4. Excel 匯出
# ==========================================
st.divider()
df_flow = pd.DataFrame({
    "項目": ["總收入", "生活費", "投資", "隨機", "小孩"],
    "金額": [income, b_life, b_invest, b_random, b_kid],
    "比例": ["100%", f"{p_life}%", f"{p_invest}%", f"{p_random}%", f"{p_kid}%"]
})

list_all_assets = []
for i in st.session_state.asset_bank: list_all_assets.append({"類別": "銀行", "項目": i["項目"], "金額": i["金額"]})
for i in st.session_state.asset_crypto: list_all_assets.append({"類別": "幣圈", "項目": i["項目"], "金額": i["金額"]})
for i in st.session_state.asset_stock: list_all_assets.append({"類別": "股票", "項目": i["項目"], "金額": i["金額"]})
df_assets_detail = pd.DataFrame(list_all_assets)
df_assets_detail.loc[len(df_assets_detail)] = ["總計", "Net Worth", net_worth]

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_flow.to_excel(writer, sheet_name='1.本月流量', index=False)
    if st.session_state.portfolio:
        pd.DataFrame(st.session_state.portfolio).to_excel(writer, sheet_name='2.定期定額設定', index=False)
    df_assets_detail.to_excel(writer, sheet_name='3.總資產細項', index=False)
buffer.seek(0)
curr_date = datetime.date.today().strftime("%Y%m%d")

st.download_button(
    label="📥 下載完整資產報表 (Excel)",
    data=buffer,
    file_name=f"Trader_Report_{curr_date}.xlsx",
    mime="application/vnd.ms-excel"
)


