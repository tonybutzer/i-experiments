import os
import datetime, psutil
import argparse
from osgeo import gdal
from boto3 import Session
from monet.__version__ import __version__


def argParser():
    """
    Args:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('latitude' ,type=float, help="Latitude  (DECIMAL, DD.DDDDDDD)",nargs=1)
    parser.add_argument('longitude',type=float, help="Longitude (DECIMAL, DD.DDDDDDD)",nargs=1)
    parser.add_argument('-r', '--radius', dest='radius',
                        type=float, default=1000,
                        help="Bounding box radius (default: 1000 meters)")
    parser.add_argument('-a', '--api-key', dest='apiKey',
                        type=str, default=None,
                        help="x-api-key value that will be included in the request headers")
    parser.add_argument('-s', '--start-date', dest='start_date',
                        type=str, default=\
                        datetime.datetime.strftime(datetime.datetime.now() -\
                        datetime.timedelta(days=1095),"%Y-%m-%d"),
                        help="Start Date YYYY-MM-DD (default: 3 years ago)")
    parser.add_argument('-e', '--end-date', dest='end_date',
                        type=str, default=\
                        datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d"),
                        help="End Date YYYY-MM-DD (default: now)")
    parser.add_argument('-c', '--cloud-cover', dest='cloud_cover',
                        type=float, default=10.0,
                        help="Cloud cover (percent 0-100) default 10.0")
    parser.add_argument('-d', '--data-coverage', dest='data_coverage',
                        type=float, default=80.0,
                        help="Data coverage, for Sentinel only (percent 0-100) default 80.0")
    parser.add_argument('-u', '--url', dest='url',
                        default="https://earth-search.aws.element84.com/v0",
                        help="STAC URL default: 'https://earth-search.aws.element84.com/v0'")
    parser.add_argument('-C', '--collection', dest='collection',
                        type=str, default='sentinel-s2-l2a-cogs',
                        help="STAC collection default: 'sentinel-s2-l2a-cogs'")
    parser.add_argument('-o', '--output-dir', dest='output_dir',
                        default="./imagery",
                        help="Output Directory for saved files (default ./imagery/)")
    parser.add_argument('-D', '--download', dest='download',
                        action="store_true", default=False,
                        help="Download flag, default (False)")
    parser.add_argument('-t', '--thumbnails', dest='thumbnails',
                        action="store_true",default=False,
                        help="Store thumbnails for downloaded images in thumbnails directory")
    parser.add_argument('-P', '--print-all', dest='all_flag', action="store_true",
                        help="Print out all of the S3 files  \
                              (default: limit to 10)", \
                        default=False)
    parser.add_argument('-p', '--profile', dest='profile',type=str,default="default",
                        help="AWS environment profile  \
                              (default: 'default')", \
                        )
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action="store_true",default=False,
                        help="Verbose output to stdout")
    parser.add_argument('-y', '--yes', dest='yes',
                        action="store_true",default=False,
                        help="Force Yes to all stdin questions, useful when run in background")
    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))
    return parser.parse_args()

def download_box(remote_filename,local_filename,box=None,output_dir="./imagery",profile="default"):
  """
    download_box downloads an AWS S3 tile limited by input bounding box
    Inputs:
      remote_filename   -- S3 file (e.g. s3://sentinel-s2-l2a/tiles/16/T/DM/2020/1/21/0/R10m/TCI.jp2)
      local_filename    -- local file to save as, (e.g. 20200121_16TDM_00_R10m_TCI.tif)
      box               -- Bounding box [ul_lon,ul_lat,lr_lon,lr_lat] (degrees)
      output_dir        -- Output Directory to save
  """
  access_key = secret_key = None
  try:
    session = Session(profile_name=profile)
    creds   = session.get_credentials()
    access_key = creds.access_key
    secret_key = creds.secret_key
  except:
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
  if remote_filename.find("s3") == 0:
    s3_filename = remote_filename.replace("s3://","/vsis3/")
  elif remote_filename.find("http") == 0:
    s3_filename = "/vsicurl/%s" % (remote_filename)
  if local_filename.find("jp2") >=0:
    local_tif = local_filename.replace("jp2","tif")
  else:
    local_tif = local_filename
  output_filename = os.path.join(output_dir,local_tif)
  try:
    if (access_key is not None) and (secret_key is not None):
      gdal.SetConfigOption("AWS_SECRET_ACCESS_KEY",secret_key)
      gdal.SetConfigOption("AWS_ACCESS_KEY_ID",access_key)
    gdal.UseExceptions()
    ds = gdal.Open(s3_filename)
  except Exception as e:
    print("Unable to save [%s] to [%s]" % (remote_filename,output_filename))
    print(e)
  try:
    if not box:
      # Download the entire file
      gdal.Warp(output_filename,ds)
    else:
      success = False
      try:
        # Try projecting to 4326 first, if not, keep source proj
        gdal.Warp(output_filename,ds,
                 outputBounds=box,outputBoundsSRS="EPSG:4326",
                 format="GTiff",multithread=True,copyMetadata=True)
        success = True
      except:
        success = False
      if not success:
        try:
          print("Tried projecting to EPSG:4326, keeping source proj")
          # Keeping source proj
          gdal.Warp(output_filename,ds,
                   outputBounds=box,
                   format="GTiff",multithread=True,copyMetadata=True)
        except Exception as e:
          print(e)
  except Exception as e:
    print("Unable to save [%s] to [%s]" % (remote_filename,output_filename))
    print(e)


def gen_aws_local_file(filename):
  """
    gen_aws_local_file converts the S3 bucket filename to a local friendly filename
    Inputs:
      filename -- AWS S3 url
  """
  if filename.find("http") == 0:
    # Need to chop off .com/
    try:
      s3 = filename.split(".com/")[1].split("/")
      if len(s3) <= 6:
        r  = s3[4].split("_")
      else:
        r  = s3[6].split("_")
      runid = "%s_%s_%02d_R10m_%s" % (\
              r[2],r[1],int(r[3]),s3[-1])
    except Exception as e:
      print(e)
  elif filename.find("s3") == 0:
    try:
      c = filename.split("tiles")[1].split("/")
      runid = "%d%02d%02d_%s%s%s_%02d_%s_%s" % (\
              int(c[4]),int(c[5]),int(c[6]),
              c[1],c[2],c[3],int(c[7]),c[8],c[9])
    except:
      runid = os.path.basename(filename)
  else:
    print("Cannot make a local filename")
    raise SystemExit()
  return runid

def print_aws_cp_command(filename):
  """
    print_aws_cp_command prints the AWS command line to download individual tile, helpful for debugging
    Inputs:
      filename -- AWS filename
  """
  local_file = gen_aws_local_file(filename)
  s = "aws s3 cp %s %s --request-payer" % \
      (filename,local_file)
  return s,local_file

def data_used():
  """
    data_used returns the data (sent and received) at the point when it is called in Megabytes.
  """
  data_total = (psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv)/1024./1024.
  return float(data_total)
