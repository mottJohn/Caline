import pandas as pd 
import numpy as np

factor_NO2 = 1000
factor_FSP = 1

data = pd.read_csv("2024_Type3_hr_FSP.bdn.csv", header = 8) #read csv with header at position 8
flow_data = pd.read_csv("hourlyVehicleFlow_transformed.csv")

data = data[(data['Period'] != 'Day') & (data['Veh'] != 'ALL') & (data['MdlYr'] == 'AllMYr') & (data['Tech'] == 'TOT')] #filter model year and tech group
data['Period'] = data['Period'].astype(int) -1
data['NOx_RUNEX'] = data['NOx_RUNEX'].div(data['VKT'], axis = 0)
data['PM2.5_RUNEX'] = data['PM2.5_RUNEX'].div(data['VKT'], axis = 0)

#print(data)
grouped_data = data.groupby(['Period', 'Veh']).sum() #group by period and vehicle type to get the EF in tonnes per hr

cols = ['PC', 'Taxi', 'LGV3', 'LGV4', 'LGV6', 'HGV7', 'HGV8', 'PLB','PV4', 'PV5', 'NFB6', 'NFB7', 'NFB8', 'FBSD', 'FBDD', 'MC']
flow_data[cols] = flow_data[cols].div(flow_data['VEH'], axis = 0) #get the percent

NO_2_ratio = pd.DataFrame({'Veh':cols, 'Ratios':[0.057,0.026,0.082,0.080,0.280,0.303,0.117,0.151,0.187,0.252,0.280,0.272,0.092,0.102,0.062,0.050]})
#print(flow_data)

compositEF_NO2 = []
compositEF_FSP = []
for index, row in flow_data.iterrows():
    data_filtered = data[data['Period'] == row['Hour']]
    row = row[cols]
    #print(row)
    #print(data_filtered)
    merged = pd.merge(row.rename('EF (Tonnes per VKT)').to_frame(), data_filtered, how = 'left', right_on='Veh', left_index=True)
    merged = pd.merge(merged, NO_2_ratio, on='Veh')
    #print(merged)
    compositeEF_1 = (merged['NOx_RUNEX']*merged['Ratios']*merged['EF (Tonnes per VKT)']).sum()*1000000
    compositeEF_2 = (merged['PM2.5_RUNEX']*merged['EF (Tonnes per VKT)']).sum()*1000000
    compositEF_NO2.append(compositeEF_1)
    compositEF_FSP.append(compositeEF_2)

flow_data['composit emission factor NO2'] = compositEF_NO2
flow_data['composit emission factor FSP'] = compositEF_FSP

#print(flow_data)
flow_data['colFromIndex'] = flow_data.index
flow_data = flow_data.sort_values(by = ['Hour','colFromIndex'])
flow_data.to_csv("compositEmissionFactor_NO2FSP.csv")

###########
#codes for generating input files
#each road ID will be cut to several sections
###########

xls = pd.ExcelFile("roadCoordinates_template.xlsx")
roadCoordinate = xls.parse("Sheet1")

flow_data = pd.merge(flow_data, roadCoordinate, how = 'left', on=['Road ID'])
flow_data['composit emission factor NO2'] = flow_data['composit emission factor NO2']*(1.60934)*factor_NO2 #*(1.60934) conver to miles
flow_data['composit emission factor FSP'] = flow_data['composit emission factor FSP']*(1.60934)*factor_FSP

with pd.ExcelWriter('traffic_NO2_FSP_inp.xlsx') as writer:
    for hr in flow_data['Hour'].unique():
        flow_data_hr = flow_data[flow_data['Hour'] == hr]

        traffic_col = []
        NO_2_col = []
        FSP_col = []
        for i in range(0, len(flow_data_hr), 4):
            temp = pd.DataFrame(columns = ['Traffic', 'NO_2', 'FSP'])
            slc = flow_data_hr.iloc[i:i+4]
            traffic = slc['VEH'].astype(str).str.cat(sep = ' ')
            NO_2 = slc['composit emission factor NO2'].astype(str).str.cat(sep = ' ') 
            FSP = slc['composit emission factor FSP'].astype(str).str.cat(sep = ' ')
            traffic_col.append(traffic)
            NO_2_col.append(NO_2)
            FSP_col.append(FSP)

        input = pd.DataFrame({'Traffic':traffic_col, 'NO_2':NO_2_col, 'FSP':FSP_col})
        input.to_excel(writer, sheet_name='Hr {}'.format(hr), index = False)