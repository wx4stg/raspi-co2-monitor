from time import sleep
import board
import adafruit_scd4x
import polars as pl
from os import path, remove
from datetime import datetime as dt, timezone
import numpy as np

if __name__ == '__main__':
    i2c = board.I2C()
    scd4x = adafruit_scd4x.SCD4X(i2c)

    scd4x.start_periodic_measurement()
    if path.exists('co2data.parquet'):
        my_df = pl.read_parquet('co2data.parquet')
    else:
        my_df = pl.DataFrame(
            schema=[
                ('timestamp', pl.Datetime('ms', 'UTC')),
                ('co2', pl.UInt16),
                ('temp', pl.Float32),
                ('rh', pl.Float32)
            ]
        )
    while True:
        if scd4x.data_ready:
            this_dt = dt.now(timezone.utc)
            this_co2 = scd4x.CO2
            this_t = scd4x.temperature
            this_rh = scd4x.relative_humidity
            new_data = pl.DataFrame({
                                     'timestamp' : [this_dt],
                                     'co2' : [scd4x.CO2],
                                     'temp' : [scd4x.temperature],
                                     'rh' : [scd4x.relative_humidity]})
            new_data = new_data.cast({'timestamp' : pl.Datetime('ms', 'UTC'), 'co2': pl.UInt16, 'temp' : pl.Float32, 'rh' : pl.Float32})
            my_df = pl.concat([my_df, new_data])
            if path.exists('co2data.parquet'):
                remove('co2data.parquet')
            my_df.write_parquet('co2data.parquet')
            sleep(1)
        else:
            sleep(0.1)
