import pandas as pd
import plotly.express as px
import streamlit as st

from analytics import (
    compare_all_models,
    condition_frequency,
    correlation_matrix,
    dataset_overview,
    evaluate_production_model,
    feature_importance_df,
    generate_insights,
    load_dataset,
    numeric_summary_by_risk,
    symptom_frequency,
    symptom_risk_crosstab,
)

st.set_page_config(page_title="Smart Care Analytics", page_icon="📊", layout="wide")

st.title("📊 Data Analytics Dashboard")
st.caption(
    "Exploratory data analysis, clinical patterns, and model performance for Smart Care triage data"
)

df = load_dataset()
overview = dataset_overview(df)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Patients", overview["total_patients"])
col2.metric("Avg Age", overview["avg_age"])
col3.metric("Avg Heart Rate", f"{overview['avg_heart_rate']} bpm")
col4.metric("Avg Systolic BP", f"{overview['avg_systolic_bp']} mmHg")
col5.metric("Dominant Risk", overview["dominant_risk"])

st.divider()

tab_eda, tab_clinical, tab_model, tab_compare = st.tabs(
    ["Dataset EDA", "Clinical Patterns", "Model Performance", "Model Comparison"]
)

with tab_eda:
    st.subheader("Dataset Overview")
    left, right = st.columns(2)

    with left:
        risk_df = (
            pd.DataFrame.from_dict(overview["risk_counts"], orient="index", columns=["Count"])
            .reset_index()
            .rename(columns={"index": "Risk_Level"})
        )
        fig = px.pie(
            risk_df,
            names="Risk_Level",
            values="Count",
            color="Risk_Level",
            color_discrete_map={"Low": "#22c55e", "Medium": "#f59e0b", "High": "#ef4444"},
            title="Risk Level Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        gender_df = (
            pd.DataFrame.from_dict(overview["gender_counts"], orient="index", columns=["Count"])
            .reset_index()
            .rename(columns={"index": "Gender"})
        )
        fig = px.bar(gender_df, x="Gender", y="Count", title="Gender Distribution", text="Count")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Age Distribution by Risk Level")
    fig = px.histogram(
        df,
        x="Age",
        color="Risk_Level",
        barmode="overlay",
        opacity=0.75,
        color_discrete_map={"Low": "#22c55e", "Medium": "#f59e0b", "High": "#ef4444"},
        nbins=20,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Summary Statistics by Risk Level")
    st.dataframe(numeric_summary_by_risk(df), use_container_width=True)

    st.subheader("Feature Correlation Heatmap")
    corr = correlation_matrix(df)
    fig = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title="Correlation Between Encoded Features and Risk Score",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_clinical:
    st.subheader("Symptom Frequency")
    symptoms = symptom_frequency(df).reset_index()
    symptoms.columns = ["Symptom", "Count"]
    fig = px.bar(symptoms, x="Symptom", y="Count", title="Most Common Symptoms", text="Count")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Pre-existing Condition Frequency")
    conditions = condition_frequency(df).reset_index()
    conditions.columns = ["Condition", "Count"]
    fig = px.bar(conditions, x="Condition", y="Count", title="Most Common Conditions", text="Count")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Vitals by Risk Level")
    vital = st.selectbox("Select vital", ["Heart_Rate", "Systolic_BP", "Temperature"])
    fig = px.box(
        df,
        x="Risk_Level",
        y=vital,
        color="Risk_Level",
        color_discrete_map={"Low": "#22c55e", "Medium": "#f59e0b", "High": "#ef4444"},
        title=f"{vital.replace('_', ' ')} Distribution by Risk Level",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Symptom vs Risk Level")
    symptom_risk = symptom_risk_crosstab(df)
    if not symptom_risk.empty:
        fig = px.imshow(
            symptom_risk,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Blues",
            title="Symptom Count by Risk Level",
        )
        st.plotly_chart(fig, use_container_width=True)

with tab_model:
    st.subheader("Production Model Evaluation (AdaBoost)")

    @st.cache_data(show_spinner="Evaluating production model...")
    def cached_model_eval():
        return evaluate_production_model(df)

    evaluation = cached_model_eval()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Model", evaluation["model_name"])
    m2.metric("Accuracy", f"{evaluation['accuracy']:.1%}")
    m3.metric("Macro F1", f"{evaluation['macro_f1']:.3f}")
    m4.metric("Weighted F1", f"{evaluation['weighted_f1']:.3f}")

    cm = evaluation["confusion_matrix"]
    labels = evaluation["labels"]
    fig = px.imshow(
        cm,
        x=labels,
        y=labels,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Greens",
        title="Confusion Matrix",
        labels=dict(x="Predicted", y="Actual"),
    )
    st.plotly_chart(fig, use_container_width=True)

    report_df = pd.DataFrame(evaluation["classification_report"]).transpose()
    st.subheader("Classification Report")
    st.dataframe(report_df.round(3), use_container_width=True)

    st.subheader("Feature Importance")
    importance = feature_importance_df(df)
    fig = px.bar(
        importance,
        x="Importance",
        y="Feature",
        orientation="h",
        title="AdaBoost Feature Importance",
        text="Importance",
    )
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

with tab_compare:
    st.subheader("Model Benchmarking")
    st.caption("Cross-validated accuracy across all tested classifiers")

    @st.cache_data(show_spinner="Running model comparison (first load may take ~2 min)...")
    def cached_comparison():
        return compare_all_models(df)

    comparison = cached_comparison()
    fig = px.bar(
        comparison,
        x="cv_accuracy",
        y="model",
        orientation="h",
        title="Model Comparison (5-Fold CV Accuracy)",
        text="cv_accuracy",
        color="cv_accuracy",
        color_continuous_scale="Viridis",
    )
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(comparison, use_container_width=True)

st.divider()
st.subheader("Key Data Insights")
for insight in generate_insights(df):
    st.markdown(f"- {insight}")

st.caption(
    "Analytics dashboard supports portfolio demonstrations for data analysis and ML evaluation workflows."
)
