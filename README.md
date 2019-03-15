# CALINE
# Basic of Guassian Plume Model
concentration (g/m^3) 

= (emission rate)/(wind speed * area of disk) * guassian distribution = g/s / (m/s * m^2) * gaussian distribution

 =  g/s * (s/m * 1/m^2) = g/m^3

## Logic
1. Given output emission factors for each pollutants from EMFAC in unit Tonnes/hour
2. Convert it into grams/hour/VKT. Because hour = 1, the emission factor is grams/VKT (I don't know why we used this, and I know now). 
    * Emission per activity * traffic flow * road length --> grams/VKT * n/hr * l = grams/hr = grams/s