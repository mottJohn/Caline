import pandas as pd 
import numpy as np

################
# user inputs
################
year = '2024'
factor_NO = 1000
factor_RSP = 1

path_emfac_output = r'C:\Users\CHA82870\OneDrive - Mott MacDonald\Documents\Caline\2024_Type3_hr_RSP.bdn.csv'
path_hourlyData = r'C:\Users\CHA82870\OneDrive - Mott MacDonald\Documents\Caline\hourlyVehicleFlow_transformed.csv'
path_roadCoordinates = r'C:\Users\CHA82870\OneDrive - Mott MacDonald\Documents\Caline\roadCoordinates_template.xlsx'

################
#Code do not modify unless you know what you are doing
################

data = pd.read_csv(path_emfac_output, header = 8) #read csv with header at position 8
flow_data = pd.read_csv(path_hourlyData)

data = data[(data['Period'] != 'Day') & (data['Veh'] != 'ALL') & (data['MdlYr'] == 'AllMYr') & (data['Tech'] == 'TOT')] #filter model year and tech group
data['Period'] = data['Period'].astype(int) -1
data['NOx_RUNEX'] = data['NOx_RUNEX'].div(data['VKT'], axis = 0)
data['PM10_RUNEX'] = data['PM10_RUNEX'].div(data['VKT'], axis = 0)

grouped_data = data.groupby(['Period', 'Veh']).sum() #group by period and vehicle type to get the EF in tonnes per VKT

cols = ['PC', 'Taxi', 'LGV3', 'LGV4', 'LGV6', 'HGV7', 'HGV8', 'PLB','PV4', 'PV5', 'NFB6', 'NFB7', 'NFB8', 'FBSD', 'FBDD', 'MC']
flow_data[cols] = flow_data[cols].div(flow_data['VEH'], axis = 0) #get the percent

NO_ratio = pd.DataFrame({'Veh':cols, 'Ratios':[0.939,0.973,0.946,0.946,0.720,0.673,0.688,0.824,0.801,0.746,0.720,0.713,0.675,0.710,0.710,0.950]})

compositEF_NO = []
compositEF_RSP = []
for index, row in flow_data.iterrows():
    data_filtered = data[data['Period'] == row['Hour']]
    row = row[cols]
    #print(row)
    #print(data_filtered)
    row = row.rename('Percent of Total Flow').to_frame()
    row.index = row.index.str.upper() #convert to upper case for merge (very tricky)
    NO_ratio['Veh'] = NO_ratio['Veh'].str.upper() #convert to upper case for merge (very tricky)
    merged = pd.merge(row , data_filtered, right_on='Veh', left_index=True)
    merged = pd.merge(merged, NO_ratio, on='Veh')
    #merged.to_csv("check_merged.csv")
    #print(merged)
    compositeEF_1 = (merged['NOx_RUNEX']*1000000*merged['Ratios']*merged['Percent of Total Flow']).sum()
    compositeEF_2 = (merged['PM10_RUNEX']*1000000*merged['Percent of Total Flow']).sum()
    compositEF_NO.append(compositeEF_1)
    compositEF_RSP.append(compositeEF_2)


flow_data['composit emission factor NO'] = compositEF_NO
flow_data['composit emission factor RSP'] = compositEF_RSP

#print(flow_data)
flow_data['colFromIndex'] = flow_data.index
flow_data = flow_data.sort_values(by = ['Hour','colFromIndex'])
flow_data.to_csv("compositEmissionFactor_NORSP_{}.csv".format(year))

###########
#codes for generating input files
#each road ID will be cut to several sections
###########

xls = pd.ExcelFile(path_roadCoordinates)
roadCoordinate = xls.parse("Sheet1")

flow_data = pd.merge(flow_data, roadCoordinate, how = 'left', on=['Road ID'])
flow_data['composit emission factor NO'] = flow_data['composit emission factor NO']*(1.60934)*factor_NO #*(1.60934) conver to miles
flow_data['composit emission factor RSP'] = flow_data['composit emission factor RSP']*(1.60934)*factor_RSP

with pd.ExcelWriter('traffic_NO_RSP_inp_{}.xlsx'.format(year)) as writer:
    for hr in flow_data['Hour'].unique():
        flow_data_hr = flow_data[flow_data['Hour'] == hr]

        traffic_col = []
        NO_col = []
        RSP_col = []
        for i in range(0, len(flow_data_hr), 4):
            temp = pd.DataFrame(columns = ['Traffic', 'NO_2', 'FSP'])
            slc = flow_data_hr.iloc[i:i+4]
            traffic = slc['VEH'].astype(str).str.cat(sep = ' ')
            NO = slc['composit emission factor NO'].astype(str).str.cat(sep = ' ') 
            RSP = slc['composit emission factor RSP'].astype(str).str.cat(sep = ' ')
            traffic_col.append(traffic)
            NO_col.append(NO)
            RSP_col.append(RSP)

        input = pd.DataFrame({'Traffic':traffic_col, 'NO':NO_col, 'RSP':RSP_col})
        input.to_excel(writer, sheet_name='Hr {}'.format(hr), index = False)