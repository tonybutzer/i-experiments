import geopandas as gpd
from pystac_client import Client
from shapely.geometry import mapping
import pandas as pd


# functions

import hvplot.pandas


# User configurable settings

# plot size settings
frame_width = 600
frame_height = 600

# line width of polygons
line_width = 3

# plot polygons as lines on a slippy map with background tiles.
def plot_polygons(data, *args, **kwargs):
    return data.hvplot.paths(*args, geo=True, tiles='OSM', xaxis=None, yaxis=None,
                             frame_width=frame_width, frame_height=frame_height,
                             line_width=line_width, **kwargs)

class LTWG:
    def __init__(self, platform, aoi, date_range, cloud_cover_threshold):
        print("Instantiate class LTWG")
        print("CLOUD Threshold is", cloud_cover_threshold, "percent.")
        self.cloud_cover_threshold = cloud_cover_threshold
        self.aoi = aoi
        self.platform = platform
        self.date_range = date_range
        self.url = 'https://earth-search.aws.element84.com/v0'

        filename = self.aoi
        aoi_gpd = gpd.read_file(filename)

        geom = mapping(aoi_gpd.to_dict()['geometry'][0])
        # Search parameters
        self.params = {
            #"collections": ["landsat-c2l2-sr"],
            "collections": ["sentinel-s2-l2a-cogs"],
            "intersects": geom,
            "datetime": date_range,
            "limit": 100,
            "query": [f'eo:cloud_cover<={cloud_cover_threshold}']
        }


    def __repr__(self):
        return(f"CLOUD Threshold is {self.cloud_cover_threshold} percent. \n platform={self.platform}."+
               f'date_range={self.date_range}')


    def show_map(self):
        # read in AOI as a GeoDataFrame

        filename = self.aoi
        aoi_gpd = gpd.read_file(filename)
        return(plot_polygons(aoi_gpd))
	
    
    def item_count(self):

        cat = Client.open(self.url)
        self.search = cat.search(**self.params)

        matched = self.search.matched()
        if matched is not None:
            self.items_dict = [i.to_dict() for i in self.search.items()]
            return(matched)
        else:
            return(0)

    def list_scenes(self):
        self.items = []
        for item in self.search.items():
            self.items.append(item)
            print(item.id)
            
    def df_meta_s(self,index):
        #print(self.items[0].properties)
        mdf = pd.DataFrame(self.items[index].properties)
        # datetime 	platform 	constellation 	instruments 	gsd 	view:off_nadir 	proj:epsg 	sentinel:utm_zone 	sentinel:latitude_band 	sentinel:grid_square 	sentinel:sequence 	sentinel:product_id 	sentinel:data_coverage 	eo:cloud_cover 	sentinel:valid_cloud_cover 	created 	updated--
        pruned_df = mdf[["datetime", "platform", 'instruments', 'gsd', 'sentinel:data_coverage', 'eo:cloud_cover']]
        pruned_df.set_index('datetime', inplace=True)

        return(pruned_df)
    
    def df_asset_s(self,index):
        
        assets = pd.DataFrame.from_dict(self.items_dict[index]['assets'], orient='index')

        for f in ['href', 'alternate', 'file:checksum', 'proj:transform', 'rel']:
            if f in assets:
                del assets[f]
        #type 	title 	roles 	gsd 	eo:bands 	proj:shape

        return(assets)
