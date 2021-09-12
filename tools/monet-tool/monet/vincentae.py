import math as m


def vincenty(lat1_deg,lon1_deg,az_deg,distance):
	"""
		Given a starting point on the earth and a bearing/distance, calculate
		the ending point
		Inputs:
			lat1_deg		-- Latitude  on Earth's Surface (deg)
			lon1_deg		-- Longitude on Earth's Surface (deg)
			az_deg			-- Azimuth (bearing) from pt1 to desired pt2
			distance		-- Distance from  pt1 to desired pt2 (meters)
		Outputs:
			lat2_deg		-- Latitude  on Earth's Surface (deg)
			lon2_deg		-- Longitude on Earth's Surface (deg)
		NOTE:
			This function breaks at points > Re distance apart, The calling function is
			responsible for wild points
	"""
	lat1     = lat1_deg*m.pi/180.0
	lon1     = lon1_deg*m.pi/180.0
	az       = az_deg*m.pi/180.0

	f = 1.0/298.257223563
	Re = 6378137.0
	Rp = 6356752.314245

	U1      = m.atan( (1.0-f)*m.tan(lat1) )
	sig1    = m.atan( m.tan(U1)/m.cos(az) )
	sinA    = m.cos(U1)*m.sin(az)
	cos2A   = 1.0 - sinA**2.
	u2      = cos2A*( (Re**2. - Rp**2.)/Rp**2. )
	A      = 1.0 + u2/16384.0*( 4096.0 + u2*(-768.0 + u2*(320.0-175.0*u2)))
	B      = u2/1024.0*(256.0 + u2*(-128.0 + u2*(74.0-47.0*u2)))
	sigma  = distance/Rp/A
	sigma_o = sigma
	delta = 1.0e-5
	epsilon = 1.0e-9
	count = 0
	delSig_old = None
	firstPass = True
	while abs(delta) > epsilon:
		# Iteration Loop
		cos2sigM  = m.cos(2.0*sig1 + sigma)
		delSig = B*m.sin(sigma)*(cos2sigM + 0.25*B*(m.cos(sigma)*(-1.0 + 2.0*(cos2sigM**2.)) - B/6.0*cos2sigM*(-3.0 + 4.0*(m.sin(sigma)**2.))*(-3.0 + 4.0*(cos2sigM**2.))))
		sigma = sigma_o + delSig
		delta = abs(delta - abs(delSig))
		if abs(delta) < epsilon or count > 10:
			break
		else:
			if not delSig_old:
				delSig_old = abs(delSig)
			else:
				delta = abs(delSig)-abs(delSig_old)
				delSig_old = abs(delSig)
		count +=1

	lat2 = m.atan2( (m.sin(U1)*m.cos(sigma) + m.cos(U1)*m.sin(sigma)*m.cos(az)),( (1.0-f)*m.sqrt(sinA**2 + (m.sin(U1)*m.sin(sigma) - m.cos(U1)*m.cos(sigma)*m.cos(az))**2) ) )
	Lambda = m.atan2( m.sin(sigma)*m.sin(az),( m.cos(U1)*m.cos(sigma) - m.sin(U1)*m.sin(sigma)*m.cos(az) ) )
	C         = f/16.0*cos2A*( 4.0 + f*(4.0 - 3.0*cos2A) )
	L = Lambda - (1.0 - C)*f*sinA*( sigma + C*m.sin(sigma)*( cos2sigM + C*m.cos(sigma)*(-1.0 + 2.0*cos2sigM**2)))
	L2 = L + lon1
	lat2 = lat2*180.0/m.pi
	lon2 = L2*180.0/m.pi
	return(lat2,lon2)

