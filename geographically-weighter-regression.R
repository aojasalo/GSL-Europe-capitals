# set working directory
setwd("C:/Users/amand/Documents/GRADU")
options(stringsAsFactors = FALSE) # strings as factors false

library(ggplot2)
library(Metrics)
library(plyr)
library(dplyr)
library(readr)
library(MASS)
library(mgcv)
library(ape)
library(tidyverse)
library(maptools)
library(spgwr)
library(spData)
library(GWmodel)
library(car)
library(sp)

###########################################################################
### This is a script for Geographically Weighted Regression model (GWR) ###
### and all associated analyses using GSL, LST, land cover and DLT data. ## 
###########################################################################

# read all city-level files into one dataframe
data <- list.files("C:/Users/amand/Documents/GRADU/Data/results/combined-buffer-results/", pattern = "-buffer-results.csv", 
                   full.names = TRUE) %>% 
  lapply(read_csv) %>%   
  bind_rows                                         

data <- na.omit(data)

############ Exploratory analysis #############

ggplot(data, aes(x=y, y=GSL_mean))+
  geom_point()
  
# distributions
col = data$GSL_mean
q <- quantile(col)
# plot a histogram showing the distribution
ggplot(data = data, aes(x=col)) +
  geom_histogram(binwidth = 5, color="black", fill="white") +
  xlab("column") +
  geom_vline(xintercept = median(col), colour = "red", linetype = "dashed") +
  geom_vline(xintercept = q[2], colour = "blue", linetype = "dashed") +
  geom_vline(xintercept = q[4], colour = "blue", linetype = "dashed")                                           

# correlations
res <- cor(data,method = c("spearman"))
res[round(res, 2) > 0.7]
round(res,2)

# check spatial autocorrelations with moran's I
data.dists <- as.matrix(dist(cbind(data$y, data$x)))

data.dists.inv <- 1/data.dists
diag(data.dists.inv) <- 0

Moran.I(data$GSL_mean, data.dists.inv)

######## Global OLS to help the variable selection #########

# full linear model used in backwards stepwise variable selection
lm <- lm(GSL_mean ~ poly(ringId_x,2) + poly(broadleaved_percentage,2) + 
                       poly(conifer_percentage,2) + poly(other_veg_percentage,2) + poly(MAT_2017.2021,2) + 
                       poly(urban_fabric_1,2) + poly(agricultural,2) + poly(other,2) +
                       poly(natural_vegetation,2), data=data)

# removing quadratic terms from all except temperature (no theoretical importance)
# removing ringId, other land cover classes and urban fabric 2 (not significant)
# removing broadleaved percentage and other_veg percentage, not as significant as conifers

# final global OLS model
lm <- lm(GSL_mean ~ conifer_percentage +
           poly(MAT_2017.2021,2) + 
           agricultural + urban_fabric_1 +
           natural_vegetation, data=data)

# diagnostics, anova, VIF
summary(lm)
anova(lm, test="T")
vif(lm)

# residuals
plot(lm, which = 1)
res <- resid(lm)
plot(density(res))

########## Geographically Weighted Regression ########

# Testing GWR first with the global OLS variables, other DLT and land cover variables, different bandwidth options 
# and checking local multicollinearity diagnostics. Below is the procedure with final GWR variables.

# adaptive bandwidth with final GWR variables
GWRbandwidth <- gwr.sel(GSL_mean ~ urban_fabric_1 + 
                          MAT_2017.2021 + broadleaved_percentage,
                        data=data, coords = cbind(data$x,data$y), adapt=TRUE)
GWRbandwidth

# fixed bandbidth with final GWR variables
GWRbandwidth <- gwr.sel(GSL_mean ~ urban_fabric_1 + 
                          MAT_2017.2021 + broadleaved_percentage,
                        data=data, coords = cbind(data$x,data$y)) 
GWRbandwidth

# construct final GWR model with fixed bandwidts
gwr.model = gwr(GSL_mean ~ MAT_2017.2021 + broadleaved_percentage + 
                urban_fabric_1, data=data, coords = cbind(data$x,data$y),
                bandwidth = GWRbandwidth,
                hatmatrix=TRUE, se.fit=TRUE, longlat=FALSE) 

# model diagnostics
gwr.model
min(gwr.model$SDF$localR2)
max(gwr.model$SDF$localR2)

# plotting results
spplot(gwr.model$SDF, c("localR2")) #, col.regions=grey.colors(20))
spplot(gwr.model$SDF, c("MAT_2017.2021")) #, col.regions=grey.colors(20))
spplot(gwr.model$SDF, c("broadleaved_percentage")) #, col.regions=grey.colors(20))
spplot(gwr.model$SDF, c("urban_fabric_1")) #, col.regions=grey.colors(20))

# checking local multicollinearity 
# convert to spatial dataframe
spdf <- SpatialPointsDataFrame(coords = cbind(data$x,data$y), data = data,
                               proj4string = CRS("+proj=laea +lat_0=52 +lon_0=10 +x_0=4321000 +y_0=3210000 +ellps=GRS80 +units=m +no_defs "))

# calculate multicollinearity diagnostics
diag <- gwr.collin.diagno(GSL_mean ~ MAT_2017.2021 + broadleaved_percentage +
                            urban_fabric_1, spdf, bw = GWRbandwidth, kernel="gaussian",
                          adaptive=FALSE, p=2, theta=0, longlat=F)

diag$VIF[diag$VIF > 5]

# model results to dataframe
results<-as.data.frame(gwr.model$SDF)

# calculating p-values for each variable
dfree<-gwr.model$results$edf

f_mat <- gwr.model$SDF$MAT_2017.2021 / gwr.model$SDF$MAT_2017.2021_se
results$p_val_mat <- 2 * pt(-abs(f_mat), dfree)

f_broad <- gwr.model$SDF$broadleaved_percentage / gwr.model$SDF$broadleaved_percentage_se
results$p_val_con <- 2 * pt(-abs(f_broad), dfree)

f_urb <- gwr.model$SDF$urban_fabric_1 / gwr.model$SDF$urban_fabric_1_se
results$p_val_urb <- 2 * pt(-abs(f_urb), dfree)

# save model results
write.csv(results, "C:/Users/amand/Documents/GRADU/Data/results/GWR-final-051123.csv", row.names=FALSE)

# convert multicollinearity diagnostics to dataframe and save to csv
diag_df <- as.data.frame(diag$SDF)
write.csv(diag_df, "C:/Users/amand/Documents/GRADU/Data/results/GWR-collin-diagnostics.csv", row.names=FALSE)

############### Sensitivity analysis ############

# construct final GWR model with different bandwidth sizes: 500 km, 1000 km, 2000 km and 10000 km.
gwr.model = gwr(GSL_mean ~ MAT_2017.2021 + broadleaved_percentage + 
                  urban_fabric_1, data=data, coords = cbind(data$x,data$y),
                bandwidth = 500000, # change the bandwidth (unit is m)
                hatmatrix=TRUE, se.fit=TRUE, longlat=FALSE) 

# model diagnostics
gwr.model
min(gwr.model$SDF$localR2)
max(gwr.model$SDF$localR2)

# plotting results
spplot(gwr.model$SDF, c("localR2")) #, col.regions=grey.colors(20))
spplot(gwr.model$SDF, c("MAT_2017.2021")) #, col.regions=grey.colors(20))
spplot(gwr.model$SDF, c("broadleaved_percentage")) #, col.regions=grey.colors(20))
spplot(gwr.model$SDF, c("urban_fabric_1")) #, col.regions=grey.colors(20))

