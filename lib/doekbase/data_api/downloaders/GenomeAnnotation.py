"""
GenomeAnnotation to GenBank downloader.


Usage::

    from doekbase.data_api.downloaders import GenomeAnnotation

    # Genome annotation
    obj = genome.GenomeConverter(ref='6052/40/1', kbase_instance='ci')
    new_obj_ref = obj.convert(target_workspace_id)
    # NOTE: side-effect of this conversion is to also create a ContigSet
    # object, by converting the associated Assembly, in the same workspace.

    # Assembly
    obj = genome.AssemblyConverter(ref='6052/31/1', kbase_instance='ci')
    new_obj_ref = obj.convert(target_workspace_id)
"""
__author__ = 'Marcin Joachimiak <mjoachimiak@lbl.gov>'
__date__ = '6/10/16'

# Stdlib
import hashlib
import itertools
import logging
import os
import string
# Local
from . import base
from .base import DEBUG, INFO, WARN, ERROR
from doekbase.data_api.pbar import PBar

#from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
#from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
from doekbase.workspace.client import Workspace
from doekbase.data_api.core import ObjectAPI
from doekbase.handle.Client import AbstractHandle as handleClient


###example method, needs refactoring
def downloadAsGBK():

  genome_ref = '6838/Shewanella_oneidensis_MR1'#Pseudomonas_syringae_pv_tomato_strDC3000'
  #'7364/20'#
  #genome_ref = 'ReferenceGenomeAnnotations/kb|g.440'#ReferenceGenomeAnnotations/kb|g.166819'#6838/146'#ReferenceGenomeAnnotationsV5/kb|g.166819
  #ReferenceGenomeAnnotations/kb%7Cg.440
  #ecoli: 6838/106/1

  ga_api = GenomeAnnotationAPI(services, token=token, ref=genome_ref)

  tax_api = ga_api.get_taxon()

  asm_api = ga_api.get_assembly()

  genome_name = str(ga_api.get_id())

  print genome_name

  valid_chars = "-_.(){0}{1}".format(string.ascii_letters, string.digits)
  temp_file_name = ""
  filename_chars = list()

  for character in genome_name:
      if character in valid_chars:
          filename_chars.append(character)
      else:
          filename_chars.append("_")

  if len(filename_chars) == 0:
      temp_file_name = "GenBankFile"
  else:
      temp_file_name = "".join(filename_chars)+".gbk"

  output_file = os.path.join(working_directory,temp_file_name)

  contig_ids = asm_api.get_contig_ids()
  contig_lengths = asm_api.get_contig_lengths(contig_ids)

  full_tax = tax_api.get_scientific_lineage()


  do_contig_ids = contig_ids#['kb|g.166819.c.17']#contig_ids

  with open(output_file, "w") as out_file:

      #create per-contig section in gbk file
      for contig_id in do_contig_ids:

          start=1
          stop=contig_lengths[contig_id]

          print contig_id
          writeHeader(contig_id, contig_lengths, full_tax, tax_api, out_file)
          regions = []
          contig_add = {"contig_id": contig_id, "start": start, "length": stop-start, "strand": "+"}
          contig_add2 = {"contig_id": contig_id, "start": stop, "length": stop-start, "strand": "-"}        
          regions.append(contig_add)
          regions.append(contig_add2)

          writeFeaturesOrdered(ga_api, regions, out_file)
          
          ###TODO write contig sequence
          writeContig(contig_id, out_file)
          break

  out_file.close()

  print "done "+output_file




