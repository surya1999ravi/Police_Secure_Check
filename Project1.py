import pandas as pd 
import streamlit as st
import pymysql

#database connection

def create_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='1234',
            database='securecheck',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection 
    except Exception as e :
        st.error(f"Database connection Error:(e)")
        return None
    

#Fetch data from database
def fetch_data(query):
    connection = create_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()    
                df = pd.DataFrame(result)
                return df
        finally:
            connection.close()
    else:
        return pd.DataFrame()
    

#Streamlit code 

st.set_page_config(page_title="SecureCheck Police Dashboard",layout="wide")
st.title("🚨SecureCheck : Police Check Post Digital Ledger")
st.markdown("**Real-time monitoring and insights for law enforcement**")

#Showing full table 
st.header("Police Logs Overview")
query = "Select * from police_logs"
data = fetch_data(query)
st.dataframe(data,use_container_width=True) #to make the table take up space of the screen width 

#Quick metrics

st.header("Key Metrics")

col1, col2 , col3 , col4 = st.columns(4)

with col1:
    total_stops = data.shape[0]
    st.metric("Total Police Stops", total_stops)

with col2:
    arrests = data[data['stop_outcome'].str.contains("arrest",case=False,na=False)].shape[0]
    st.metric("Total Arrests", arrests)

with col3:
    warning = data[data['stop_outcome'].str.contains("Warning",case=False,na= False)].shape[0]
    st.metric("Total Warnings:",warning)

with col4 :
    drug = data[data['drugs_related_stop']==1].shape[0]
    st.metric("Drug Related Stops",drug)



#Advanced Queries

st.header("Advanced Insights")

select_query1 =[
    "What are the top 10 vehicle_Number involved in drug-related stops?",
    "Which vehicles were most frequently searched?",
    "Which driver age group had the highest arrest rate?"
    "What is the average stop duration for different violations?",
    "What is the gender distribution of drivers stopped in each country?",
    "Which race and gender combination has the highest search rate?",
    "What time of day sees the most traffic stops?",
    "What is the average stop duration for different violations?",
    "Are stops during the night more likely to lead to arrests?",
    "Which violations are most associated with searches or arrests?",
    "Which violations are most common among younger drivers (<25)?",
    "Is there a violation that rarely results in search or arrest?",
    "Which countries report the highest rate of drug-related stops?",
    "What is the arrest rate by country and violation?",
    "Which country has the most stops with search conducted?"
]

query_map1 = {
    "What are the top 10 vehicle_Number involved in drug-related stops?":"SELECT vehicle_number,COUNT(*) AS drug_related_count FROM police_logs WHERE drugs_related_stop = TRUE GROUP BY vehicle_number ORDER BY drug_related_count DESC LIMIT 10;",
    "Which vehicles were most frequently searched?":"SELECT vehicle_number,COUNT(*) AS search_count FROM police_logs WHERE search_conducted = TRUE GROUP BY vehicle_number ORDER BY search_count DESC;",
    "Which driver age group had the highest arrest rate?":"SELECT driver_age, COUNT(*) AS arrest_count FROM police_logs WHERE is_arrested = TRUE GROUP BY driver_age ORDER BY arrest_count DESC LIMIT 1;",
    "What is the average stop duration for different violations?": "select violation, avg(stop_duration) from police_logs group by violation;",
    "What is the gender distribution of drivers stopped in each country?":"SELECT country_name, driver_gender, COUNT(*) AS total_stops FROM police_logs GROUP BY country_name, driver_gender ORDER BY country_name, total_stops DESC;",
    "Which race and gender combination has the highest search rate?":"SELECT driver_race, driver_gender,COUNT(*) AS total_stops,SUM(search_conducted) AS total_searches FROM police_logs GROUP BY driver_race, driver_gender ORDER By total_searches / total_stops DESC;",
    "What time of day sees the most traffic stops?":"SELECT HOUR(stop_time) AS hour_of_day,COUNT(*) AS total_stops FROM police_logs GROUP BY HOUR(stop_time) ORDER BY total_stops DESC Limit 1 ;",
    "Are stops during the night more likely to lead to arrests?":"SELECT time_of_day,COUNT(*) AS total_stops,SUM(is_arrested) AS total_arrests FROM (SELECT *,CASE WHEN HOUR(stop_time) >= 20 OR HOUR(stop_time) < 6 THEN 'Night'ELSE 'Day'END AS time_of_day FROM police_logs) AS t GROUP BY time_of_day;",
    "Which violations are most associated with searches or arrests?":"SELECT violation,COUNT(*) AS total_stops,SUM(search_conducted) AS total_searches, SUM(is_arrested) AS total_arrests FROM police_logs GROUP BY violation ORDER BY total_searches DESC, total_arrests DESC LIMIT 10;",
    "Which violations are most common among younger drivers (<25)?":"SELECT violation, COUNT(*) AS total_stops FROM police_logs WHERE driver_age < 25 GROUP BY violation ORDER BY total_stops DESC LIMIT 10;",
    "Is there a violation that rarely results in search or arrest?":"SELECT violation FROM police_logs GROUP BY violation ORDER BY (SUM(search_conducted)/COUNT(*) + SUM(is_arrested)/COUNT(*)) ASC LIMIT 1;",
    "Which countries report the highest rate of drug-related stops?":"SELECT country_name FROM police_logs GROUP BY country_name ORDER BY SUM(drugs_related_stop)/COUNT(*) DESC LIMIT 10;",
    "What is the arrest rate by country and violation?":"SELECT country_name, violation, SUM(is_arrested)/COUNT(*) AS arrest_rate FROM police_logs GROUP BY country_name, violation ORDER BY arrest_rate DESC;",
    "Which country has the most stops with search conducted?":"SELECT country_name, COUNT(*) AS total_searches FROM police_logs WHERE search_conducted=1 GROUP BY country_name ORDER BY total_searches DESC LIMIT 1;"
}

