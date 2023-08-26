import numpy as np
import math
import pandas as pd
import struct
import sys
import os
import ctypes

"""
This program will parse a CSV file to a IMR, to enable QC or error investigation. 

csv_to_imr.py : Converts a csv file to .imr. Example: csv_to_imr.py input_file.imr input_file.csv output_file.imr

Sean G. Polun
2023, University of Missouri
"""
def main(imr_ref_file, csv_file, out_imr_file):
    """
    csv_to_imr.py: Program to convert CSV table to IMR. 
    inputs: in_file - a IMR file formatted following https://docs.novatel.com/Waypoint/Content/Data_Formats/IMR_File.htm. 
    csv_file: a path to a csv file to convert. 
    out_imr_file: path for a new imr (binary) file
    """
    with open(imr_ref_file, mode="rb") as f:
        header = f.read(512)
        # data = f.read()
    
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
        
    imu_data = pd.read_csv(csv_file)
    out_bytes = bytearray(header)
    for i, row in imu_data.iterrows():
        time = float(row[time_label])
        gx_f = row['gx']
        gy_f = row['gy']
        gz_f = row['gz']
        ax_f = row['ax']
        ay_f = row['ay']
        az_f = row['az']
        
        gx_i = round(gx_f / g_sf)
        gy_i = round(gy_f / g_sf)
        gz_i = round(gz_f / g_sf)
        
        ax_i = round(ax_f / a_sf)
        ay_i = round(ay_f / a_sf)
        az_i = round(az_f / a_sf)
        
        if bls_intel_or_moto == 0:
            data_row = struct.pack('<diiiiii',time, gx_i, gy_i, gz_i, ax_i, ay_i, az_i)
        else: 
            data_row = struct.pack('>diiiiii',time, gx_i, gy_i, gz_i, ax_i, ay_i, az_i)
        out_bytes.extend(data_row)
    
    with open(out_imr_file, "wb") as out:
        out.write(out_bytes)
        


if __name__ == '__main__':
    """
    imu_export.py : exports a .imr file to csv. Example: imu_export.py input_file.imr output_file.csv
    Also dumps the header as a (mangled) text file, output_file.txt"""
    arg1, arg2, arg3 = sys.argv[1:4]
    main(arg1, arg2, arg3)