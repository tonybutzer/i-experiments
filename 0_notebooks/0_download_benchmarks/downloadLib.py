import subprocess
def subprocess_cmd(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    stupidBytesObject = proc_stdout
    outStr = (stupidBytesObject.decode("utf-8"))
    print(outStr)
    return(outStr)

from satsearch import Search

def get_STAC_items(url, collection, dates, bbox):
    results = Search.search(url=url,
                        collections=[collection], 
                        datetime=dates,
                        bbox=bbox,    
                        sortby=['-properties.datetime'])

    items = results.items()
    print(f'Found {len(items)} Items')
    
    
#     #return intake.open_stac_item_collection(items)
#     return intake_stac.catalog.StacItemCollection(items)
#     #return intake.stac_item_collection(items)
    
    return(items)
