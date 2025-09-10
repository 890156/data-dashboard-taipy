# Interactive Data Dashboard

This project is an implementation of the tutorial from KDNuggets:
[Creating Slick Data Dashboards with Python, Taipy & Google Sheets](https://www.kdnuggets.com/creating-slick-data-dashboards-with-python-taipy-google-sheets)

It creates an interactive data dashboard using Python, Taipy, and Google Sheets. This is a **direct implementation of the tutorial without any modifications**.

## Tools Used
- Python  
- Taipy  
- Google Sheets  
- Plotly  
- gspread & oauth2client  

## How to Run
1. Create a project on Google Cloud and enable Google Sheets API.  
2. Get `credentials.json` from your service account.  
3. Share your Google Sheet with your service account email.  
4. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the dashboard:
   ```bash
   python app.py
   ```

