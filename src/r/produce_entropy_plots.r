# NAME: produce_entropy_plots.r
# DATE: 22-MAR-20
# LAST EDIT: 24-MAR-20
# AUTHOR: Author <62926253+kroot-kaytetye@users.noreply.github.com>
# PROJECT: kroot
# SUMMARY: Produces several plots and data tables based on the output from the python functions in this project. This script
#          is not called by main.rs, and needs to be run independently. It takes as its argument the same folder as the 
#          second argument for kroot.exe.
# EXAMPLE CALL: rscript C:\kroot\src\\r\produce_entropy_plots.r C:\docs\kroot_docs
library(pacman)
p_load(dplyr, magrittr, stringr, stringi, tidyr, ggplot2, readr)
#args = commandArgs(trailingOnly = T)
if(length(args) != 1) {
  stop("This script requires one argument!")
}
# Create r_plots and r_tables if they don't exist
dir.create(file.path(args[1], "\\r_plots"), showWarnings = F)
dir.create(file.path(args[1], "\\r_tables"), showWarnings = F)

ent_tb <- read_csv(paste0(args[1], "\\py_outputs\\phonological_entropy.csv"))
# STEP 1: CREATE POSITIONAL ENTROPY PLOT
label_names <- vector()
for (i in 1:length(ent_tb$entropy)) {
  labl <- ent_tb$syl[i] %>% strsplit("_") %>% unlist()
  if(labl[1] == "final") {
    label_names[i] <- paste0("Syllable ", labl[1], " ", labl[2])
  }else {
    label_names[i] <- paste0("Syllable ",as.numeric(labl[1]) + 1, " ", labl[2])
  }
}

ent_tb <- ent_tb %>% mutate(label_names = label_names)
ent_tb <- ent_tb[!grepl("final coda", ent_tb$label_names),]
ent_gg <- ggplot(ent_tb, aes(x = label_names, y = entropy)) + 
  geom_histogram(stat = "identity") + 
  theme(text = element_text(size=10),
  axis.text.x = element_text(angle=90, hjust=1))  + 
  scale_x_discrete(limits = ent_tb$label_names) + 
  xlab("Syllable") + 
  ylab("Shannon Entropy")
ggsave(paste0(args[1], "\\r_plots\\shannon_entropy.png"))
# save ent_tb
write_csv(ent_tb, paste0(args[1], "\\r_tables\\entropy_tab.csv"))

# STEP 2: CREATE WORD SURPRISAL PLOTS
sur_tab <- readr::read_csv(paste0(args[1], "\\py_outputs\\lexical_surprisals.csv"))
sur_tab$lexeme <- sur_tab$lexeme
sur_tab<- sur_tab %>% mutate(vowel_count = stri_count_regex(lexeme, "[\u0250\u0259iIuU]"),
                             vowel_initial = grepl("^[\u0250\u0259iIuU]", lexeme))
cat <- vector()
for(i in 1:length(sur_tab$lexeme)) {
  cat <- c(cat, paste0(sur_tab$vowel_initial[i], sur_tab$vowel_count[i], collapse = "_"))
}
cat <- cat %>% stri_replace_all_fixed("TRUE", "V_") %>% stri_replace_all_fixed("FALSE", "C_")
sur_tab <- sur_tab %>% mutate(cat=cat)

cats <- cat %>% unique()
mean_surp <- vector()
for(categ in cats) {
  mean_surp <- c(mean_surp, mean(sur_tab$mean_surprisal[sur_tab$cat == categ]))
}

out_tab <- cbind(cats, mean_surp) %>% data.frame(stringsAsFactors = F)
out_tab$mean_surp <- as.numeric(out_tab$mean_surp) %>% round(digits = 4)

# calculate difference from grand mean
out_tab <- out_tab %>% mutate(mean_diff = mean_surp - mean(mean_surp))
std_devs <- vector()
for(i in 1:length(out_tab$cats)) {
  std_devs <- c(std_devs, sd(sur_tab$mean_surprisal[sur_tab$cat == out_tab$cats[i]]))
}
out_tab <- out_tab %>% mutate(std_dev = std_devs)

sur_dens <- ggplot(sur_tab, aes(x = mean_surprisal)) + geom_density(alpha = 0.5)
ggsave(paste0(args[1], "\\r_plots\\surprisal_density_plot.png"))

