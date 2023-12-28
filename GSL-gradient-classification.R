# set working directory
setwd("C:/Users/amand/Documents/GRADU")
options(stringsAsFactors = FALSE) # strings as factors false

library(ggplot2) # import libraries
library(Metrics)

#######################################################################################
### This script plots the GSL along the urban-rural gradient, fits a linear ###########
### and a quadratic fit to the gradient and saves the associated metrics into file. ###
#######################################################################################

# list all files
all_files <- list.files("C:/Users/amand/Documents/GRADU/Data/results/combined-buffer-results/", pattern = "-buffer-results.csv", 
                        full.names = TRUE)

# create a plotting function
plot_fun <-function(path_to_file) {
  d = read.csv(path_to_file) # read the data
  d <- na.omit(d) # drop nans
  
  # define the columns to plot
  y_col = d$GSL_mean
  x_col = d$distance
  
  # define city name from filepath
  city <- gsub('C:/Users/amand/Documents/GRADU/Data/results/combined-buffer-results/','',path_to_file)
  city <- gsub('-buffer-results.csv','',city)
  
  # fit a linear model and 2nd order polynomial to the variables
  linear <- lm(y_col~x_col, data = d)
  polynomial <- lm(y_col~poly(x_col,2), data = d)

  # calculate describing metrics for both models
  linear_r2 = summary(linear)$r.squared
  poly_r2 = summary(polynomial)$r.squared
  linear_slope = summary(linear)$coefficients[2]
  poly_quad = summary(polynomial)$coefficients[3] # quadratic term
  linear_mae = mae(y_col, predict(linear))
  poly_mae = mae(y_col, predict(polynomial))
  linear_rmse = sqrt(mean(linear$residuals^2)) # RMSE
  poly_rmse = sqrt(mean(polynomial$residuals^2)) # RMSE
  
  # define the gradient pattern based on fit metrics
  if (linear_r2 > 0.5 && linear_slope > 0){
    pattern = 'linear increase' 
  } else if (linear_r2 > 0.5 && linear_slope < 0){
    pattern = 'linear decrease'
  } else if (poly_r2 > 0.5 && linear_r2 < 0.5 && poly_quad > 0){
    pattern = 'quadratic up'
  } else if (poly_r2 > 0.5 && linear_r2 < 0.5 && poly_quad < 0){
    pattern = 'quadratic down'
  } else if (linear_r2 < 0.5 && poly_r2 < 0.5){
    pattern = 'random'
  }
  
  d['pattern'] = pattern

  # text to show in the plot
  plot_text = paste('\nLinear model r2: ',sprintf("%0.2f",linear_r2),', MAE: ',sprintf("%0.2f",linear_mae),', RMSE: ',sprintf("%0.2f",linear_rmse),', slope: ',sprintf("%0.4f",linear_slope),
                    '\n2nd order polynomial r2: ',sprintf("%0.2f",poly_r2),', MAE: ',sprintf("%0.2f",poly_mae),', RMSE: ',sprintf("%0.2f",poly_rmse))
  
  # save the df
  write.csv(d, path_to_file, row.names=FALSE)
  
  # plot
  ggp <- ggplot(d, aes(x=x_col, y=y_col))+
    geom_point(size=3) +
    geom_abline(intercept = coefficients(linear)[1], slope = coefficients(linear)[2], color="red") + # linear model line
    stat_smooth(method = "lm", formula = y ~ poly(x,2), color='blue', size=0.5) + # polynomial line
    ggtitle(city) + theme(plot.title = element_text(hjust = 0.5)) + # 0 line, title, adjust title to center
    ylab("GSL mean (days)") +
    labs(caption = plot_text) + 
    scale_x_continuous("Distance to urban area (km)", labels = as.character(x_col / 1000), breaks = x_col, expand = c(0,0)) # xlabel?

  ggp
  }

# apply the function to all files
lapply(all_files, plot_fun)

