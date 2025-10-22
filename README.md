# College-Tuition-ROI

This project is a data analysis of the financial Return on Investment (ROI) for various US colleges and universities. The central goal is to estimate the "break-even time" for a degree by comparing its total cost to the additional earnings a graduate can expect compared to a high school graduate.

The complete analysis is available in the Jupyter Notebook: tuition_roi.ipynb.

## Key Findings
Top Performers: The analysis identified a number of institutions with a rapid return on investment, with the fastest estimated break-even times being just under 2 years.

Cost vs. Earnings: A weak positive correlation was found between a college's total cost and its 10-year earnings premium. The wide confidence interval in the regression plot suggests that a higher price tag does not reliably guarantee a proportionally higher earnings premium.

Geographic Disparity: ROI varies significantly by state. The interactive choropleth map reveals regional trends, highlighting areas where the average break-even time is considerably lower or higher than the national average.



## How to Run This Project
Clone the repository:

git clone https://github.com/donovanweekley/College-Tuition-ROI.git
Install dependencies:

pip install pandas plotly seaborn
Download the data:

This project requires the "Most Recent Cohorts" (Institution-Level) data file from the College Scorecard, as it is too large for this repository.

Go to: collegescorecard.ed.gov/data/

Download the data and place it in the project folder with the filename: Most-Recent-Cohorts-Institution_05192025.csv

(Note: The p24.xlsx file is already included.)

Run the notebook: Open and run the tuition_roi.ipynb notebook.

## Methodology & Assumptions
This analysis relies on several key assumptions:

Earnings Baseline: Uses a national median for high school graduates. It does not account for regional differences in cost of living or wages.

Cost Calculation: Total_Cost is estimated as Cost_Per_Year * 4. This is a simplification and does not account for students who take more or less than four years to graduate.

Scope: The analysis is at the institution level and does not differentiate by major (e.g., engineering vs. liberal arts), which is one of the largest predictors of post-graduation earnings.

Data Limitations: The College Scorecard data includes suppressed values ("PS") for privacy. These rows were dropped, which could potentially skew the results for institutions with smaller cohort sizes.

## Future Work
This analysis could be expanded in several ways:

Integrate major-specific earnings data to provide more granular and actionable ROI estimates.

Incorporate regional cost-of-living data to create a more accurate, location-adjusted earnings premium.

Analyze the impact of graduation rates and average student debt on the final break-even calculation.

## Technology Used
Python

Jupyter Notebook

Pandas (for data manipulation and cleaning)

Matplotlib & Seaborn (for static visualizations)

Plotly (for interactive mapping)
