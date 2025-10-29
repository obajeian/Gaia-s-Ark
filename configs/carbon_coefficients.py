# Carbon Fraction of Biomass (proportion of biomass that is carbon)
# Source: IPCC guidelines, scientific literature
CARBON_FRACTION_BIOMASS = 0.47

# Belowground Biomass to Aboveground Biomass Ratio (BGB:AGB)
# Source: Scientific literature for tropical mangroves.
# Used to estimate BGB if only AGB is directly measured.
BGB_AGB_RATIO = 0.40

# Average Mangrove Soil Carbon Density (Mg C / ha / meter depth)
# This is highly variable; this is an illustrative average.
# Source: Blue Carbon Initiative reports, IPCC, regional studies.
SOIL_CARBON_DENSITY_PER_M = 300 # Mg C / hectare / meter of depth

# Default assumed soil depth for carbon stock calculation (meters)
# Mangrove soils can be meters deep; this is a simplified average.
DEFAULT_SOIL_DEPTH_M = 1.0

print("Carbon coefficients loaded.")