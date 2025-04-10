library(tidyverse)
library(sjPlot)
library(igraph)
library(networkD3)

seq_counts <- read.csv('Downloads/DATA_304/test/data-304/data/assignment_5/seq_counts.csv')

links <- data.frame(
  source = seq_counts$course1,
  target = seq_counts$course2,
  value = seq_counts$count
)

nodes <- data.frame(
  name = unique(unlist(list(source, target), use.names = FALSE))
)

links$IDsource <- match(links$source, nodes$name) - 1 
links$IDtarget <- match(links$target, nodes$name) - 1

sankey <- sankeyNetwork(Links = links, Nodes = nodes,
                        Source = "IDsource", Target = "IDtarget",
                        Value = "value", NodeID = "name",
                        sinksRight = FALSE)

sankey
