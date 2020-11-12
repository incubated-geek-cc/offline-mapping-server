import math
from math import pow
import os
import requests

path=os.chdir("../") # change work directory
print(path)

# transforms the x and y into latitude and longitude respectively based on zoom level
def num2deg(xtile, ytile, zoom):
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)

# transforms the lat_deg and lon_deg into x and y of a tile image respectively based on zoom level 
def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
  return (xtile, ytile)

# Use the following JavaScript Code to stream xy object
# E.g. At sites like: http://maps.stamen.com/toner/#11/1.3327/103.8496
# var imgs = document.getElementsByTagName("img");
# var coordinates = [];
# for(var i in imgs) {
#     if(typeof imgs[i].classList !== "undefined") {
#         if(imgs[i].classList.contains("leaflet-tile-loaded")) {
#             var srcArr=imgs[i].src.split("/");
#             var yIndex=srcArr[srcArr.length-1];
#             var xIndex=srcArr[srcArr.length-2];
#             var zIndex=srcArr[srcArr.length-3];

#             var xy={
#                 "x": parseInt(xIndex),
#                 "y": parseInt(yIndex)
#             };

#             coordinates.push(xy);
#         }
#     }
# }
# console.log(JSON.stringify(coordinates));

xy=[
  {"x":1614,"y":1016},{"x":1615,"y":1016},{"x":1614,"y":1017},{"x":1615,"y":1017},{"x":1614,"y":1015},
  {"x":1615,"y":1015},{"x":1613,"y":1016},{"x":1616,"y":1016},{"x":1613,"y":1017},{"x":1616,"y":1017},
  {"x":1614,"y":1018},{"x":1615,"y":1018},{"x":1613,"y":1015},{"x":1616,"y":1015},{"x":1613,"y":1018},
  {"x":1616,"y":1018},{"x":1612,"y":1016},{"x":1617,"y":1016},{"x":1612,"y":1017},{"x":1617,"y":1017},
  {"x":1612,"y":1015},{"x":1617,"y":1015},{"x":1612,"y":1018},{"x":1617,"y":1018},{"x":1614,"y":1014},
  {"x":1615,"y":1014},{"x":1613,"y":1014},{"x":1616,"y":1014},{"x":1612,"y":1014},{"x":1617,"y":1014}
]

minZoomLevel=11 #11 # IMPORTANT! Ensure that your minZoomLevel is the same as the one you decided intially
maxZoomLevel=14 # The upper limit of zoom level set on the basemap

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

    lat=num2deg(x, y, minZoomLevel)[0]
    lng=num2deg(x, y, minZoomLevel)[1]
    feature={
      "type":"Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [
          lng,
          lat
        ]
       },
        "properties": {
          "zoom": minZoomLevel
        } 
    }

    geojsonObj["features"].append(feature)


# proceed to save geojson to file
geojson=str(geojsonObj).replace("'","\"")

geojson_file = open("output.geojson", "w")
geojson_file.write(geojson)
geojson_file.close()

print("GeoJSON has been saved to file: output.geojson")

# print out min max of x and y
print("Value of minXVal is: " + str(minXVal))
print("Value of maxXVal is: " + str(maxXVal))

print("Value of minYVal is: " + str(minYVal))
print("Value of maxYVal is: " + str(maxYVal))

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

print("Dimensions of map are: " + str(xTileDimension) + " x " + str(yTileDimension) + " tiles for zoom level " + str(minZoomLevel))

def initDirectoryStructure(n): # where n refers to the zoom level
    minX=(minXVal/xTileDimension)*( xTileDimension/pow(2,minZoomLevel)*pow(2,n))
    maxX=(maxXVal/xTileDimension)*( xTileDimension/pow(2,minZoomLevel)*pow(2,n)) 
    
    minY=(minYVal/yTileDimension)*( yTileDimension/pow(2,minZoomLevel)*pow(2,n))
    maxY=(maxYVal/yTileDimension)*( yTileDimension/pow(2,minZoomLevel)*pow(2,n))
    
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
basemapUrlPrefix="http://tile.stamen.com/toner-hybrid/"
# specify basemap suffix here
basemapUrlSuffix=".png"

def streamTileImages(n): # where n refers to the zoom level
    minX=(minXVal/xTileDimension)*( xTileDimension/pow(2,minZoomLevel)*pow(2,n))
    maxX=(maxXVal/xTileDimension)*( xTileDimension/pow(2,minZoomLevel)*pow(2,n)) 
    
    minY=(minYVal/yTileDimension)*( yTileDimension/pow(2,minZoomLevel)*pow(2,n))
    maxY=(maxYVal/yTileDimension)*( yTileDimension/pow(2,minZoomLevel)*pow(2,n))
    
    minX=int(minX)
    maxX=int(maxX)
    minY=int(minY)
    maxY=int(maxY)
    
    for x in range(minX,maxX+1,1):
      for y in range(minY,maxY+1,1):
            basemapTileUrl=basemapUrlPrefix+str(n) + "/" + str(x) + "/" + str(y) + basemapUrlSuffix

            try:
              # send a HTTP request to retrieve the tile image file
              r = requests.get(basemapTileUrl)
              # proceed to save it as a local image file in the folders created in step 3
              save_as_filename=directoryPrefix+str(n) + "/" + str(x) + "/" + str(y) + ".png"
              with open(save_as_filename,"wb") as local_tile_image:
                  local_tile_image.write(r.content)
            except:
              print(basemapTileUrl)

for z in range(minZoomLevel,maxZoomLevel+1,1):
    streamTileImages(z)
    
print("All map tile images for zoom levels " + str(minZoomLevel) + " to " + str(maxZoomLevel) + " have been saved to local directories.")