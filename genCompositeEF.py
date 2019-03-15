import pandas as pd 

data = pd.read_csv("2024_Type3_hr_FSP.bdn.csv", header = 8) #read csv with header at position 8

data = data[(data['MdlYr'] == 'AllMYr') & (data['Tech'] == 'TOT')] #filter model year and tech group
grouped_data = data.groupby(['Period', 'Veh']).sum() #group by period and vehicle type to get the EF in tonnes per hr
print(grouped_data)