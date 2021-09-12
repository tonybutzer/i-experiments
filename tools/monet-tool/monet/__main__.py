import os
import datetime, time, wget
import boto3, geojson, json
from satsearch import Search
from monet.painter import argParser, download_box, print_aws_cp_command, data_used
from monet.vincentae import gen_bbox


def main():
  try:
    # Set up s3 client
    s3 = boto3.resource("s3")
    p = argParser()
    satsearch_url = p.url
    # Check arguments
    if p.radius > 10000:  #TODO use a python assert statement
      print("Radius is too large for chipping")
      raise SystemExit()
    # Check if output directory exists
    if not(os.path.isdir(os.path.join(p.output_dir))):
      try:
        os.mkdir(os.path.join(p.output_dir))
      except Exception as e:
        print("Unable to write to [%s]" % (p.output_dir))
        print(e)
        raise SystemExit()
    # Check to see if output directory is writable
    if not os.access(p.output_dir,os.W_OK):
      print("Unable to write to %s" % (p.output_dir))
      raise SystemExit()
    # Get Bounding box from input Lat/Lon using Vincenty
    if p.radius <= 10:
      box           = [p.longitude[0]-.000001, p.latitude[0]-.000001, p.longitude[0]+.000001, p.latitude[0]+.000001]
      print("Radius is too small to chip, using the entire scene")
    else:
      try:
        box         = gen_bbox(p.latitude[0],p.longitude[0],p.radius)
      except Exception as e:
        print("Unable to get bounding box for latitude [%s degrees] longitude [%s degrees]"\
              % (str(p.latitude),str(p.longitude)))
        print("and radius of [%s meters]" % (str(p.radius)))
        print(e)
        raise SystemExit()
    # Get start/end dates formatted correctly for satsearch
    start_date     = datetime.datetime.strptime(p.start_date,"%Y-%m-%d")
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    stop_date      = datetime.datetime.strptime(p.end_date,"%Y-%m-%d")
    stop_date_str  = stop_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    date_query_str = "%s/%s" % (start_date_str,stop_date_str)
    # Get an API Key
    if p.apiKey is not None:
      headers      = {"x-api-key": p.apiKey}
    elif os.environ.get("STAC_API_KEY") is not None:
      headers      = {"x-api-key": os.environ.get("STAC_API_KEY")}
    else:
      headers = None
    # Start timer for query
    query_time     = time.time()
    query = {"eo:cloud_cover": {"lte": p.cloud_cover}}
    if p.collection.find('sentinel') >= 0:
      query["sentinel:data_coverage"] = {"gte": p.data_coverage}
    search = Search(url=satsearch_url,bbox=box,datetime=date_query_str,
                    query=query,collections=[p.collection])
    # Get items in collection
    items  = search.items(headers=headers)
    query_time   = time.time() - query_time
    num_products = search.found(headers=headers)
    features     = []
    if num_products > 0:
      print(items.calendar()) #TODO slows down code
    # Print out the findings and query parameters
    print("Found %d products between %s and %s with less than %d percent clouds in %0.1f seconds." \
      % (num_products, p.start_date, p.end_date, p.cloud_cover, query_time))
    # Start list of aws commands, will print to stdout for tiles of interest
    aws_commands = []
    if num_products > 0:
      files = []
      thumbnails = []
      local_files = []
      # Only grab Visual spectrum....there are others (TODO might want for future improvements)
      try:
        # try to get imagery
        files.extend([item.assets["visual"]["href"] for item in items])
        # try to get thumbnails
        thumbnails.extend([item.assets["thumbnail"]["href"] for item in items])
      except:
        # Within non sentinel/landsat try getting href from data key
        try:
          files.extend([item.assets["data"]["href"] for item in items])
        except:
          print("Unknown file structure, please consult monet product developers for additional functionality")
          raise SystemExit()

      if len(files) > 0:
        for Findex,f in enumerate(files):
          try:
            # Get aws commands as well as local file names
            s,l = print_aws_cp_command(f)
            aws_commands.append(s)
            local_files.append(l)
            item = items[Findex]
            feature = geojson.Feature(geometry=geojson.loads(json.dumps(item.geometry)))
            feature["properties"] = item.properties
            feature["properties"]["fqp"] = os.path.abspath(l)
            features.append(feature)
            if Findex < 10 or (Findex > 10 and p.all_flag):
              # Simply print aws command to stdout
              if p.verbose:
                print(f)
          except:
            print("Unable to process file [%s]" % (files[Findex]))
    # Grab thumbnails if desired
    if p.thumbnails and len(thumbnails) > 0 and len(local_files)==len(thumbnails):
      print("Downloading Thumbnails...")
      if not(os.path.isdir(os.path.join(p.output_dir,"thumbnails"))):
        os.mkdir(os.path.join(p.output_dir,"thumbnails"))
      for index in range(len(thumbnails)):
        try:
          dummy              = local_files[index].replace(".tif",".jpg").replace(".jp2",".jpg")
          thumbnail_filename = os.path.join(p.output_dir,"thumbnails",dummy)
          if p.verbose:
            print("Saving [%s] to [%s]" % (thumbnails[index],thumbnail_filename))
          wget.download(thumbnails[index],thumbnail_filename,None)
        except Exception as e:
          print("Unable to make save thumbnail [%s]" % (thumbnail_filename))
    # Ask user if they want to limit the number of files to download
    if p.download and len(aws_commands) > 0:
      stop_index = len(aws_commands)
      if not p.yes:
        test = input("Download all %d files? [y/N] " %(len(aws_commands)))
        if test.lower().find("y") >= 0:
          stop_index = len(aws_commands)
        else:
          test = input("Only download the 10 most recent files? [y/N] ")
          if test.lower().find("y") >= 0:
            stop_index = 10
          else:
            raise SystemExit()
      print("Downloading Images...")
      start_data     = data_used()
      for index in range(stop_index):
        # Download portion of file from input bounding box
        print("[%d of %d]: Downloading to %s/%s" % (index+1,stop_index,p.output_dir,local_files[index]))
        if p.radius <= 10:
          download_box(files[index],local_files[index],box=None,output_dir=p.output_dir,profile=p.profile)
        else:
          download_box(files[index],local_files[index],box,output_dir=p.output_dir,profile=p.profile)
      # Write out geojson features of each file for future upload
      geo_package_file = os.path.join(p.output_dir, "imagery.geojson")
      fid = open(geo_package_file,"w")
      fc = geojson.FeatureCollection(features)
      geojson.dump(fc,fid)
      fid.close()
      total_data     = data_used() - start_data
      print ("%0.1f MB Data Used" % total_data)
  except KeyboardInterrupt:
    pass

if __name__ == '__main__':
  main()


#TODO add whitespace in code and inline comments
#TODO convert to 4 spaces over 2 spaces
