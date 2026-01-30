# 🎓 EcoPackAI: Demo Walkthrough Guide

This document serves as a script and guide for demonstrating the EcoPackAI system for academic evaluation or stakeholder presentation.

---

## 1. Introduction (1 Minute)
*   **Hook**: "Packaging waste is a global crisis. Businesses want to be sustainable, but balancing cost and impact is hard."
*   **Solution**: "EcoPackAI is a data-driven recommendation system that uses Machine Learning to find that balance instantly."
*   **Tech Highlight**: "Built with Flask, PostgreSQL, and XGBoost models, it provides real-time, optimized suggestions."

---

## 2. The User Journey (Demo Flow)

### Step 1: Landing Page
*   **Action**: Open the application home page.
*   **Narrative**: "We start at a clean, modern interface designed to be intuitive. Notice the distinct 'Get Started' call to action."
*   **Visual**: Point out the "Rich Aesthetics" (Dark mode, glassmorphism) which ensures a premium user experience.

### Step 2: Getting Recommendations (The Core Feature)
*   **Action**: Navigate to the **Recommendation** page.
*   **Input**:
    *   **Category**: Select "Electronics".
    *   **Weight**: Enter `2.5` kg.
    *   **Fragility**: Select "High".
*   **Action**: Click "Get Recommendations".
*   **Narrative**: "Behind the scenes, the system filters 100+ materials. It uses our random forest model to predict the *current market cost* and our XGBoost model to calculate the *CO₂ footprint* specific to this weight."

### Step 3: Analyzing Results
*   **Action**: Scroll to the results table.
*   **Narrative**: 
    *   "Here we see the top ranked materials."
    *   "Corrugated Bubble Wrap comes first because it offers high protection (High Fragility) with a lower carbon score than Styrofoam."
    *   "The 'Suitability Score' combines these factors into a single metric."

### Step 4: Business Intelligence Dashboard
*   **Action**: Click on "Analytics Dashboard" in the navigation bar.
*   **Narrative**: "For managers, decision-making happens here."
*   **Visual Points**:
    *   **KPI Cards**: "We see a potential **45% CO₂ Reduction** if we switch to recommended materials."
    *   **CO₂ Analysis Chart**: "This bar chart compares the carbon footprint of our entire inventory."
    *   **Category Distribution**: "This pie chart shows our material diversity."
*   **Insight**: "The dashboard proves that sustainable options aren't just 'green'—they are often cost-competitive."

---

## 3. Technical Deep Dive (Optional Q&A)

If asked about the **ML Models**:
> "We trained models on a dataset of material properties. The Cost Model (Random Forest) achieved an 85% accuracy in predicting unit costs based on strength and weight."

If asked about **Scalability**:
> "The backend uses a modular 'Service Layer' pattern and is container-ready (Docker/Render), allowing it to scale easily with increased data load."

---

## 4. Closing
"EcoPackAI bridges the gap between intention and action, making sustainable packaging accessible and data-backed."
