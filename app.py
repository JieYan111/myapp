import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- 網頁設定 ---
st.set_page_config(page_title="我的財富分配機", page_icon="💰")

# --- 標題 ---
st.title("💰 交易員資金分配系統")
st.write("目標：專職 Trader | 財務自由")

# --- 1. 輸入區 ---
st.header("1. 輸入本月收入")
income = st.number_input("輸入金額 (TWD)", value=43000, step=1000)

st.divider()

# --- 2. 設定大方向比例 ---
st.header("2. 設定分配比例 (%)")
col1, col2 = st.columns(2)

with col1:
    p_life = st.number_input("🏠 生活費 (Life)", value=40)
    p_invest = st.number_input("📈 投資 (Invest)", value=35)

with col2:
    p_random = st.number_input("🎲 隨機/學習 (Random)", value=20)
    p_kid = st.number_input("👶 小孩 (Kid)", value=5)

# 檢查總和
total_percent = p_life + p_invest + p_random + p_kid
if total_percent != 100:
    st.error(f"⚠️ 目前總和為 {total_percent}%，請調整至 100%！")
else:
    st.success("✅ 比例正確 (100%)")

# --- 計算大方向金額 ---
m_life = int(income * (p_life / 100))
m_invest = int(income * (p_invest / 100))
m_random = int(income * (p_random / 100))
m_kid = int(income * (p_kid / 100))

# --- 顯示大方向結果 ---
st.subheader("📊 分配結果")
c1, c2, c3, c4 = st.columns(4)
c1.metric("生活費", f"${m_life:,}")
c2.metric("投資總額", f"${m_invest:,}")
c3.metric("隨機運用", f"${m_random:,}")
c4.metric("小孩資金", f"${m_kid:,}")

st.divider()

# --- 3. 投資細項分配 (你的 006208 / BTC / VOO) ---
st.header("3. 投資帳戶細項分配")
st.write(f"目前投資總額：**${m_invest:,}**")

# 設定投資內部的比例
col_i1, col_i2, col_i3 = st.columns(3)
with col_i1:
    p_006208 = st.text_input("🇹🇼 006208 比例", value="33") # 使用字串輸入避免小數點問題，稍後轉型
with col_i2:
    p_btc = st.text_input("₿ Bitcoin 比例", value="20")
with col_i3:
    p_voo = st.text_input("🇺🇸 VOO 比例", value="47")

# 計算細項
try:
    # 轉成整數計算
    pp_006208 = float(p_006208)
    pp_btc = float(p_btc)
    pp_voo = float(p_voo)
    
    # 檢查細項總和
    inv_sub_total = pp_006208 + pp_btc + pp_voo
    
    m_006208 = int(m_invest * (pp_006208 / 100))
    m_btc = int(m_invest * (pp_btc / 100))
    m_voo = int(m_invest * (pp_voo / 100))
    
    if inv_sub_total != 100:
         st.warning(f"⚠️ 投資細項總和為 {inv_sub_total}%，建議調整為 100%")
    
    # 顯示細項金額
    ic1, ic2, ic3 = st.columns(3)
    ic1.info(f"006208: ${m_006208:,}")
    ic2.error(f"Bitcoin: ${m_btc:,}") # 紅色顯示提醒風險
    ic3.success(f"VOO: ${m_voo:,}")

except:
    st.error("請輸入數字")

# --- 視覺化圖表 ---
st.divider()
st.subheader("🍰 資產大餅圖")
labels = ['Life', 'Invest', 'Random', 'Kid']
sizes = [m_life, m_invest, m_random, m_kid]
fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
ax.axis('equal') 
st.pyplot(fig)
