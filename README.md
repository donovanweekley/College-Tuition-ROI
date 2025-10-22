# College-Tuition-ROI
This project is a data analysis of the financial Return on Investment (ROI) for various US colleges and universities. The central goal is to estimate the "break-even time" for a degree by comparing its total cost to the additional earnings a graduate can expect compared to a high school graduate.

The complete analysis is available in the Jupyter Notebook: tuition_roi.ipynb.

How to Run This Project
Clone the repository:

git clone https://github.com/donovanweekley/College-Tuition-ROI.git
Install dependencies:

pip install pandas plotly seaborn
Download the data:

This project requires the "Most Recent Cohorts" (Institution-Level) data file from the College Scorecard.

Go to: collegescorecard.ed.gov/data/

Download the file (it will be a large CSV) and place it in the main project folder. Ensure the filename matches: Most-Recent-Cohorts-Institution_05192025.csv

(Note: The p24.xlsx file is already included in this repository.)

Run the notebook: Open and run the tuition_roi.ipynb notebook.

Analysis & Key Features
Data Pipeline: Ingested, cleaned, and processed data from multiple sources using pandas, handling missing/suppressed values ("PS") and converting data types.

Metric Engineering: Developed two key metrics for the analysis:

"Earnings Premium": The 10-year median earnings of a college graduate minus the national median earnings of a high school graduate.

"Break-Even Years": The estimated time (in years) to pay back the total cost of the degree.

Data Visualization: Conducted exploratory data analysis using matplotlib, seaborn, and plotly to identify key trends.

Visualizations Included
Top 10 Schools (Bar Chart): A bar chart identifying the top 10 institutions with the fastest (lowest) positive break-even times.

Cost vs. Earnings (Scatter Plot): A regression plot analyzing the relationship between an institution's Total_Cost and its Earnings_Premium, complete with a line of best fit and a 95% confidence interval.

Geographic Trends (Choropleth Map): An interactive choropleth map (using plotly) that visualizes the average break-even years by state.
