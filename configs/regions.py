import ee

# IMPORTANT: Initialize GEE here using your actual project ID.
# This ensures ee.Geometry can be properly created if called standalone,
# though it will be re-initialized in notebooks.
ee.Initialize(project='gaias-ark') 

# Define the Kenyan Coastal Strip Region of Interest (ROI)
# Copied from GEE Code Editor and directly translated to Python
kenyan_coast_roi = ee.Geometry.Polygon(
    [[[41.5717961934335, -1.6660673751001729],
      [40.797260060621, -1.9405892862517224],
      [40.1545598653085, -2.7693492692094908],
      [39.533832326246, -3.9866897907459995],
      [39.1987493184335, -4.671372188469907],
      [39.4734075215585, -4.720644703111153],
      [40.291888966871, -3.005255303437709],
      [40.2424504903085, -2.7748360052373107],
      [40.4951360371835, -2.55534723599033],
      [40.665424123121, -2.5663225925438042],
      [41.4509465840585, -1.874707854125858]]]
)

print("Region of Interest for Kenyan Coast defined.")