sur_hist <- ggplot(out_tab, aes(x = cats, y = mean_surp)) + geom_histogram(stat='identity') +xlab("Category") + ylab("Mean Surprisal")
ggsave(paste0(args[1], "\\r_plots\\surprisal_by_category.png"))
# save surprisal tab
write_csv(out_tab, paste0(args[1], "\\r_tables\\surprisal_categories.csv"))
# save categories for each lexeme
write_csv(sur_tab, paste0(args[1], "\\r_tables\\lexemes_by_category.csv"))

# STEP 3ː Create frequency table of different categories, with sum entropy
cat_tab <- sur_tab$cat %>% table() %>% data.frame(stringsAsFactors = F)
tab_cats <- levels(droplevels(cat_tab$.))

#create numeric ent_tb col
syl_nums <- vector()
for(syl in ent_tb$syl) {
  syl_split <- syl %>% strsplit("_") %>% unlist()
  if(syl_split[1] == "final") {
    syl_nums <- c(syl_nums, 100) #assign 100 to ensure it is never accidentally captured
  } else {
    syl_nums <- c(syl_nums, as.numeric(syl_split[1]))
  }
}
ent_tb <- ent_tb %>% mutate(syl_num = syl_nums)
highest_num <- sort(syl_nums,partial=length(syl_nums)-1)[length(syl_nums)-1]

# produce sum entropy
entropy_col <- vector()
for (cat in tab_cats) {
  # get number of syllables in word
  cat_split <- cat %>% strsplit("_") %>% unlist()
  cat_num <- cat_split[2] %>% as.numeric()
  
  this_ent_tb <- ent_tb[ent_tb$syl_num < cat_num,]
  # remove last two rows and add final_nucleus. Unless
  # cat_num is equal to the highest number excluding 100
  row_num <- dim(this_ent_tb)[1]
  if (cat_num == highest_num) {
    this_ent_tb <- this_ent_tb[1:row_num-1,]
    this_ent_tb <- rbind(this_ent_tb, ent_tb[grepl("final", ent_tb$syl),])
  } else {
    this_ent_tb <- this_ent_tb[1:(row_num-2),]     
    this_ent_tb <- rbind(this_ent_tb, ent_tb[grepl("final", ent_tb$syl),])
  }
  entropy_col <- c(entropy_col, sum(this_ent_tb$entropy))
}
cat_tab <- cat_tab %>% mutate(sum_entropy = entropy_col)

# create plot with unique vowel count values
vowel_counts <- vector()
for (cat in tab_cats) {
  cat_split <- cat %>% strsplit("_") %>% unlist()
  vowel_counts <- c(vowel_counts, as.numeric(cat_split[2]))
}
vc_tab <- cbind(vowel_counts, cat_tab$sum_entropy) %>% data.frame()
vc_tab <- vc_tab[!duplicated(vc_tab),]
vc_tab$vowel_counts <- paste0(vc_tab$vowel_counts, " Vowels")
vc_tab$vowel_counts[1] <- vc_tab$vowel_counts[1] %>% stri_replace_all_regex("s$", "")

ent_gg <- ggplot(vc_tab, aes(x = vowel_counts, y = V2)) + 
  geom_histogram(stat = "identity") + 
  theme(text = element_text(size=10),
  axis.text.x = element_text(angle=90, hjust=1))  + 
  scale_x_discrete(limits = vc_tab$vowel_counts) + 
  xlab("Syllable") + 
  ylab("Shannon Entropy")
ggsave(paste0(args[1], "\\r_plots\\vowel_count_entropy.png"))
write_csv(cat_tab, paste0(args[1], "\\r_tables\\category_frequencies_with_sum_entropy.csv"))

# STEP 4: Produce syllable templates
syl_temps <- sur_tab$lexeme %>% 
  stri_replace_all_fixed(".", "") %>% 
  stri_replace_all_regex("[\u0259\u0250iu]", "V") %>% 
  stri_replace_all_regex("[^\u0259\u0250iuV:]+", "C") %>%
  table() %>%
  data.frame(stringsAsFactors = F) %>%
  mutate(proport = Freq / sum(Freq),
         num_syls = stri_count_fixed(., "V"))
