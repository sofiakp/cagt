
import sys
sys.path.append('../../')
import gzip
import pickle

from src.filenames import *

GENE_DISTAL = 0
INSIDE_GENE = 1
UPSTREAM_POS = 2
UPSTREAM_NEG = 3


def get_genes_from_gencode_file(output_folder, gene_list_filename):
  print "starting get_genes_from_gencode_file..."
  print "gene_list_filename:", gene_list_filename
  gene_data = open(gene_list_filename,"r").readlines()
  print "gene_data[5]:", gene_data[5]
  gene_rows = map(lambda row: row.split(), gene_data)
  print "len(gene_rows):", len(gene_rows)
  # gene_transcript_rows =\
  # filter(lambda row: len(row) >= 9 and row[2]=="transcript", gene_rows)

  genes = {}
  genes['total_num_bases'] = 0
  genes['num_genes'] = 0
  genes['num_pos_genes'] = 0
  genes['num_neg_genes'] = 0
  for row in gene_rows:
    chr = row[0]
    entry = {}
    entry["start"] = int(row[1])
    entry["end"] = int(row[2])
    entry["strand"] = row[5]
    # info = row[8].split(';')
    # entry["type"] = info[5].split()[1]
    if True:
#   if entry["type"] == '"protein_coding"':
      if not genes.has_key(chr):
        genes[chr] = []
      genes[chr].append(entry)

    genes['total_num_bases'] += entry['end'] - entry['start']
    genes['num_genes'] += 1
    if entry['strand'] == '+':
      genes['num_pos_genes'] += 1
    elif entry['strand'] == '-':
      genes['num_neg_genes'] += 1
    else:
      print entry['strand']
      raise Exception("something went wrong here")


  genes_filename = make_genes_filename(output_folder)
  pickle.dump(genes, open(genes_filename,"w"))
  # return gencode_genes


def proximity_cluster(clustering_info):
  profiles_info = clustering_info.profiles_info
  genome_length = profiles_info.args.genome_length
  gene_proximity_distance = profiles_info.args.gene_proximity_distance

  peaks = clustering_info.peaks

  genes_filename = make_genes_filename(profiles_info.output_folder)
  genes = pickle.load(open(genes_filename, "r"))


  def find_gene_proximity(p):
    chr = peaks[p][0]
    pos = peaks[p][1]

    nearest_gene_index = -1
    nearest_gene_distance = float("infinity")
    nearest_gene_strand = "+"
    if not genes.has_key(chr):
      return GENE_DISTAL
    for g in range(len(genes[chr])):
      gene_upstream_end = genes[chr][g]['start']
      gene_downstream_end = genes[chr][g]['end']
      strand = genes[chr][g]['strand']
      # gene_type = genes[chr][g]['type']
      if pos >= gene_upstream_end and pos <= gene_downstream_end:
        return INSIDE_GENE
      if strand=="+":
        gene_start = gene_upstream_end
      else:
        gene_start = gene_downstream_end
      if abs(pos - gene_start) < nearest_gene_distance:
        nearest_gene_index = g
        nearest_gene_distance = abs(pos - gene_start)
        nearest_gene_strand = strand
    if nearest_gene_distance >= gene_proximity_distance:
      return GENE_DISTAL
    elif nearest_gene_strand == '+':
      return UPSTREAM_POS
    elif nearest_gene_strand == '-':
      return UPSTREAM_NEG
    else:
      raise "something went wrong here"

  gene_proximity_assignments = map(find_gene_proximity, range(len(peaks)))

  # clusters = {GENE_DISTAL: [], INSIDE_GENE: [], UPSTREAM_POS: [], UPSTREAM_NEG: []}
  # for i in range(len(peaks)):
  #   clusters[gene_proximity_assignments[i]].append(i)

  # print genes['total_num_bases']
  # print genes['num_genes']
  # print genes['num_pos_genes']
  # print genes['num_neg_genes']
  expected = {}
  expected[INSIDE_GENE] = float(genes['total_num_bases'])/genome_length
  expected[UPSTREAM_POS] = float(genes['num_pos_genes']*gene_proximity_distance)/genome_length
  expected[UPSTREAM_NEG] = float(genes['num_neg_genes']*gene_proximity_distance)/genome_length
  expected[GENE_DISTAL] = 1 - expected[INSIDE_GENE] - expected[UPSTREAM_POS] - expected[UPSTREAM_NEG]

  # print "set(gene_proximity_assignments):", set(gene_proximity_assignments)
  # counts_list = map(lambda t: [t,len(filter(lambda a: a==t, gene_proximity_assignments))] , list(set(gene_proximity_assignments)))
  # counts = {GENE_DISTAL: 0, INSIDE_GENE: 0, UPSTREAM_POS: 0, UPSTREAM_NEG: 0}
  # for c in counts_list:
  #   counts[c[0]] = c[1]
  # print "proximity type counts:", counts
  # print expected

  return (gene_proximity_assignments, expected)

  # pickle.dump((gene_proximity_assignments, expected), open(make_gene_proximity_filename(profiles_info),"w"))





# def gene_proximity_cluster_all(clustering_info):
#   proximity_assignments = {}
#
#   print "getting gencode genes..."
#   t0 = time()
# # gencode_genes = get_genes_from_gencode_file()
# # pickle.dump(gencode_genes, open("tmp/tmp_gencode_genes","w"))
#   gencode_genes = pickle.load(open("tmp/tmp_gencode_genes","r"))
#   print "time to get gencode genes:", time()-t0
#
#   print "total bp covered by gencode genes:", sum(map(lambda chr: sum(map(lambda entry: entry["end"]-entry["start"], gencode_genes[chr])), gencode_genes.keys()))
#
#   for peak_tag in peak_tags:
#     print "starting", peak_tag, "..."
#     proximity_assignments[peak_tag] = proximity_cluster(clustering_info, peak_tag, gencode_genes)
#   return proximity_assignments
#











