#################################
# SPLAT! and Shout on 3690 MHz
################################
library(quantmod)
library(fpp)
library(seasonal)
library(TStudio)
library(seasonalview)
library(mFilter)
library(readxl)


##### FILE Imports
# =================
# Shout Data
shout <- read_excel("3690.xlsx", sheet=1)
attach(shout)
View(shout)

# SPLAT! data
splat <- read_excel("splat-3690.xlsx", sheet=1)
attach(splat)
View(splat)


##### PLOT: SPLAT and Shout
# =================
plot(splat$`Distance`, 
     splat$`Avg Power`,
     main = "SPLAT! & Shout Comparison at 3690 MHz",
     xlab = "Path Length (m)", 
     ylab = "Received Power (dbm, Unknown Ref)",
     xlim = c(500, 2500),
     ylim = c(-115, -50),
     col = 'red')

lines(shout$Distance, shout$`Avg Power`, type = "p", col = "blue")
legend("topright", c("SPLAT!", "Shout"), fill = c("red", "blue"))

##### Regression: SPLAT and Shout
# =================
regsplat <- lm(splat$`Avg Power` ~ splat$Distance, data = splat)
regshout <- lm(shout$`Avg Power` ~ shout$Distance, data = shout)

# Add Regression Line to Plot 
abline(regsplat, col='red')
# Add Regression Line to Plot 
abline(regshout, col='blue')


##### Naming: SPLAT and Shout
# =================
text(splat$Distance, 
     splat$`Avg Power`, 
     labels = splat$Name, 
     cex = .5, font=1, pos=3)

text(shout$Distance, 
     shout$`Avg Power`, 
     labels = splat$Name, 
     cex = .5, font=1, pos=3)


##### End of File
# =================
