# YouTube Channel Analytics Dashboard
An interactive dashboard to view your channel's performance over several different measures and also analyze each video's performance, built using Streamlit.</br>
* The dataset contains 4 .csv files pertaining to a YouTuber's channel. Source : Kaggle
*  The dashboard has two sections :
1. Aggregate Metrics
* This section displays a few metrics comparing performance over the last 6 months with the entire year.
2. Individual Video Analysis
* Here, one can select a particular video and view the geographic distribution of viewers and also their subscriber status.
* Also, one can observe the rate at which the number of views increases over time, with the 20th percentile, 80th percentile, 50th percentile (median) and increase in views over the first 30 days for the selected video.
# Instructions to run
* After cloning the repository to your system, please install the requirements as seen in the text file included in the repo. 
* To run the app, please run the command "streamlit run YT_Dash.py"
# Notes
* This is a work in progress.
* Currently working on conducting natural language processing on the comment data for sentiment analysis and finding frequently asked questions to develop a bot to answer them.
* Ran into an issue with Firefox where the horizontal scroll bar overlaps the last row in the dataframe when displayed on Streamlit. It is not reproducible on Safari though. Internet answers are also absent, perhaps a deeper search will help.