def writeHeader(contig_id, contig_lengths, fulltax, tax_api, out_file):
    out_file.write("LOCUS       " + contig_id + "             " + str(contig_lengths[contig_id]) + " bp    " +"DNA\n")
    sn = tax_api.get_scientific_name()
    out_file.write("DEFINITION  " + sn + " genome.\n")
    out_file.write("SOURCE      " + sn + "\n")
    out_file.write("  ORGANISM  " + sn + "\n")

    fulltaxstring = ';'.join(full_tax)
    print full_tax

    if (full_tax):
        formatTax = ""

        counter = 0
        index = 0
        while (index < len(fulltax)):
            formatTax = formatTax+(fulltax[index])
            if (index < len(fulltax) - 1):
                formatTax=formatTax+(" ")
            counter=counter+ len(fulltax[index]) + 1
            index=index+1

            if (counter >= 65 or len(fulltaxstring) < 80):
                formatTax = formatTax+("\n")
                formatTax = formatTax+("            ")
                counter = 0

        out_file.write("            " + formatTax + ".\n")

    out_file.write("COMMENT     Exported from the DOE KnowledgeBase.\n")

    out_file.write("FEATURES             Location/Qualifiers\n")
    out_file.write("     source          1.." + str(contig_lengths[contig_id]) + "\n")
    out_file.write("                     /organism=\"" + tax_api.get_scientific_name() + "\"\n")
    out_file.write("                     /mol_type=\"DNA\"\n") 


