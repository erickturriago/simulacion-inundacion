# -*- coding: utf-8 -*-
"""
Simulación de inundación a partir de DEM y shapefile de río
"""

import geopandas as gpd
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio import plot
import imageio
from rasterio import features

def hillshade(array, azimuth, angle_altitude):
    """
    Función para generar hillshade a partir de un array de elevación.
    """
    x, y = np.gradient(array)
    slope = np.pi/2. - np.arctan(np.sqrt(x*x + y*y))
    aspect = np.arctan2(-x, y)
    azimuthrad = azimuth * np.pi / 180.
    altituderad = angle_altitude * np.pi / 180.
    shaded = np.sin(altituderad) * np.sin(slope) + np.cos(altituderad) * np.cos(slope) * np.cos(azimuthrad - aspect)
    return 255*(shaded + 1)/2

# dem_path="DEM_Bogota/Bogota1.tif"
# river_path="DEM_Bogota/Rio.shp"
dem_path="DEM_Rio_Caqueta/Rio_Caqueta.tif"
river_path="DEM_Rio_Caqueta/Rio.shp"

# Leer el DEM y el río
with rasterio.open(dem_path) as src:
    dem_array = src.read(1)
    dem_meta = src.meta

try:
    river_gdf = gpd.read_file(river_path)
except:
    print("Error al leer el archivo shapefile. Verifique el formato y el sistema de coordenadas.")
    exit()


# Calcular hillshade
hillshade_array = hillshade(dem_array, 315, 45)

# Calcular elevación media del río
river_elevations = []
for geom in river_gdf.geometry:
    mask = features.geometry_mask([geom], transform=dem_meta['transform'], invert=True, out_shape=dem_array.shape)
    river_elevations.extend(dem_array[mask])
mean_river_elevation = np.mean(river_elevations)

# Generar frames para la animación
intervals = np.arange(0,30,2) #Altura de inundación caquetá
# intervals = np.arange(10,700,30) #Altura de inundacion cerca Bogotá
frames = []
for interval in intervals:
    flood_elevation = mean_river_elevation + interval
    flood_mask = dem_array <= flood_elevation

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(hillshade_array, cmap='gray', extent=rasterio.plot.plotting_extent(src))
    ax.imshow(flood_mask, cmap='Blues', alpha=0.5, extent=rasterio.plot.plotting_extent(src))
    river_gdf.plot(ax=ax, color='blue', edgecolor='blue')
    ax.set_title(f"Inundación a {interval} m")
    plt.axis('off')

    fig.canvas.draw()
    image = np.array(fig.canvas.renderer._renderer)
    plt.close(fig)
    frames.append(image)

# Guardar GIF
gif_path = "inundacion.gif"
imageio.mimsave(gif_path, frames, duration=0.5, loop=0)
print(f"Animación guardada en: {gif_path}")