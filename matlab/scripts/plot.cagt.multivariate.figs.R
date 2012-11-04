require(ggplot2)
library('reshape')

plot.cagt.multivariate.figs <- function(cagt.table.filename,
                                        output.dir=NULL,
                                        output.file=NULL,
                                        output.format="pdf",
                                        support.thresh=0,
                                        orient.shapes=T,
                                        replace.flag=T,
                                        partner.marks="all",
                                        zscore=F,
                                        common.scale=F,
                                        plot.over=F,
                                        whiskers=F,
                                        mag.shape="all" 
                                        ) {
  
  #   cagt.table.filename : name of CAGT table file (can be gzipped)
  #   output.dir=NULL : name of output directory. If set to null, the directory of the input file will be used.
  #   output.file=NULL : prefix output file (without extension). If set to null, the file will be <prefix of input file>.<partner.marks>.<mag.shape>
  #   output.format="pdf" : format of figures (png or pdf)
  #   support.thresh=0 : remove shapes whose support is < support.thresh * fraction of peaks in high signal component
  #   orient.shapes=T : If set to T then for the shape clusters, if required invert shapes to make them Low (left) to High (right)                                        
  #   replace.flag=T : If set to F then if output files exist the function returns without plotting anything
  #   partner.marks="all" : The partner mark(s) that you want to plot alongside the target mark. You can specify multiple eg. c("GC","DNase"). Regular expressions are also allowed for matching. Set to "all" to print all marks.
  #   zscore=F : whether to plot standardized plots or original scale
  #   common.scale=F : Set to T if you want to put all magnitude plots on a common scale
  #   plot.over=F : If T, all signals will be in one set of plots (using facet_wrap). Otherwise, each partner mark will go to a different row (with facet_grid).
  #   whiskers=F : Whether to plot percentile whiskers or just the mean signal.
  #   mag.shape="all" : "shape" plots just the clusters. "mag" plots the aggregation plot over all clusters and the "high" and "low" signal components. "all" plots clusters and signal components.
  #
  #   Authors: Anshul Kundaje, Sofia Kyriazopoulou
  
  # If output.dir is NULL set directory to same directory as cagt.table.filename
  if (is.null(output.dir)) {
    output.dir <- dirname(cagt.table.filename)
  }
  # Create output directory if it doesn't exist
  if (! file.exists(output.dir) ) {
    dir.create(output.dir,recursive=T)
  }
  
  # Convert support to fraction if expressed as percentage
  if (support.thresh >= 1) {
    support.thresh <- support.thresh / 100
  }
  
  input.file.stub <- basename(cagt.table.filename)
  if(is.null(output.file)){
    output.file <- paste( file.path(output.dir, gsub(pattern="\\.txt(\\.gz)?$",replacement="",x=input.file.stub)), 
                          paste(partner.marks,collapse="-"),
                          mag.shape,
                          output.format, 
                          sep=".")
  }else{
    output.file = file.path(output.dir, paste(output.file, output.format, sep = '.'))
  }
  
  if (!replace.flag && file.exists(output.file)) {
    cat("Skipping",cagt.table.filename,": Output files already exist. Use replace.flag=T to overwrite\n")
    return()
  }  
  
  # First 3 lines starting with # are headers (long, short and data type headers)
  # Descriptive columns are (TF  Mark  Cluster  Prctile	Pos)
  # These are followed by data columns representing target mark and various other marks aggregated based on clustering on target mark
  # Data types are of the form "Median", "LowPrc", "HighPrc", "MedianNorm", "LowPrcNorm", "HighPrcNorm"
  # The target mark is represented by the word SIGNAL in the "short" header
  cagt.table.headers <- as.matrix( read.table(file=cagt.table.filename,                                
                                              sep="\t",
                                              header=F,
                                              comment.char="",
                                              nrows=3))
  # Remaining lines are data
  cagt.table <- read.table(file=cagt.table.filename,
                           sep="\t",
                           header=F,
                           comment.char="#")
  
  # headers is a data frame with 3 columns (long, short and type)
  # long: has long names of each column in CAGT table (wgEncode....)
  # short: has the short name of each column
  # type: "Median", "LowPrc", "HighPrc", "MedianNorm", "LowPrcNorm", "HighPrcNorm"
  headers <- data.frame(long=gsub(pattern="#",replacement="", as.character(cagt.table.headers[1,]) ) ,
                        short=gsub(pattern="#",replacement="", as.character(cagt.table.headers[2,]) ) ,
                        type=gsub(pattern="#",replacement="", as.character(cagt.table.headers[3,]) ))
  
  # main.data: Descriptive columns (TF  Mark  Cluster  Prctile  Pos)
  main.data <- cagt.table[, c(3:5)]
  colnames(main.data) <- as.character(headers$type[3:5])
  signal.name = as.character(cagt.table[1,2])
  
  # Find total number of peaks for this table Cluster=="all" and Prctile column
  n.peaks <- main.data$Prctile[ which(main.data$Cluster == "all")[1] ]
  prc.high <- main.data$Prctile[ which(main.data$Cluster == "high")[1] ]
    
  # supp.data: Supplementary data (aggregate data for different marks)
  supp.data <- cagt.table[, c(6:ncol(cagt.table))]
  headers <- headers[c(6:nrow(headers)) , ] # headers now only represent supp.data
  bad.cols = apply(supp.data, 2, function(x) all(is.nan(x)))
  supp.data = supp.data[, !bad.cols]
  headers = headers[!bad.cols, ]
  resort.idx <- order(headers$long, headers$short, headers$type) # reorder columns of supp data
  headers <- headers[resort.idx,] 
  supp.data <- supp.data[, resort.idx]
  colnames(supp.data) <- make.names( paste(headers$type, headers$short, sep="."), unique=T )
  headers$short <- sub(pattern="^[^\\.]+\\.",replacement="",colnames(supp.data)) # This is to rename multiple versions of the same mark with numeric suffixes
  
  # Use the Prctile column to find all rows that pass support.thresh
  valid.support.row.idx <- which( main.data$Prctile >= (support.thresh*prc.high ) )
  main.data <- main.data[ valid.support.row.idx , ]  
  supp.data <- supp.data[ valid.support.row.idx, ]
  
  # Remove the redundant columns corresponding to the target signal
#   target.long.name <- gsub( pattern="(^.+_AT_)|(_clusterData.+$)", replacement="", x=basename(cagt.table.filename)) # Get name of target mark file name from cagt.table.filename
#   rm.idx <- which(headers$long == target.long.name)
#   if (length(rm.idx)==0) {
#     target.short.name <- target.long.name
#   } else {
#     target.short.name <- headers$short[ rm.idx[1] ]
#     supp.data <- supp.data[, -rm.idx]
#     headers <- headers[-rm.idx, ]    
#   }
#   print(target.short.name)

  # Remove supplementary data columns that dont match any elements of partner.marks
  if ( ! all(tolower(partner.marks) == "all") ) {
    keep.idx <- grep(pattern="SIGNAL",x=headers$short)
    for (i in partner.marks) {
      keep.idx <- c(keep.idx, grep(pattern=i, x=headers$short, ignore.case=T))
    }
    supp.data <- supp.data[, keep.idx]
    headers <- headers[keep.idx, ]
  }
  max.pos = max(main.data$Pos)
  min.pos = min(main.data$Pos)
  middle.pos = round((max.pos + min.pos) / 2)
  
  # If orient.shapes=T then invert shapes that are High(left) to Low(Right)
  if (orient.shapes == T) {
    # For each cluster, compute the max MEDIAN signal value over all data points to the LEFT of the anchor point (Pos < 0)
    left.max <- cast( cbind(main.data, data.frame(Median=supp.data$Mean.SIGNAL)),
                      Cluster~. , function(x) max(x,na.rm=T), value="Median", subset=Pos<middle.pos)
    # For each cluster, compute the max MEDIAN signal value over all data points to the RIGHT of the anchor point (Pos > 0)
    right.max <- cast( cbind(main.data, data.frame(Median=supp.data$Mean.SIGNAL)),
                       Cluster~. , function(x) max(x,na.rm=T), value="Median", subset=Pos>middle.pos)
    flip.Cluster.names <- as.character( left.max[,1][left.max[,2] > right.max[,2]] ) # names of clusters to flip
    if (length(flip.Cluster.names) > 0) {
      for (tc in flip.Cluster.names) {
        curr.idx <- which(main.data$Cluster == tc) # rows corresponding to shape 'tc'
        curr.idx <- curr.idx[ order( main.data[curr.idx,"Pos"], decreasing=F ) ] # Reorder curr.idx so that they represent positions in ascending order
        main.data[curr.idx,] <- main.data[rev(curr.idx),] # Replace these rows in main.data with the row_ids reversed (flip signal)
        main.data[curr.idx,"Pos"] <- max.pos + min.pos - main.data[curr.idx,"Pos"] # flip the sign of the reordered positions
        supp.data[curr.idx,] <- supp.data[rev(curr.idx),] # Replace these rows in supp.data with the row_ids reversed
      }
    }
  }
  
  # Split supp.data into multiple data frames for each summary type and then melt them into the long form
  # type: "Median", "LowPrc", "HighPrc", "MedianNorm", "LowPrcNorm", "HighPrcNorm"
  all.types <- as.character(unique(headers$type))
  supp.data.by.type <- NULL
  for (i in all.types) {
    tmp.idx <- which(headers$type == i) # Get columns that represent summary type
    tmp.data <- data.frame(supp.data[, tmp.idx])

    colnames(tmp.data) <- as.character( headers$short[tmp.idx] ) # name the columns based on the short name of the mark
    tmp.data <- cbind(main.data,tmp.data) # Add main.data 
    tmp.data <- melt(data=tmp.data, id.vars=c(1:3),) # melt to create long form
    colnames(tmp.data)[colnames(tmp.data)=="value"] <- i # Name the value column same as the summary type
    if (is.null(supp.data.by.type)) {
      supp.data.by.type <- tmp.data
    } else {
      supp.data.by.type <- merge(supp.data.by.type, tmp.data)
    }
  }

  # Change "variable" named SIGNAL to the target.mark name and reorder the levels so that SIGNAL is always first and then alphabetical
  all.mark.names <- c(signal.name, sort( setdiff( levels(supp.data.by.type$variable), "SIGNAL" ) ) )
  supp.data.by.type$variable <- factor( gsub(pattern="SIGNAL", replacement=signal.name, x=as.character(supp.data.by.type$variable)), 
                                        ordered=T, levels=all.mark.names)
  # Convert cluster ids to ordered set (all,high,low,shape1 ... shapeN)
  shape.cluster.ids <- setdiff( unique(supp.data.by.type$Cluster), c("all","high","low") )
  shape.cluster.ids <- sort(as.numeric(gsub(pattern="shape",replacement="",shape.cluster.ids)))
  shape.cluster.ids <- paste("P_",as.character(shape.cluster.ids),sep="")
  all.cluster.ids <- c("all","high","low",shape.cluster.ids)
  supp.data.by.type$Cluster <- gsub(pattern="shape",replacement="P_",x=supp.data.by.type$Cluster)
  supp.data.by.type$Cluster <- factor(supp.data.by.type$Cluster,ordered=T,levels=all.cluster.ids)

  # Add the support values
  cluster.name.supp <- supp.data.by.type[ !duplicated(supp.data.by.type$Cluster), c("Cluster","Prctile") ] # Names and support of cluster ids
  cluster.name.supp <- cluster.name.supp[ match( levels(supp.data.by.type$Cluster), cluster.name.supp$Cluster ) , ] # reorder to match order of levels in supp.data.by.type$Cluster
  all.levels <- paste( as.character(cluster.name.supp$Cluster), " (", cluster.name.supp$Prctile, "%)", sep="" )
  all.levels <- sub(pattern="(all.*)%",replacement="\\1",x=all.levels)
  levels(supp.data.by.type$Cluster) <- all.levels

  # Retain only magnitude or shape plots or use all depending on mag.shape parameter
  if (mag.shape == "mag") {
    supp.data.by.type <- supp.data.by.type[ grep(pattern="P_", x=supp.data.by.type$Cluster, invert=T) , ]
  }

  if (mag.shape == "shape") {
    supp.data.by.type <- supp.data.by.type[ grep(pattern="P_", x=supp.data.by.type$Cluster) , ]
  }

  p <- ggplot(supp.data.by.type)
  
  # whiskers
  if (whiskers) {
    if (zscore) {
      p <- p + geom_ribbon(aes(x=Pos,ymin=LowPrcNorm,ymax=HighPrcNorm,fill=variable),alpha=0.3) 
    } else {
      #p <- p + geom_ribbon(aes(x=Pos,ymin=LowPrc,ymax=HighPrc), fill = "grey80")
      p <- p + geom_ribbon(aes(x=Pos,ymin=LowPrc,ymax=HighPrc,fill=variable),alpha=0.3)
    }    
  }
  
  nvars = length(unique(supp.data.by.type$variable))
  # median
  if (zscore) {
    p <- p + geom_line(aes(x=Pos,y=MeanNorm,color=variable),size=1)
  } else {
    p <- p + geom_line(aes(x=Pos,y=Mean,color=variable),size=1)    
    #p <- p + geom_line(aes(x=Pos,y=Median),size=1)    
  }
  
  # horizontal and vertical lines
  p <- p + 
    #geom_hline(yintercept=0,color="grey30",size=0.3) + 
    geom_vline(xintercept=0,color="grey30",size=0.3)
  
  # Faceting and scaling
  if (common.scale) {
    scale.val="fixed"
  } else {
    scale.val="free"
  }    
  if (plot.over) {
    p <- p + facet_wrap(~Cluster,nrow=3,scales=scale.val)
  } else {
    p <- p + facet_grid(variable~Cluster,scales=scale.val)
  }
  
  # Formatting
  if (zscore) { 
    y.label="Standardized signal"
  } else {
    y.label="Signal"
  }
  p <- p +
    theme_bw() +
    xlab("Distance from summit") + 
    ylab(y.label) 
  p <- p + opts(axis.text.x = theme_text(size=14,angle=-45,vjust=1,colour="black"),
                axis.text.y = theme_text(size=14,colour="black",hjust=1),
                axis.title.x = theme_text(size=20),
                axis.title.y = theme_text(size=20,angle=90, vjust=0.3),       
                strip.text.x = theme_text(size=18,colour="black"),
                strip.text.y = theme_text(size=18,angle=90,colour="black"),
                legend.title = theme_blank(),
                legend.text = theme_text(size=7,colour="black")
                )
  
  if (!plot.over || nvars < 2) {
    p <- p + opts(legend.position="none") # Remove legend if we are are plotting different marks in different rows
  }
    
  if (plot.over) {
    extra.margin=2
    n.rows <- 2.5
    n.cols <- ceiling( length(unique(supp.data.by.type$Cluster)) / n.rows )
  } else {
    extra.margin=0
    n.rows <- length(unique(supp.data.by.type$variable))
    n.cols <- length(unique(supp.data.by.type$Cluster))
  }
  ggsave(filename=output.file,plot=p,width=((2.5*n.cols)+0.5+extra.margin),height=((2.5*n.rows)+0.5),dpi=300) 
}