def writeFeaturesOrdered(ga_api, regions, out_file):
    types = ga_api.get_feature_types()    
    print types
    
    print "Getting feature ids"
    feature_ids = ga_api.get_feature_ids(filters={"region_list":regions,"type_list":types})    
    #print feature_ids
                    
    print "Getting proteins"
    proteins = ga_api.get_proteins()
    
    all_ids = []
    for t in types:
        all_ids = all_ids + feature_ids['by_type'][t] 
    #print all_ids
    
    print "Getting all features for contig"
    features = ga_api.get_features(all_ids)#['by_type']['gene'])
    numfeat = str(len(features))
    print "number of features "+numfeat
    
    if('gene' in feature_ids['by_type']):
        cds_by_gene = ga_api.get_cds_by_gene(feature_ids['by_type']['gene'])
    
        cds_by_gene_keys = cds_by_gene.keys()
        print "cds_by_gene "
        print cds_by_gene[cds_by_gene_keys[1]]
    
    mrna_by_cds = ga_api.get_mrna_by_cds(feature_ids['by_type']['CDS']);
    
    mrna_by_cds_keys = mrna_by_cds.keys()
    print "mrna_by_cds "
    print mrna_by_cds[mrna_by_cds_keys[1]]   

    count = 0
    for feat in features:
        if features[feat]['feature_type'] == 'gene':
            count = count +1
            print feat+"\t"+features[feat]['feature_type']
            print features[feat]
            function = features[feat]['feature_function']
            allfunction = function.split(" ")
            print "FUNCTION "+function
            format_function = formatAnnotation(function, allfunction, 48, 58)

            #print features[feat]
            curstart = features[feat]['feature_locations'][0]['start']
            curstop = curstart + features[feat]['feature_locations'][0]['length']
            out_file.write("     gene            "+str(curstart)+".."+str(curstop)+"\n")
            out_file.write("                     /gene=\"" + feat + "\"\n")

            aliases = features[feat]['feature_aliases']
            if(aliases is not None and len(aliases)>0):
                print "ALIASES "+feat
                for k, v in aliases.iteritems():
                    print k, v
                
                #aliases_keys = aliases.keys()
                #print aliases_keys[0]
                #print aliases.get(aliases_keys[0])
                #print "aliases 1 :"+aliases_keys[0]+"\t"+aliases.get(aliases_keys[0])[0]

                ###TODO handle different alias cases and types
                for s in aliases :
                    #print s
                    #print aliases[s]
                    if(aliases[s][0].find("Genbank ") == -1):
                        out_file.write("                     /db_xref=\""+aliases[s][0]+":" + s + "\"\n")
                    else:
                        key = aliases[s][0].replace("Genbank ","")
                        #key_list = key.split(" ", 1)
                        #print key
                        out_file.write("                     /"+key+"=\"" + s + "\"\n")



            #     gene            3631..5899
            #             /gene="NAC001"
            #             /locus_tag="AT1G01010"
            #             /gene_synonym="ANAC001; NAC domain containing protein 1;
            #             NAC001; T25K16.1; T25K16_1"
            #             /db_xref="GeneID:839580"

            #try:
            if feat in cds_by_gene :
                cds_id = cds_by_gene[feat]

                print "CDS"
                print cds_id
                for cds in cds_id:                

                    mrna_id = mrna_by_cds[cds]
                    if mrna_id is not None:
                        print "mRNA " + mrna_id
                        functionmRNA = features[mrna_id]['feature_function']
                        print "FUNCTION mRNA " + functionmRNA
                        allfunctionmRNA = functionmRNA.split(" ")
                        format_functionmRNA = formatAnnotation(functionmRNA, allfunctionmRNA, 48, 58)

                        out_file.write("     mRNA            ")
                        writeLocation(features[mrna_id]['feature_locations'], out_file)

                        out_file.write("                     /gene=\"" + mrna_id + "\"\n")
                        if format_function is not None:
                            out_file.write("                     /function=\"" + format_function)
                        else:
                            out_file.write("                     /function=\"\"\n")

                        aliases = features[mrna_id]['feature_aliases']
                        if(aliases is not None and len(aliases)>0):
                            for s in aliases :
                                if(aliases[s][0].find("Genbank ") == -1):
                                    out_file.write("                     /db_xref=\""+aliases[s][0]+":" + s + "\"\n")
                                else:
                                    key = aliases[s][0].replace("Genbank ","")
                                    #key_list = key.split(" ", 1)
                                    #print key
                                    out_file.write("                     /"+key+"=\"" + s + "\"\n")

                    # mRNA            complement(join(5928..6263,6437..7069,7157..7232,
                    # 7384..7450,7564..7649,7762..7835,7942..7987,8236..8325,
                    # 8417..8464,8571..8737))
                    # /gene="ARV1"
                    # /locus_tag="AT1G01020"
                    # /gene_synonym="T25K16.2; T25K16_2"
                    # /product="protein Arv1"
                    # /inference="Similar to DNA sequence:INSD:AY758070.1"
                    # /inference="Similar to RNA sequence,
                    # EST:INSD:EH846835.1,INSD:AU227271.1,INSD:EG512767.1,
                    # INSD:EG452794.1,INSD:EL102675.1,INSD:EG512768.1,
                    # INSD:EH959539.1"
                    # /transcript_id="NM_099984.5"
                    # /db_xref="GI:240253989"

                    print "CDS "+ cds
                    print features[cds]['feature_function']
                    allfunction = function.split(" ")
                    format_function = formatAnnotation(function, allfunction, 48, 58)
                    print "format_function "+format_function

                    out_file.write("     CDS             ")
                    writeLocation(features[cds]['feature_locations'], out_file)
                    out_file.write("                     /gene=\"" + cds + "\"\n")

                    #out_file.write("                     /note=\"" + formatNote)
                    #out_file.write("                     /codon_start=1\n")
                    #out_file.write"                     /transl_table=11\n")
                    #out_file.write("                     /product=\"" + cds + "\"\n")
                    if format_function is not None:
                        out_file.write("                     /function=\"" + format_function)
                    else:
                        out_file.write("                     /function=\"\"\n")

                    out_file.write("                     /protein_id=\"" + cds + "\"\n")

                    aliases = features[cds]['feature_aliases']
                    #print "aliases 1 :"+aliases.keys()[1]

                    ###TODO handle different alias cases and types
                    if (len(aliases)>0) :
                        for s in aliases :
                            #print s
                            if(aliases[s][0].find("Genbank ") == -1):
                                out_file.write("                     /db_xref=\""+aliases[s][0]+":" + s + "\"\n")
                            else:
                                key = aliases[s][0].replace("Genbank ","")
                                #key_list = key.split(" ", 1)
                                #print key
                                out_file.write("                     /"+key+"=\"" + s + "\"\n")


                    getprot = proteins.get(cds)
                    if getprot is not None:
                        protein_translation = proteins[cds]['protein_amino_acid_sequence']
                        if(protein_translation is None):
                            protein_translation_final = ""
                        else:
                            #print features[cds_id]
                            #print features[cds]
                            #print "protein_translation "+protein_translation
                            protein_translation_final = formatString(protein_translation, 44, 58)

                        print feat +"\tprotein_translation "+ protein_translation_final

                        out_file.write("                     /translation=\"" + protein_translation_final);

                        #     CDS             complement(join(6915..7069,7157..7232,7384..7450,
                        # 7564..7649,7762..7835,7942..7987,8236..8325,8417..8464,
                        # 8571..8666))
                        # /gene="ARV1"
                        # /locus_tag="AT1G01020"
                        # /gene_synonym="T25K16.2; T25K16_2"
                        # /inference="Similar to DNA sequence:INSD:AY758070.1"
                        # /inference="Similar to RNA sequence,
                        # EST:INSD:EH846835.1,INSD:AU227271.1,INSD:EG512767.1,
                        # INSD:EG452794.1,INSD:EL102675.1,INSD:EG512768.1,
                        # INSD:EH959539.1"
                        # /note="ARV1; CONTAINS InterPro DOMAIN/s: Arv1-like protein
                        # (InterPro:IPR007290); BEST Arabidopsis thaliana protein
                        # match is: Arv1-like protein (TAIR:AT4G01510.1); Has 311
                        # Blast hits to 311 proteins in 154 species: Archae - 0;
                        # Bacteria - 0; Metazoa - 110; Fungi - 115; Plants - 42;
                        # Viruses - 0; Other Eukaryotes - 44 (source: NCBI BLink)."
                        # /codon_start=1
                        # /product="protein Arv1"
                        # /protein_id="NP_171610.2"
                        # /db_xref="GI:79332834"
                        # /db_xref="GeneID:839569"
                        # /db_xref="TAIR:AT1G01020"
                        # /translation="MAASEHRCVGCGFRVKSLFIQYSPGNIRLMKCGNCKEVADEYIE
                        # CERMIIFIDLILHRPKVYRHVLYNAINPATVNIQHLLWKLVFAYLLLDCYRSLLLRKS
                        # DEESSFSDSPVLLSIKVLIGVLSANAAFIISFAIATKGLLNEVSRRREIMLGIFISSY
                        # FKIFLLAMLVWEFPMSVIFFVDILLLTSNSMALKVMTESTMTRCIAVCLIAHLIRFLV
                        # GQIFEPTIFLIQIGSLLQYMSYFFRIV"