selected_query1 = st.selectbox("Select an Advanced Query to Run", list(query_map1.keys()), key="select_query1")

if st.button("Run Query", key="run_query1"):
    result = fetch_data(query_map1[selected_query1])
    if not result.empty:
        st.write(result)
    else:
        st.warning("No result found for the selected query")



#complex queries 

st.header("Complex Insights")

select_query2 = [
    "Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)",
    "Driver Violation Trends Based on Age and Race (Join with Subquery)",
    "Time Period Analysis of Stops (Joining with Date Functions) , Number of Stops by Year,Month, Hour of the Day",
    "Violations with High Search and Arrest Rates (Window Function)",
    "Driver Demographics by Country (Age, Gender, and Race)",
    "Top 5 Violations with Highest Arrest Rates"
]


query_map2 = {
    "Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)":"SELECT country_name,year,total_stops,total_arrests,ROUND(100.0 * total_arrests / total_stops, 2) AS arrest_rate_percent,RANK() OVER (PARTITION BY year ORDER BY total_arrests DESC) AS rank_by_arrests FROM (SELECT country_name,EXTRACT(YEAR FROM stop_date) AS year, COUNT(*) AS total_stops,SUM(is_arrested) AS total_arrests FROM police_logs GROUP BY country_name, EXTRACT(YEAR FROM stop_date)) AS yearly_data ORDER BY year, rank_by_arrests;",
    "Driver Violation Trends Based on Age and Race (Join with Subquery)":"SELECT p.driver_race,a.age_group,COUNT(*) AS total_stops,SUM(p.is_arrested) AS total_arrests FROM police_logs p JOIN (SELECT id,CASE WHEN driver_age<25 THEN 'Under 25' WHEN driver_age BETWEEN 25 AND 40 THEN '25-40' WHEN driver_age BETWEEN 41 AND 60 THEN '41-60' ELSE 'Above 60' END AS age_group FROM police_logs) a ON p.id=a.id GROUP BY p.driver_race,a.age_group ORDER BY p.driver_race,a.age_group;",
    "Time Period Analysis of Stops (Joining with Date Functions) , Number of Stops by Year,Month, Hour of the Day":"SELECT EXTRACT(YEAR FROM stop_date) AS year,EXTRACT(MONTH FROM stop_date) AS month,EXTRACT(HOUR FROM stop_time) AS hour_of_day,COUNT(*) AS total_stops FROM police_logs GROUP BY year,month,hour_of_day ORDER BY year,month,hour_of_day;",
    "Violations with High Search and Arrest Rates (Window Function)":"SELECT violation,COUNT(*) AS total_stops,SUM(search_conducted) AS total_searches,SUM(is_arrested) AS total_arrests,ROUND(100.0*SUM(search_conducted)/COUNT(*),2) AS search_rate,ROUND(100.0*SUM(is_arrested)/COUNT(*),2) AS arrest_rate,RANK() OVER(ORDER BY SUM(is_arrested) DESC) AS rank_by_arrests FROM police_logs GROUP BY violation ORDER BY rank_by_arrests;",
    "Driver Demographics by Country (Age, Gender, and Race)":"SELECT country_name,driver_gender,driver_race,AVG(driver_age) AS avg_age,COUNT(*) AS total_drivers FROM police_logs GROUP BY country_name,driver_gender,driver_race ORDER BY country_name,driver_gender,driver_race;",
    "Top 5 Violations with Highest Arrest Rates":"SELECT violation,COUNT(*) AS total_stops,SUM(is_arrested) AS total_arrests, ROUND(1.0 * SUM(is_arrested) / COUNT(*) * 100, 2) AS arrest_rate_percentage FROM police_logs GROUP BY violation HAVING COUNT(*) > 0 ORDER BY arrest_rate_percentage DESC LIMIT 5;"
}

