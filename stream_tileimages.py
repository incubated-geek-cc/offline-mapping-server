import math
from math import pow
import os
import requests

def num2deg(xtile, ytile, zoom):
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)

def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
  return (xtile, ytile)


minZoomLevel=11 # IMPORTANT! Ensure that your minZoomLevel is the same as the one you decided intially
maxZoomLevel=15 # The upper limit of zoom level set on the basemap

directoryPrefix="toner/" # specify folder to save to e.g. "toner"

geojsonObj={
  "type": "FeatureCollection",
  "features": []
}

minXVal=None
maxXVal=None

minYVal=None
maxYVal=None

for item in xy:
    x=item["x"]
    y=item["y"]
    if (minXVal is None) or (x <= minXVal):
        minXVal=x
        
    if (minYVal is None) or (y <= minYVal):
        minYVal=y
    
    if (maxXVal is None) or (x >= maxXVal):
        maxXVal=x
        
    if (maxYVal is None) or (y >= maxYVal):
        maxYVal=y
        
    feature={
      "type":"Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [
          num2deg(x, y, zoom)[1],
          num2deg(x, y, zoom)[0]
        ]
       },
        "properties": {
          "zoom": minZoomLevel
        } 
    }
    geojsonObj["features"].append(feature)

geojson=str(geojsonObj).replace("'","\"")

geojson_file = open("output.geojson", "w")
geojson_file.write(geojson)
geojson_file.close()

print("GeoJSON has been saved to file: output.geojson")

# get tile dimensions for minZoomLevel specified e.g. zoom level 11
noOfx={}
noOfy={}

for item in xy:
    x=item["x"]
    y=item["y"]
    noOfx[x]=0
    noOfy[y]=0

xTileDimension=len(list(noOfx.keys()))
yTileDimension=len(list(noOfy.keys()))

# Upper limit of x-coordinate has to be substracted by 1 to not double count the tile coordinates in subsequent calculations:
maxXVal=maxXVal-1

def initDirectoryStructure(n): # where n refers to the zoom level
    minX=(minXVal/xTileDimension)*(xTileDimension*pow(2,n-minZoomLevel))
    maxX=(maxXVal/xTileDimension)*(xTileDimension*pow(2,n-minZoomLevel))
    
    minY=(minYVal/yTileDimension)*(yTileDimension*pow(2,n-minZoomLevel))
    maxY=(maxYVal/yTileDimension)*(yTileDimension*pow(2,n-minZoomLevel))
    
    minX=int(minX)
    maxX=int(maxX)
    minY=int(minY)
    maxY=int(maxY)
    
    for x in range(minX,maxX+1,1):
      for y in range(minY,maxY+1,1):
            directory=directoryPrefix+str(n) + "/" + str(x)
            if not os.path.exists(directory):
                os.makedirs(directory)

# Execute function to create folder structures for zoom levels minZoomLevel to maxZoomLevel (inclusive)
for z in range(minZoomLevel,maxZoomLevel+1,1):
    initDirectoryStructure(z)
    
print("Folder structure for zoom levels " + str(minZoomLevel) + " to " + str(maxZoomLevel) + " has been created.")


# specify basemap prefix here
basemapUrlPrefix="http://tile.stamen.com/toner/"
# specify basemap suffix here
basemapUrlSuffix=".png"

def streamTileImages(n): # where n refers to the zoom level
    minX=(minXVal/xTileDimension)*(xTileDimension*pow(2,n-minZoomLevel))
    maxX=(maxXVal/xTileDimension)*(xTileDimension*pow(2,n-minZoomLevel))
    
    minY=(minYVal/yTileDimension)*(yTileDimension*pow(2,n-minZoomLevel))
    maxY=(maxYVal/yTileDimension)*(yTileDimension*pow(2,n-minZoomLevel))
    
    minX=int(minX)
    maxX=int(maxX)
    minY=int(minY)
    maxY=int(maxY)
    
    for x in range(minX,maxX+1,1):
      for y in range(minY,maxY+1,1):
            # send a HTTP request to retrieve the tile image file
            basemapTileUrl=basemapUrlPrefix+str(n) + "/" + str(x) + "/" + str(y) + basemapUrlSuffix
            r = requests.get(basemapTileUrl)
            # proceed to save it as a local image file in the folders created in step 3
            save_as_filename=directoryPrefix+str(n) + "/" + str(x) + "/" + str(y) + ".png"
            with open(save_as_filename,"wb") as local_tile_image:
                local_tile_image.write(r.content) 

for z in range(minZoomLevel,maxZoomLevel+1,1):
    streamTileImages(z)
    
print("All map tile images for zoom levels " + str(minZoomLevel) + " to " + str(maxZoomLevel) + " have been saved to local directories.")