def writeLocation(feature_locations, out_file):
  added = 0
  complement = 0
  isJoin = 0
  numloc = len(feature_locations)
  for n in range(0, numloc) :
      now4 = feature_locations[n]
      if (added == 0 and now4['strand'] == "-") :
          out_file.write("complement(")
          complement = 1

      if (len(feature_locations) > 1) :
          if (added == 0):
              out_file.write("join(")
          isJoin = 1
      
      ###TODO output location info
      if (complement == 0):
          out_file.write(str(now4['start']) + ".." + str(now4['start'] + now4['length'] - 1))
      else :
          out_file.write(str(now4['start'] - (now4['length'] + 1)) + ".." + str(now4['start']))

      if (numloc > 0 and n < (numloc - 1)) :
          out_file.write(",")
      added = added + 1

  if (complement == 1 and isJoin == 1):
      out_file.write("))\n")
  elif (complement ==1  or isJoin == 1):
      out_file.write(")\n")
  else:
      out_file.write("\n")

def writeContig(contig_id, outfile) :
  print "getting contig"
  contigdata = asm_api.get_contigs([contig_id])
  print contigdata
  print contigdata.keys()
  outfile.write(formatDNASequence(contigdata[contig_id]['sequence'], 10, 60))
  outfile.write("//\n")