selected_query2 = st.selectbox("Select a Complex Query to Run", list(query_map2.keys()), key="select_query2")

if st.button("Run Query", key="run_query2"):
    result = fetch_data(query_map2[selected_query2])
    if not result.empty:
        st.write(result)
    else:
        st.warning("No result found for the selected query")


st.markdown("___________")

st.header("Add New Police Log & Predict Outcome and Violation")

#input form for all fields (Excuding outpts)

with st.form("new_log_form"):
    stop_date = st.date_input("Stop Date") , 
    stop_time = st.time_input ("stop Time") ,
    country_name = st.text_input ("Country Name") , 
    driver_gender = st.selectbox("Driver Gender" ,["Male","Female"] ) ,
    driver_age = st.number_input("Driver Age" , min_value =16,max_value= 100, value=27 ) ,
    driver_race = st.text_input ("Driver Race") ,
    search_conducted = st.selectbox("Was a Search Conducted?",["0","1"]), 
    search_type = st.text_input ("Search_Type") ,
    stop_duration = st.selectbox("Stop Duration",data['stop_duration'].dropna().unique()) , 
    drugs_related_stop = st.selectbox("Was it Drug Related?",["0","1"]) , 
    vehicle_number = st.text_input("Vehicle Number") ,
    Timestampp = pd.Timestamp.now() 

    submitted = st.form_submit_button("Predict Stop Outcome & Violation")
    
if submitted:
    # Extract values from tuples if they are tuples
    driver_gender = driver_gender[0] if isinstance(driver_gender, tuple) else driver_gender
    driver_age = driver_age[0] if isinstance(driver_age, tuple) else driver_age
    country_name = country_name[0] if isinstance(country_name, tuple) else country_name
    stop_time = stop_time[0] if isinstance(stop_time, tuple) else stop_time
    stop_date = stop_date[0] if isinstance(stop_date, tuple) else stop_date
    stop_duration = stop_duration[0] if isinstance(stop_duration, tuple) else stop_duration
    vehicle_number = vehicle_number[0] if isinstance(vehicle_number, tuple) else vehicle_number
    search_conducted = search_conducted[0] if isinstance(search_conducted, tuple) else search_conducted
    drugs_related_stop = drugs_related_stop[0] if isinstance(drugs_related_stop, tuple) else drugs_related_stop
    
    #filter data for prediction
    filtered_data = data[
        (data['driver_gender']==driver_gender)&
        (data['driver_age']==driver_age)&
        (data['search_conducted']== search_conducted)&
        (data['stop_duration']== stop_duration)&
        (data['drugs_related_stop'] == drugs_related_stop)
    ]
    

    
    #predict stop_outcome
    if not filtered_data.empty:
        predicted_outcome = filtered_data["stop_outcome"].mode()[0]
        predicted_violation = filtered_data["violation"].mode()[0]
    else:
        predicted_outcome = "Warning"
        predicted_violation = "Speeding"
    
    #Display prediction results
    st.subheader("Prediction Summary")
    st.write(f"Based on the provided details:")
    st.write(f"- **Stop Outcome**: {predicted_outcome}")
    st.write(f"- **Violation Type**: {predicted_violation}")
    
    #Natural language summary
    search_text = "A Search Was conducted" if search_conducted == "1" else "No search was conducted"
    drug_text = "was drug related" if drugs_related_stop == "1"  else "was not drug related"
    
    st.markdown(f"""
        **Prediction Summary**
        
        **Predicted Violation:** {predicted_violation}
        **Predicted Stop Outcome:** {predicted_outcome}
        
        A {driver_age}-year old  - {driver_gender} driver from {country_name} was stopped at {stop_time} on {stop_date}
        {search_text}, and the stop {drug_text},
        Stop duration: **{stop_duration}**,
        Vehicle Number: **{vehicle_number}**,
        """)







          






