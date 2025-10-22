# College-Tuition-ROI
This project is a data analysis of the financial Return on Investment (ROI) for various US colleges and universities. The central goal is to estimate the "break-even time" for a degree by comparing its total cost to the additional earnings a graduate can expect compared to a high school graduate.
The complete analysis is available in the Jupyter Notebook: tuition_roi.ipynb.

Data Sources
Institution Data: College Scorecard (Most-Recent-Cohorts-Institution_05192025.csv)

Earnings Baseline: ACS/CPS Tables (p24.xlsx) for national median earnings by education level.

Analysis & Key Features
Data Pipeline: Ingested, cleaned, and processed data from multiple sources using pandas, handling missing/suppressed values ("PS") and converting data types.

Metric Engineering: Developed two key metrics for the analysis:

"Earnings Premium": The 10-year median earnings of a college graduate minus the national median earnings of a high school graduate.

"Break-Even Years": The estimated time (in years) to pay back the total cost of the degree, calculated by dividing the Total_Cost by the Earnings_Premium.

Data Visualization: Conducted exploratory data analysis using matplotlib, seaborn, and plotly to identify key trends.

Visualizations Included
Top 10 Schools (Bar Chart): A bar chart identifying the top 10 institutions with the fastest (lowest) positive break-even times.

Cost vs. Earnings (Scatter Plot): A regression plot analyzing the relationship between an institution's Total_Cost and its Earnings_Premium, complete with a line of best fit and a 95% confidence interval.

Geographic Trends (Choropleth Map): An interactive choropleth map (using plotly) that visualizes the average break-even years by state.

Technology Used
Python

Pandas

Matplotlib

Seaborn

Plotly

Jupyter Notebook
