import pandas as pd, re, random, io
from collections import defaultdict

# ---- スケジュール計算ロジック（Colab のまま） ----
SPACE = 4
def shift_sort_key(col):
    day = int(re.match(r'(\d+)', col).group(1))
    sub = int(re.search(r'-(\d)', col).group(1)) if '-' in col else 0
    return (day, sub)

def build_schedule(df_raw: pd.DataFrame):
    doctors   = df_raw['Name'].tolist()
    group_map = df_raw.set_index('Name')['Group'].to_dict()
    avail_df  = 1 - df_raw.drop(columns=['Group','Name'])
    shift_cols = sorted(avail_df.columns, key=shift_sort_key)

    def day_of(c): return shift_sort_key(c)[0]
    def kind(c):   return 'holiday_double' if '-1' in c else 'single'
    shift_day  = {c: day_of(c) for c in shift_cols}
    shift_kind = {c: kind(c)   for c in shift_cols}

    def can_work(doc, col, last):
        return avail_df.loc[df_raw['Name']==doc, col].iat[0]==1 and shift_day[col]-last[doc] >= SPACE

    duty, last, duty_cnt = defaultdict(dict), {d:-10 for d in doctors}, defaultdict(int)
    oncall, oncall_cnt   = {}, defaultdict(int)
    g1 = [d for d in doctors if group_map[d]==1]
    g0 = [d for d in doctors if group_map[d]==0]
    hd = [c for c in shift_cols if shift_kind[c]=='holiday_double']
    sg = [c for c in shift_cols if shift_kind[c]=='single']

    random.shuffle(g1)
    for doc in g1:                   # Group1 duty = 2
        for colset in (hd, sg):
            for col in random.sample(colset, len(colset)):
                if 'G1' in duty[col].values(): continue
                if can_work(doc,col,last):
                    duty[col][doc]='G1'; duty_cnt[doc]+=1; last[doc]=shift_day[col]
                    if duty_cnt[doc]==2: break
            if duty_cnt[doc]==2: break

    random.shuffle(g0)               # Group0 duty 1〜2
    for doc in g0:
        for col in shift_cols:
            need = (shift_kind[col]=='holiday_double' and 'G0' not in duty[col].values()) \
                   or (shift_kind[col]=='single' and not duty[col])
            if need and can_work(doc,col,last):
                duty[col][doc]='G0'; duty_cnt[doc]+=1; last[doc]=shift_day[col]
                break

    for col in shift_cols:           # fill residues
        if shift_kind[col]=='holiday_double' and 'G0' not in duty[col].values():
            cand=[d for d in g0 if duty_cnt[d]<2 and can_work(d,col,last)]
            if cand: doc=random.choice(cand); duty[col][doc]='G0'; duty_cnt[doc]+=1; last[doc]=shift_day[col]
        elif shift_kind[col]=='single' and not duty[col]:
            cand=[d for d in g0 if duty_cnt[d]<2 and can_work(d,col,last)]
            if cand: doc=random.choice(cand); duty[col][doc]='G0'; duty_cnt[doc]+=1; last[doc]=shift_day[col]

    for col in sg:                   # on‑call (G0)
        if 'G1' in duty[col].values():
            cand=[d for d in g0 if d not in duty[col] and can_work(d,col,last)]
            if not cand: cand=[d for d in g0 if d not in duty[col]]
            doc=random.choice(cand); oncall[col]=doc; oncall_cnt[doc]+=1; last[doc]=shift_day[col]

    # ---- DataFrame 出力 ----
    rows=[]
    for col in shift_cols:
        rows.append({'Shift':col,
                     'Duty_G0':', '.join([d for d,g in duty[col].items() if g=='G0']),
                     'Duty_G1':', '.join([d for d,g in duty[col].items() if g=='G1']),
                     'Oncall_G0': oncall.get(col,'')})
    schedule=pd.DataFrame(rows)

    summary=pd.DataFrame({
        'Group':[group_map[d] for d in doctors],
        'Duty':[duty_cnt[d] for d in doctors],
        'Oncall':[oncall_cnt[d] for d in doctors]
    }, index=doctors)
    summary['Total']=summary['Duty']+summary['Oncall']
    return schedule, summary

# ---- Streamlit UI ----
import streamlit as st
st.set_page_config(page_title="Duty Scheduler", layout="centered")
st.title("当直自動割付アプリ")

uploaded = st.file_uploader("当直希望 CSV をアップロード (0=可,1=不可)", type=["csv"])
if uploaded:
    df_raw = pd.read_csv(uploaded, encoding='cp932')
    schedule, summary = build_schedule(df_raw)

    st.subheader("スケジュール")
    st.dataframe(schedule, hide_index=True, use_container_width=True)

    st.subheader("各医師の回数")
    st.dataframe(summary, use_container_width=True)

    # Excel バイト列作成
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        schedule.to_excel(writer, sheet_name="Schedule", index=False)
        summary.to_excel(writer, sheet_name="Summary")
    st.download_button("Excel をダウンロード", buffer.getvalue(),
                       file_name="schedule_target_counts.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("まずは CSV をアップロードしてください。")
