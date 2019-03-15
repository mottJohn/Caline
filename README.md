# CALINE
## Basic of Guassian Plume Model
concentration (g/m^3) 

= (emission rate)/(wind speed * area of disk) * guassian distribution = g/s / (m/s * m^2) * gaussian distribution

 =  g/s * (s/m * 1/m^2) = g/m^3

## Logic
1. Given output emission factors for each pollutants from EMFAC in unit Tonnes/hour
2. Convert it into grams/hour/VKT. Because hour = 1, the emission factor is grams/VKT (I don't know why we used this, and I know now). 
    * Emission per activity * traffic flow * road length --> grams/VKT * n/hr * l = grams/hr => grams/s
3. Use bdn file which is much detail than the summary file to get the VKT and grams/hr for each polluants of concern. Loop through all "Veh", and "Period", filter "MdlYr" = ALLMYr, "Tech" = TOT
4. Calculate the weighted sum of all vehicles for each road

#why type 3 road does not need to sum run exh and start exh 
#it seems that Caline4 does not have start exh
#the unit of start exh is grams/start, but unfortunately, [Caline4 does not have inputs for start](http://shodhganga.inflibnet.ac.in/bitstream/10603/190635/14/14_appendix.pdf.pdf).

## Glossary
* Road Type (column name from Emfac roadBasicInfo table)
    * 1: Type 1 Expressway (100kph)
    * 2: Type 2 Local Road without cold start (50kph)
    * 3: Type 3 Local Road with cold start (50 kph)