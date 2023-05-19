import numpy as np
import math
import pandas as pd
import struct
import sys

def main(in_file, out_file):
    """
    inputs: in_file - a IMR file formatted following https://docs.novatel.com/Waypoint/Content/Data_Formats/IMR_File.htm. 
    out_file: a path to a csv file to export. 
    """
    with open(in_file, mode="rb") as f:
        header = f.read(512)
        data = f.read()
    
    bls_intel_or_moto = header[9]
    if bls_intel_or_moto == 0:
        header_unpack = struct.unpack('<7sxbdiidddiid32sI32s12s?iii',header[0:158])
    else: 
        header_unpack = struct.unpack('>7sxbdiidddiid32sI32s12s?iii',header[0:158])
    
    b_delta_theta = header_unpack[3]
    b_delta_vel = header_unpack[4]
    data_rate = header_unpack[5]
    gyro_scale = header_unpack[6]
    acc_scale = header_unpack[7]
    time_scale = header_unpack[8]

    if time_scale == 0: 
        time_label = "GPS Week Seconds"
    elif time_scale == 1:
        time_label = "UTC Week Seconds"
    elif time_scale == 2:
        time_label = "GPS Week Seconds"
    
    if b_delta_theta == 0:
        g_sf = gyro_scale
    elif b_delta_theta == 1: 
        g_sf = gyro_scale * data_rate
        
    if b_delta_vel == 0:
        a_sf = acc_scale
    elif b_delta_vel == 1: 
        a_sf = acc_scale * data_rate
        
    
    len_data = math.floor(len(data) / 32)
    time = np.empty(len_data, dtype='float')
    gx = np.empty(len_data, dtype='float')
    gy = np.empty(len_data, dtype='float')
    gz = np.empty(len_data, dtype='float')
    ax = np.empty(len_data, dtype='float')
    ay = np.empty(len_data, dtype='float')
    az = np.empty(len_data, dtype='float')
    
    for i in range(0,len_data):
        row_start = i * 32
        row_end = row_start + 32
        if bls_intel_or_moto == 0:
            data_row = struct.unpack('<diiiiii',data[row_start:row_end])
        else: 
            data_row = struct.unpack('>diiiiii',data[row_start:row_end])
        time[i] = data_row[0]
        gx[i] = data_row[1] * g_sf
        gy[i] = data_row[2] * g_sf
        gz[i] = data_row[3] * g_sf
        
        ax[i] = data_row[4] * a_sf
        ay[i] = data_row[5] * a_sf
        az[i] = data_row[6] * a_sf
        
    out_data = pd.DataFrame({time_label : time, "gx":gx, "gy":gy, "gz":gz, "ax":ax, "ay":ay, "az":az})
    out_data.to_csv(out_file)


if __name__ == '__main__':
    """imu_export.py : exports a .imr file to csv. Example: imu_export.py input_file.imr output_file.csv"""
    arg1, arg2 = sys.argv[1:3]
    main(arg1, arg2)