# drone_utils
Random utilities for drones

Currently only scripts to enable added troubleshooting / modification of novatel .imr files. 
## imu_export.py
`imu_export.py in_imr.imr out_csv.csv`

Script that takes a [Novatel IMR binary formatted file](https://docs.novatel.com/Waypoint/Content/Data_Formats/IMR_File.htm) and exports the header and IMU fields. 

## csv_to_imr.py
`csv_to_imr.py orig_imr.imr convert_csv.csv convert_csv.imr`

Script that converts a csv file (following the formatting of imu_export.py) back to the format following the original IMR file. 