syl_temps$. <- syl_temps$. %>% as.character()
# create summarised set
syl_sizes <- syl_temps$num_syls %>% unique()
for (syl_size in syl_sizes) {
  syl_set <- syl_temps[syl_temps$num_syls == syl_size,]
  in_row <- c("Total", sum(as.numeric(syl_set$Freq)), sum(as.numeric(syl_set$proport)), syl_set$num_syls[1])
  syl_temps[nrow(syl_temps)+1,] <- in_row
}
# save
write_csv(syl_temps, paste0(args[1], "\\r_tables\\syl_templates.csv"))

# STEP 5: Produce 10 lowest mean surprisals and 10 highest mean surprisals in lexicon (removing duplicates)
sur_tab_uniq <- sur_tab[!duplicated(sur_tab$lexeme),]
sur_tab_uniq <- sur_tab_uniq[order(sur_tab_uniq$mean_surprisal),]
  #get 10 top rows and 10 bottom rows
lowest_surs <- sur_tab_uniq[1:10,]
highest_surs <- sur_tab_uniq[(nrow(sur_tab_uniq)-9):nrow(sur_tab_uniq),]
out_surs <- bind_rows(lowest_surs, highest_surs)
write_csv(out_surs, paste0(args[1], "\\r_tables\\highest_lowest_surs_tab.csv"))
          
# STEP 6: Produce output statements for statistics relevant to K. phonotactics
  # Number of vowel-initial forms with proportion
paste0("Beginning with a vowel: ", length(sur_tab$cat[grepl("V", sur_tab$cat)]), "/", length(sur_tab$cat), "(", length(sur_tab$cat[grepl("V", sur_tab$cat)]) / length(sur_tab$cat), ")")
paste0("Beginning with low vowel \u0250: ", length(sur_tab$lexeme[grepl("^\u0250", sur_tab$lexeme)]), "(", length(sur_tab$lexeme[grepl("^\u0250", sur_tab$lexeme)]) / length(sur_tab$lexeme), ")")
paste0("Beginning with schwa \u0259: ", length(sur_tab$lexeme[grepl("^\u0259", sur_tab$lexeme)]), "(", length(sur_tab$lexeme[grepl("^\u0259", sur_tab$lexeme)]) / length(sur_tab$lexeme), ")")
paste0("Beginning with i: ", length(sur_tab$lexeme[grepl("^i", sur_tab$lexeme)]), "(", length(sur_tab$lexeme[grepl("^i", sur_tab$lexeme)]) / length(sur_tab$lexeme), ")")
paste0("Beginning with u: ", length(sur_tab$lexeme[grepl("^u", sur_tab$lexeme)]), "(", length(sur_tab$lexeme[grepl("^u", sur_tab$lexeme)]) / length(sur_tab$lexeme), ")")
paste0("Beginning with a consonant: ", length(sur_tab$cat[grepl("C", sur_tab$cat)]), "/", length(sur_tab$cat), "(", length(sur_tab$cat[grepl("C", sur_tab$cat)]) / length(sur_tab$cat), ")")
positional_configs <- read_csv(paste0(args[1], "\\py_outputs\\phonotactic_fqs.csv"))
# Initial phonotactics
initial_row <- positional_configs[1,]
initial_row <- initial_row[2:length(initial_row)] %>% as.numeric()
seg_set <- colnames(positional_configs)
seg_set <- seg_set[2:length(seg_set)]
initial_conss <- seg_set[initial_row > 0]
initial_conss <- initial_conss[!grepl("0", initial_conss)]
paste0("Number of initial consonantal configurations: ", length(initial_conss))
paste0("Number of singleton consonantal configurations: ", length(initial_conss[str_length(initial_conss) < 2]))

# Final phonotactics
last_row <- positional_configs[length(positional_configs$syllable)-1, 2:length(positional_configs)] %>% as.numeric()
last_nucleus <- seg_set[last_row > 0]
paste0("Frequency of final schwa ", last_row[seg_set == "\u0259"], " (", last_row[seg_set == "\u0259"]/sum(last_row), ")")
paste0("Frequency of final u ", last_row[seg_set == "u"], " (", last_row[seg_set == "u"]/sum(last_row), ")")
paste0("Frequency of final u: ", last_row[seg_set == "u:"], " (", last_row[seg_set == "u:"]/sum(last_row), ")")
paste0("Frequency of final i ", last_row[seg_set == "i"], " (", last_row[seg_set == "i"]/sum(last_row), ")")
paste0("Frequency of final i: ", last_row[seg_set == "i:"], " (", last_row[seg_set == "i:"]/sum(last_row), ")")

