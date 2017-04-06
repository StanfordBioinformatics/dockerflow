library(ggplot2)
library(optparse)

parse_arguments <- function() {
  option_list = list(
    make_option(c("-f", "--file"), 
                type = "character", 
                default = NULL,
                metavar = "character",
                help = "Filename of sequencing stats file."),
    make_option(c("-o", "--out"),
                type = "character",
                default = NULL,
                metavar = "character",
                help = "Prefix for plot files."))
  
  opt_parser = OptionParser(option_list = option_list)
  opt = parse_args(opt_parser)
  
  if (is.null(opt$file)){
    print_help(opt_parser)
    stop("Must specify a stats file.n", call.=FALSE)
  }
  return(opt)
}

make_boxplots <- function(data, plot_theme, out){
  # QC passed reads count
  ggplot(data, aes(series, mean_base_quality)) +
    geom_boxplot() +
    plot_theme + 
    labs(title = "Bina ALS Genomes - Mean Base Quality", y = "Quality Score", x = "Series")
  ggsave(file = paste(out, '.mean_base_qual.png', sep=''), width=14.4, height=8.1)
  
  # Percent mapped reads
  ggplot(data, aes(series, mean_seq_quality)) +
    geom_boxplot() +
    plot_theme + 
    labs(title = "Bina ALS Genomes - Mean Sequence Quality", y = "Quality Score", x = "Series")
  ggsave(file = paste(out, '.mean_seq_qual.png', sep=''), width=14.4, height=8.1)
  
  # Percent properly paired
  ggplot(data, aes(series, average_gc_content)) +
    geom_boxplot() +
    plot_theme + 
    labs(title = "Bina ALS Genomes - Average GC Content", y = "Percent", x = "Series")
  ggsave(file = paste(out, '.gc_content.png', sep=''), width=14.4, height=8.1)
}

main <- function() {
  
  opt = parse_arguments()
  file = opt$file
  example_out = opt$out
  
  # This is an ugly workaround for dealing with dockerflow file handling
  # method. I have to specify an output file to the script in order to get
  # the run-specific ID specified at runtime. This extracts the prefix
  # from an output file of format run_id-prefix.plot_type.file_extension.
  out_elements = strsplit(example_out, '.', fixed=TRUE)
  out = out_elements[[1]][1]
  
  print(file)
  data = read.table(file, header=T)
  
  #perc_mapped_reads = data$mapped_read_count / data$total_reads * 100
  #perc_properly_paired = data$properly_paired / data$total_reads * 100
  #data = cbind(data, perc_mapped_reads, perc_properly_paired)
  
  
  greg_theme = theme_minimal(base_size = 20, base_family = "Helvetica") + 
    theme(axis.line = element_line(colour = "black"),
          panel.grid = element_blank())
  seqctr_theme = theme(axis.text=element_text(size=18), axis.title=element_text(size=24), title=element_text(size=24), 
        legend.text=element_text(size=18), legend.title=(element_text(size=24)),
        legend.margin=unit(0.5, "cm"), plot.margin=unit(c(1,1,1,1), "cm"))
  
  make_boxplots(data, seqctr_theme, out)
  
}

if(!interactive()) {
  main()
}