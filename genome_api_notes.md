# Genome API

Data model

    +-------+   +--------+   +-------------+                  
    | Genome+-> |Features+-->+Feature      +-+----->Amino+acid
    +----+--+   +--------+   |sequences    | |                
         |                   +------+------+ |                
         |                          |        +----->DNA       
         |                          |                         
     +---+-------+                  |                         
     | ContigSet +<-----------------+                         
     +-----------+    position info                           

## Taxonomy

* lineage - list of descriptors
* taxonomy - string
* taxonomic id - string

## Sequence

* get_contig(id, start?, stop?, strand?)
* list of contigs
* list of DNA or AA features, e.g. get_feature_dna(feature_id)

## Annotation

???

## Metadata

* quality score. multidimensional
* circular (true, false, unknown)
* type: 'draft' or 'finished'
* reference
* date of origination
* external resource (see identifiers)
* percent assembled
* number of contigs