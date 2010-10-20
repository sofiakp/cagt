
import sys
sys.path.append('../../')
import gzip
import pickle

from parameters import *
from src.filenames import *


def get_genes_from_gencode_file():
	gencode_filename = make_gencode_filename()
	gencode_rows = map(lambda row: row.split("\t"), gzip.open(gencode_filename,"r").readlines())
	print "len(gencode_rows):", len(gencode_rows)
	gencode_transcript_rows =\
	filter(lambda row: len(row) >= 9 and row[2]=="transcript", gencode_rows)

	gencode_genes = {}
	for row in gencode_transcript_rows:
		chr = row[0]
		entry = {}
		entry["start"] = int(row[3])
		entry["end"] = int(row[4])
		entry["strand"] = row[6]
		info = row[8].split(';')
		entry["type"] = info[5].split()[1]
		if True:
#		if entry["type"] == '"protein_coding"':
			if not gencode_genes.has_key(chr):
				gencode_genes[chr] = []
			gencode_genes[chr].append(entry)
	
	return gencode_genes


def proximity_cluster(clustering_info, peak_tag, gencode_genes):
	peaks = clustering_info.peaks[peak_tag]
		
	# 0: gene distal
	# 1: inside a gene
	# 2: upstream of a gene within gene_proximity_distance bp, positive direction
	# 3: upstream of a gene within gene_proximity_distance bp, negative direction
	
	def find_gene_proximity(p):
		chr = peaks[p][0]
		pos = peaks[p][1]
		
		nearest_gene_index = -1
		nearest_gene_distance = float("infinity")
		nearest_gene_strand = "+"
		if not gencode_genes.has_key(chr):
			return 0
		for g in range(len(gencode_genes[chr])):
			gene_upstream_end = gencode_genes[chr][g]['start']
			gene_downstream_end = gencode_genes[chr][g]['end']
			strand = gencode_genes[chr][g]['strand']
			gene_type = gencode_genes[chr][g]['type']
#			if pos >= gene_upstream_end+10000 and pos <= gene_downstream_end-10000:
#				return 1
			gene_start = gene_upstream_end if strand=="+" else gene_downstream_end
			if abs(pos - gene_start) < nearest_gene_distance:
				nearest_gene_index = g
				nearest_gene_distance = abs(pos - gene_start)
				nearest_gene_strand = strand
		if nearest_gene_distance >= gene_proximity_distance:
			return 0
		elif nearest_gene_strand == '+':
			return 2
		elif nearest_gene_strand == '-':
			return 3
		else:
			raise "something went wrong here"
	
	gene_proximity_assignments = map(find_gene_proximity, range(len(peaks)))
	
	print "set(gene_proximity_assignments):", set(gene_proximity_assignments)
	print "proximity type counts:", map(lambda t: [t,len(filter(lambda a: a==t, gene_proximity_assignments))] , list(set(gene_proximity_assignments)))
	return gene_proximity_assignments


def gene_proximity_cluster_all(clustering_info):
	proximity_assignments = {}

	print "getting gencode genes..."
	t0 = time()
#	gencode_genes = get_genes_from_gencode_file()
#	pickle.dump(gencode_genes, open("tmp/tmp_gencode_genes","w"))
	gencode_genes = pickle.load(open("tmp/tmp_gencode_genes","r"))
	print "time to get gencode genes:", time()-t0

	print "total bp covered by gencode genes:", sum(map(lambda chr: sum(map(lambda entry: entry["end"]-entry["start"], gencode_genes[chr])), gencode_genes.keys()))

	for peak_tag in peak_tags:
		print "starting", peak_tag, "..."
		proximity_assignments[peak_tag] = proximity_cluster(clustering_info, peak_tag, gencode_genes)
	return proximity_assignments