def formatAnnotation(function,  allfunction, first, nexta) :
  format_function = ""

  isfirst = 1

  #print "formatAnnotation "+ function+"\t"+str(len(function)) +"\t"+ str(first)+"\t"+str(len(allfunction))

  if (len(function) < first) :
      format_function = format_function+(function + "\"\n")
      #print "FIRST format_function "+ format_function
  else :
      counter2 = 0
      index2 = 0
      while (index2 < len(allfunction)) :
          #print "format_function "+ str(counter2) +"\t"+ format_function
          counter2 = counter2 + len(allfunction[index2]) + 1

          if (((isfirst == 1 and counter2 >= first) or counter2 >= nexta)) :
              
              if (isfirst == 1):
                  isfirst = 0;

              if (index2 < len(allfunction)) :
                  format_function = format_function+("\n")
                  format_function = format_function+("                     ")
                  format_function = format_function+(allfunction[index2])
                  counter2 = len(allfunction[index2])
                  if (index2 < len(allfunction) - 1):
                      counter2 = counter2 + 1
                      format_function = format_function+(" ")
                  else:
                      format_function = format_function+("\"\n")
              
          else :
              if (index2 < len(allfunction)) :
                  format_function = format_function+(allfunction[index2])
                  if (index2 < len(allfunction) - 1) :
                      counter2 = counter2 + 1
                      format_function = format_function + (" ")
                  else:
                      format_function = format_function + ("\"\n")
              else:
                  format_function =  format_function+ ("\"\n")
          
          index2 = index2 + 1
      
  if (len(format_function) == 0 or format_function is None) :
      format_function = "\"\n"
      
  formatindex = format_function.find("\"\n")    

  if (formatindex != len(format_function) - 2):
      format_function = format_function+("\"\n")
      
  if(len(format_function) == 0):
      format_function = ""
  #print "formatAnnotation end "+ format_function
  return format_function


###formats a string into lines of given length (first line can be different)
def formatString(s, one, two) :
  s = s.replace("\"", "")
  out = ""
  first = 1
  counter = 0
  start = 0
  while start < len(s) :
      if (first == 1) :
          lista = [len(s), start+one]
          last = min(lista)
          isLast = 0
          if (last == len(s)):
              isLast = 1
          out = out +(s[start : last])
          if (isLast == 1):
              out = out +("\"\n")
          else :
              out = out+("\n")
          
          first = 0;
          start = start+one;
      else :
          lista = [len(s), start+two]
          last = min(lista)
          out = out + ("                     ")
          isLast = 0
          if (last == len(s)):
              isLast = 1
          out = out+(s[start: last])           
          start = start + two
          if (isLast == 1) :
              out = out +("\"\n")            
          else:
              out = out +("\n");
      counter=counter+1
      
  if len(out) ==0 or out is None:
      out = "\"\n"

  return out


def formatDNASequence(s, charnum, linenum) :
  out = "";

  #out += "        1 tctcgcagag ttcttttttg tattaacaaa cccaaaaccc atagaattta atgaacccaa\n"

  out = out + ("        1 ")
  index = 1
  counter = 0
  for last in range( 0, len(s)):
      end = min(len(s), last + charnum)
      out = out+s[last: end]
      last = last+ charnum
      counter = counter+1
      if (counter == 6 and len(s) > end) :
          out = out +("\n")
          index = index+ 60
          indexStr = str(index)
          length = len(indexStr)
          out = out +(" "*(9-length) + indexStr + " ")
          counter = 0
      else :
          out = out+(" ")
  if (out[len(out) - 1] == (' ')):
      out = out[:len(out) - 1]
  out = out+("\n")
  return out