def ivincenty(lat1_deg,lon1_deg,lat2_deg,lon2_deg):
	"""
		Given two points (A,B) on the earth, return the bearing from A --> B
		and the distance (m) from A --> B
		Inputs:
			lat1_deg		-- Latitude  on Earth's Surface (deg)
			lon1_deg		-- Longitude on Earth's Surface (deg)
			lat2_deg		-- Latitude  on Earth's Surface (deg)
			lon2_deg		-- Longitude on Earth's Surface (deg)
		Outputs:
			az_deg			-- Azimuth (bearing) from pt1 to pt2 (deg)
			distance		-- Distance from  pt1 to pt2 (meters)
		NOTE:
			This function breaks at points > Re distance apart, The calling function is
			responsible for wild distances
	"""
	lat1 = lat1_deg*m.pi/180.0
	lon1 = lon1_deg*m.pi/180.0
	lat2 = lat2_deg*m.pi/180.0
	lon2 = lon2_deg*m.pi/180.0

	f = 1.0/298.257223563
	Re = 6378137.0
	Rp = 6356752.314245

	L  = lon2-lon1
	U1 = m.atan( (1.0-f)*m.tan(lat1) )
	U2 = m.atan( (1.0-f)*m.tan(lat2) )
	Lambda = L
	delta = 1.0e-5
	epsilon = 1.0e-9
	count   = 0
	while delta > epsilon:
		# Iteration Loop
		sinSig    = m.sqrt( (m.cos(U2)*m.sin(Lambda))**2. + ( m.cos(U1)*m.sin(U2) - m.sin(U1)*m.cos(U2)*m.cos(Lambda) )**2. )
		cosSig    = m.sin(U1)*m.sin(U2) + m.cos(U1)*m.cos(U2)*m.cos(Lambda)
		sigma     = m.atan( sinSig/cosSig )
		sinA      = m.cos(U1)*m.cos(U2)*m.sin(Lambda)/sinSig
		cos2A     = 1.0 - sinA**2.
		cos2sigM  = cosSig - 2.0*m.sin(U1)*m.sin(U2)/cos2A
		C         = f/16.0*cos2A*( 4.0 + f*(4.0 - 3.0*cos2A) )
		g         = L + (1.0-C)*f*sinA*( sigma + C*sinSig*(cos2sigM + C*cosSig*(-1.0 + 2.0*(cos2sigM**2))))
		delta     = abs(g-Lambda)
		count    += 1
		if delta < epsilon  or count > 30:
			break
		else:
			Lambda = g

	Lambda = g
	u2     = cos2A*( (Re**2 - Rp**2)/Rp**2)
	A      = 1.0 + u2/16384.0*( 4096.0 + u2*(-768.0 + u2*(320.0-175.0*u2)))
	B      = u2/1024.0*(256.0 + u2*(-128.0 + u2*(74.0-47.0*u2)))
	delSig = B*sinSig*(cos2sigM + 0.25*B*(cosSig*(-1.0 + 2.0*(cos2sigM**2)) - B/6.0*cos2sigM*(-3.0 + 4.0*(sinSig**2))*(-3.0 + 4.0*(cos2sigM**2))))
	distance      = Rp*A*(sigma - delSig)
	a1     = m.atan2( (m.cos(U2)*m.sin(Lambda)),( m.cos(U1)*m.sin(U2) - m.sin(U1)*m.cos(U2)*m.cos(Lambda) ) )
	a2     = m.atan2( (m.cos(U1)*m.sin(Lambda)),( -1.0*m.sin(U1)*m.cos(U2) + m.cos(U1)*m.sin(U2)*m.cos(Lambda) ) )
	a1     = a1*180.0/m.pi
	a2     = a2*180.0/m.pi
	if a1 < 0:
		a1 += 360.0

	return(a1,distance)

def gen_bbox(lat1_deg,lon1_deg,radius=10):
  """
    gen_bbox returns the upper left and lower right coordinates of the bounding box
    who's center is at the specified lat/lon
    Inputs:
      lat1_deg -- Input latitude (degrees)
      lon1_deg -- Input longitude (degrees)
      radius   -- Inputs radius (meters)
    Outputs:
      bbox     -- List of tuples, first tuple is upper left, second is lower right
  """
  rad = radius*m.sqrt(2.0)
  # Get upper left lat/lon
  (lat_ul,lon_ul) = vincenty(lat1_deg,lon1_deg,315,rad)
  # Get lower right lat/lon
  (lat_lr,lon_lr) = vincenty(lat1_deg,lon1_deg,135,rad)
  return [lon_ul,lat_ul,lon_lr,lat_lr]

def gen_bbox_geojson(lat1_deg,lon1_deg,radius=10):
  """
    gen_bbox_geojson returns a multi-polygon bounding box for a given lat/lon
    Inputs:
      lat1_deg  -- Input latitude (degrees)
      lon1_deg  -- Input longitude (degrees)
      radius    -- Input radius (meters)
    Outputs:
      bbox      -- Multi-polygon geojson bounding box
  """
  rad = radius*m.sqrt(2.0)
  # Get upper left lat/lon
  (lat_ul,lon_ul) = vincenty(lat1_deg,lon1_deg,315,rad)
  # Get upper right lat/lon
  (lat_ur,lon_ur) = vincenty(lat1_deg,lon1_deg,45,rad)
  # Get lower right lat/lon
  (lat_lr,lon_lr) = vincenty(lat1_deg,lon1_deg,135,rad)
  # Get lower left lat/lon
  (lat_ll,lon_ll) = vincenty(lat1_deg,lon1_deg,225,rad)
  bbox = [[lon_ul,lat_ul],[lon_ur,lat_ur],[lon_lr,lat_lr],
          [lon_ll,lat_ll],[lon_ul,lat_ul]]
  b = {}
  b["type"]       = "FeatureCollection"
  b["name"]       = "bbox"
  b["crs"]        = {"type":"name","properties":{"name":"urn:ogc:def:crs:OGC:1.3:CRS84"}}
  b["features"]   = []
  g               = {}
  g["type"]       = "Feature"
  g["geometry"]   = {"type":"MultiPolygon","coordinates":[[bbox]]}
  g["properties"] = {"id":None}
  b["features"].append(g)
  return b

def ihaversine(lat1_deg,lon1_deg,lat2_deg,lon2_deg):
  """
    ihaversine returns the great circle distance from two points on the earth's surface
    Inputs:
      lat1_deg -- First Point's latitude
      lon1_deg -- First Point's longitude
      lat2_deg -- Second Point's latitude
      lon2_deg -- Second Point's longitude
    Outputs:
      d        -- Great Circle's distance
  """
  lat1 = lat1_deg*m.pi/180.0
  lon1 = lon1_deg*m.pi/180.0
  lat2 = lat2_deg*m.pi/180.0
  lon2 = lon2_deg*m.pi/180.0
  r = 6378.137*1.0e3

  d = 2.0*r*m.asin(m.sqrt(m.sin(0.5*(lat2-lat1))**2. + m.cos(lat1)*m.cos(lat2)*m.sin(0.5*(lon2-lon1))**2.0))
  return d
