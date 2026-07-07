import math
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="LactoSim | 락타아제 유당분해 예측 앱",
    page_icon="🥛",
    layout="wide"
)

ASSET_DIR = Path(__file__).parent / "assets"

MW_LACTOSE = 342.30
MW_GLUCOSE = 180.16
MW_GALACTOSE = 180.16

st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1180px;
    }
    .hero {
        padding: 26px 30px;
        border-radius: 28px;
        background: linear-gradient(135deg, #eef6ff 0%, #f8fbff 52%, #fff7e8 100%);
        border: 1px solid #dbeafe;
        margin-bottom: 18px;
    }
    .hero h1 {
        margin: 0;
        font-size: 2.25rem;
        color: #1f2a44;
        line-height: 1.2;
    }
    .hero p {
        margin: 10px 0 0 0;
        color: #516070;
        font-size: 1.05rem;
    }
    .card {
        padding: 18px 18px;
        border-radius: 22px;
        border: 1px solid #e5e7eb;
        background: white;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        min-height: 118px;
    }
    .card-title {
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 8px;
    }
    .card-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: #1f2a44;
    }
    .note {
        padding: 14px 18px;
        border-radius: 18px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        color: #334155;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def temperature_factor(temp_c: float, optimal_temp_c: float, sigma: float) -> float:
    return math.exp(-((temp_c - optimal_temp_c) ** 2) / (2 * sigma ** 2))

def simulate_lactase(
    initial_lactose_g: float,
    total_time_min: int,
    enzyme_factor: float,
    temperature_c: float,
    k_ref: float,
    optimal_temp_c: float,
    sigma: float,
    points: int = 151
) -> pd.DataFrame:
    t_factor = temperature_factor(temperature_c, optimal_temp_c, sigma)
    k_eff = k_ref * enzyme_factor * t_factor

    times = np.linspace(0, total_time_min, points)
    lactose_remaining_g = initial_lactose_g * np.exp(-k_eff * times)
    lactose_decomposed_g = initial_lactose_g - lactose_remaining_g

    decomposed_mol = lactose_decomposed_g / MW_LACTOSE
    glucose_g = decomposed_mol * MW_GLUCOSE
    galactose_g = decomposed_mol * MW_GALACTOSE
    hydrolysis_rate = (lactose_decomposed_g / initial_lactose_g) * 100

    return pd.DataFrame({
        "시간(min)": times,
        "유당 잔존량(g)": lactose_remaining_g,
        "분해된 유당량(g)": lactose_decomposed_g,
        "포도당 생성량(g)": glucose_g,
        "갈락토스 생성량(g)": galactose_g,
        "유당분해율(%)": hydrolysis_rate,
        "온도 보정 계수": t_factor,
        "최종 반응속도상수 k_eff": k_eff
    })

def card(title, value, unit=""):
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">{title}</div>
            <div class="card-value">{value}{unit}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

left, right = st.columns([1.25, 1])

with left:
    st.markdown(
        """
        <div class="hero">
            <h1>LactoSim</h1>
            <p>락타아제 처리 조건에 따른 유당 잔존량, 생성당, 유당분해율을 예측하는 탐구용 웹앱</p>
        </div>
        """,
        unsafe_allow_html=True
    )
with right:
    st.image(str(ASSET_DIR / "logo.svg"))

with st.sidebar:
    st.header("시뮬레이션 조건")
    st.caption("값을 바꾸면 결과와 그래프가 자동으로 갱신됩니다.")

    initial_lactose_g = st.number_input("초기 유당량(g)", min_value=0.1, max_value=100.0, value=5.0, step=0.1)
    total_time_min = st.slider("처리 시간(min)", min_value=0, max_value=360, value=120, step=10)
    enzyme_factor = st.slider("효소량 배수", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
    temperature_c = st.slider("처리 온도(℃)", min_value=0, max_value=80, value=37, step=1)

    st.divider()
    st.subheader("모델 설정")
    k_ref = st.slider("기준 반응속도상수 k_ref", min_value=0.001, max_value=0.100, value=0.015, step=0.001, format="%.3f")
    optimal_temp_c = st.slider("최적 온도 T_opt(℃)", min_value=20, max_value=70, value=37, step=1)
    sigma = st.slider("온도 민감도 σ", min_value=5, max_value=30, value=12, step=1)

df = simulate_lactase(
    initial_lactose_g=initial_lactose_g,
    total_time_min=total_time_min,
    enzyme_factor=enzyme_factor,
    temperature_c=temperature_c,
    k_ref=k_ref,
    optimal_temp_c=optimal_temp_c,
    sigma=sigma
)

final = df.iloc[-1]
t_factor = final["온도 보정 계수"]
k_eff = final["최종 반응속도상수 k_eff"]

st.subheader("최종 예측 결과")
c1, c2, c3, c4 = st.columns(4)
with c1:
    card("유당 잔존량", f"{final['유당 잔존량(g)']:.2f}", " g")
with c2:
    card("포도당 생성량", f"{final['포도당 생성량(g)']:.2f}", " g")
with c3:
    card("갈락토스 생성량", f"{final['갈락토스 생성량(g)']:.2f}", " g")
with c4:
    card("유당분해율", f"{final['유당분해율(%)']:.1f}", " %")

st.markdown(
    f"""
    <div class="note">
        현재 조건에서 온도 보정 계수는 <b>{t_factor:.3f}</b>, 
        최종 반응속도상수 k_eff는 <b>{k_eff:.4f}</b>입니다.
    </div>
    """,
    unsafe_allow_html=True
)

tab_home, tab_chart, tab_compare, tab_data, tab_report = st.tabs(
    ["원리 그림", "그래프", "조건 비교", "데이터", "보고서 설명"]
)

with tab_home:
    st.image(str(ASSET_DIR / "reaction_diagram.svg"))
    st.image(str(ASSET_DIR / "process_flow.svg"))
    st.image(str(ASSET_DIR / "temperature_effect.svg"))

with tab_chart:
    st.subheader("시간에 따른 물질량 변화")
    chart_df = df.set_index("시간(min)")[
        ["유당 잔존량(g)", "포도당 생성량(g)", "갈락토스 생성량(g)"]
    ]
    st.line_chart(chart_df)

    st.subheader("시간에 따른 유당분해율 변화")
    st.line_chart(df.set_index("시간(min)")[["유당분해율(%)"]])

with tab_compare:
    st.subheader("온도 또는 효소량 조건 비교")

    compare_mode = st.radio("비교 기준", ["온도 비교", "효소량 비교"], horizontal=True)

    if compare_mode == "온도 비교":
        selected_temperatures = st.multiselect(
            "비교할 온도(℃)",
            [10, 20, 30, 37, 45, 55, 65],
            default=[20, 37, 55]
        )
        compare_df = pd.DataFrame({"시간(min)": np.linspace(0, total_time_min, 151)})
        for temp in selected_temperatures:
            temp_df = simulate_lactase(
                initial_lactose_g=initial_lactose_g,
                total_time_min=total_time_min,
                enzyme_factor=enzyme_factor,
                temperature_c=temp,
                k_ref=k_ref,
                optimal_temp_c=optimal_temp_c,
                sigma=sigma
            )
            compare_df[f"{temp}℃"] = temp_df["유당분해율(%)"]
        st.line_chart(compare_df.set_index("시간(min)"))
    else:
        selected_enzymes = st.multiselect(
            "비교할 효소량 배수",
            [0.5, 1.0, 1.5, 2.0, 3.0, 5.0],
            default=[0.5, 1.0, 2.0]
        )
        compare_df = pd.DataFrame({"시간(min)": np.linspace(0, total_time_min, 151)})
        for enz in selected_enzymes:
            enz_df = simulate_lactase(
                initial_lactose_g=initial_lactose_g,
                total_time_min=total_time_min,
                enzyme_factor=enz,
                temperature_c=temperature_c,
                k_ref=k_ref,
                optimal_temp_c=optimal_temp_c,
                sigma=sigma
            )
            compare_df[f"{enz}배"] = enz_df["유당분해율(%)"]
        st.line_chart(compare_df.set_index("시간(min)"))

with tab_data:
    st.subheader("계산 데이터")
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "CSV 다운로드",
        data=csv,
        file_name="lactosim_result.csv",
        mime="text/csv"
    )

with tab_report:
    st.subheader("보고서에 넣을 수 있는 설명")
    st.markdown(
        """
본 후속활동에서는 락타아제 처리 조건에 따른 유당분해율 변화를 예측하기 위해 웹앱 형태의 시뮬레이션 프로그램을 제작하였다. 
프로그램은 초기 유당량, 처리 시간, 효소량, 온도 조건을 입력하면 유당 잔존량, 포도당 생성량, 갈락토스 생성량, 유당분해율을 자동으로 계산하고 그래프로 시각화하도록 설계하였다.

계산 모델은 유당 잔존량이 시간에 따라 지수적으로 감소한다고 가정하였다. 
효소량은 반응속도상수에 비례적으로 반영하였고, 온도는 최적 온도에서 멀어질수록 효소 활성이 감소하는 방식으로 보정하였다. 
이를 통해 락타아제의 효소 작용을 개념적으로 이해하는 수준을 넘어, 유당 저감 식품 제조 과정에서 처리 시간, 효소량, 온도 조건을 조절하는 공정 설계의 관점으로 확장하였다.

다만 본 모델은 pH 변화, 생성물 저해, 효소의 열변성, 우유 속 단백질과 지방의 영향 등을 반영하지 않은 단순화된 예측 모델이다. 
따라서 실제 식품 공정에 적용하려면 실험값을 바탕으로 반응속도상수와 온도 보정식을 보정하는 과정이 필요하다.
        """
    )

    st.subheader("모델식")
    st.latex(r"L(t) = L_0 e^{-k_{eff}t}")
    st.latex(r"k_{eff} = k_{ref} \times E_{factor} \times T_{factor}")
    st.latex(r"T_{factor} = e^{-\frac{(T - T_{opt})^2}{2\sigma^2}}")

st.caption("탐구용 단순 예측 모델입니다. 실제 제조 조건 결정에는 실험값 기반 보정이 필요합니다.")
