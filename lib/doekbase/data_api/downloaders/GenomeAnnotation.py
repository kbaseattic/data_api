"""
GenomeAnnotation to GenBank file conversion.

Usage::

    from doekbase.data_api.downloaders import GenomeAnnotation

    GenomeAnnotation.downloadAsGBK(genome_ref='6052/40/1',
                                   services={
                                       "workspace_service_url": "",
                                       "shock_service_url": "",
                                       "handle_service_url": ""
                                   },
                                   token=os.environ["KB_AUTH_TOKEN"],
                                   output_file='sample.gbk',
                                   working_dir='.')
"""
__author__ = 'Marcin Joachimiak <mjoachimiak@lbl.gov>'
__date__ = '6/10/16'

# Stdlib
import os
import string
import StringIO
# Local
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI

#@profile
###example method, needs refactoring
def downloadAsGBK(genome_ref=None, services=None, token=None, output_file=None, working_dir=None):
    ga_api = GenomeAnnotationAPI(services, token=token, ref=genome_ref)
    tax_api = ga_api.get_taxon()
    asm_api = ga_api.get_assembly()

    genome_name = str(ga_api.get_id())

    print genome_name

    contig_ids = asm_api.get_contig_ids()
    contig_lengths = asm_api.get_contig_lengths(contig_ids)
    print contig_ids

    full_tax = tax_api.get_scientific_lineage()

    valid_chars = "-_.(){0}{1}".format(string.ascii_letters, string.digits)
    filename_chars = list()

    if output_file is None:
        for character in genome_name:
            if character in valid_chars:
                filename_chars.append(character)
            else:
                filename_chars.append("_")

                output_file = "".join(filename_chars) + ".gbk"

    outpath = os.path.join(working_dir, output_file)

    start = 1
    with open(outpath, "w") as out_file:
        # create per-contig section in gbk file
        for contig_id in contig_ids:
            print contig_id
            stop = contig_lengths[contig_id]

            writeHeader(contig_id, contig_lengths, full_tax, tax_api, out_file)

            regions = [
                {"contig_id": contig_id, "start": start, "length": stop - start, "strand": "+"},
                {"contig_id": contig_id, "start": stop, "length": stop - start, "strand": "-"}
            ]

            writeFeaturesOrdered(ga_api, regions, out_file)

            ###TODO write contig sequence
            writeContig(contig_id, out_file, asm_api)
            #break

def writeHeader(contig_id=None, contig_lengths=None, full_tax=None, tax_api=None, out_file=None):
    out_file.write("LOCUS{}{}{} bp   DNA\n".format(" " * 7, contig_id, " " * 13, contig_lengths[contig_id]))

    sn = tax_api.get_scientific_name()

    out_file.write("DEFINITION  {} genome.\n".format(sn))
    out_file.write("SOURCE      {}\n".format(sn))
    out_file.write("  ORGANISM  {}\n".format(sn))

    if full_tax:
        lineLength = 0
        hasNewline = False
        lineage = []
        for i in xrange(len(full_tax)):
            lineage.append(full_tax[i] + " ")

            lineLength += len(full_tax[i] + " ")
            if lineLength > 60:
                lineage.append("\n{}".format(" " * 12))
                lineLength = 0
                hasNewline = True

        if not hasNewline:
            lineage.append("\n{}".format(" " * 12))

        out_file.write("{}{}.\n".format(" " * 12, "".join(lineage)))

    out_file.write("COMMENT{}Exported from the DOE KnowledgeBase.\n".format(" " * 5))

    out_file.write("FEATURES{}Location/Qualifiers\n".format(" " * 13))
    out_file.write("{}source{}1..{}\n".format(" " * 5, " " * 10, contig_lengths[contig_id]))
    out_file.write("{}/organism=\"{}\"\n".format(" " * 21, tax_api.get_scientific_name()))
    out_file.write("{}/mol_type=\"DNA\"\n".format(" " * 21))


#@profile
def writeFeaturesOrdered(ga_api=None, regions=None, out_file=None):
    feature_ids = ga_api.get_feature_ids(filters={"region_list": regions})

    proteins = ga_api.get_proteins()

    all_ids = []
    for t in feature_ids['by_type']:
        all_ids.extend(feature_ids['by_type'][t])

    # print "Getting all features for contig"
    features = ga_api.get_features(all_ids)  # ['by_type']['gene'])

    if ('gene' in feature_ids['by_type']):
        cds_by_gene = ga_api.get_cds_by_gene(feature_ids['by_type']['gene'])

    mrna_by_cds = ga_api.get_mrna_by_cds(feature_ids['by_type']['CDS'])

    count = 0
    for feat in features:
        if features[feat]['feature_type'] == 'gene':
            count += 1
            function = features[feat]['feature_function']
            allfunction = function.split(" ")
            # what is the significance of 48 and 58 here?
            format_function = formatAnnotation(function, allfunction, 48, 58)

            curstart = features[feat]['feature_locations'][0]['start']
            curstop = curstart + features[feat]['feature_locations'][0]['length']

            out_file.write("{}gene{}{}..{}\n".format(" " * 5, " " * 12, curstart, curstop))
            out_file.write("{}/kbase_id=\"{}\"\n".format(" " * 21, feat))

            if format_function is not None:
                out_file.write("{}/function=\"{}".format(" " * 21, format_function))
            else:
                out_file.write("{}/function=\"\"\n".format(" " * 21))

            aliases = features[feat]['feature_aliases']

            if aliases is not None and len(aliases) > 0:
                # TODO handle different alias cases and types
                #     gene            3631..5899
                #             /gene="NAC001"
                #             /locus_tag="AT1G01010"
                #             /gene_synonym="ANAC001; NAC domain containing protein 1;
                #             NAC001; T25K16.1; T25K16_1"
                #             /db_xref="GeneID:839580"
                for s in aliases:
                    if (aliases[s][0].find("Genbank ") == -1):
                        out_file.write("{}/db_xref=\"{}:{}\"\n".format(" " * 21, aliases[s][0], s))
                    else:
                        key = aliases[s][0].replace("Genbank ", "")
                        out_file.write("{}/{}=\"{}\"\n".format(" " * 21, key, s))

            if feat in cds_by_gene:
                cds_id = cds_by_gene[feat]

                for cds in cds_id:
                    mrna_id = mrna_by_cds[cds]
                    if mrna_id is not None:
                        functionmRNA = features[mrna_id]['feature_function']
                        allfunctionmRNA = functionmRNA.split(" ")
                        format_functionmRNA = formatAnnotation(functionmRNA, allfunctionmRNA, 48, 58)

                        out_file.write("{}mRNA".format(" " * 5, " " * 12))
                        writeLocation(features[mrna_id]['feature_locations'], out_file)

                        out_file.write("{}/kbase_id=\"{}\"\n".format(" " * 21, mrna_id))

                        if format_functionmRNA is not None:
                            out_file.write("{}/function=\"{}".format(" " * 21, format_functionmRNA))
                        else:
                            out_file.write("{}/function=\"\"\n".format(" " * 21))

                        aliases = features[mrna_id]['feature_aliases']

                        if (aliases is not None and len(aliases) > 0):
                            for s in aliases:
                                if (aliases[s][0].find("Genbank ") == -1):
                                    out_file.write("{}/db_xref=\"{}:{}\"\n".format(" " * 21, aliases[s][0], s))
                                else:
                                    key = aliases[s][0].replace("Genbank ", "")
                                    out_file.write("{}/{}=\"{}\"\n".format(" " * 21, key, s))

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

                    allfunction = function.split(" ")
                    # what is the significance
                    format_function = formatAnnotation(function, allfunction, 48, 58)

                    out_file.write("{}CDS{}".format(" " * 5, " " * 13))
                    writeLocation(features[cds]['feature_locations'], out_file)
                    out_file.write("{}/kbase_id=\"{}\"\n".format(" " * 21, cds))

                    # out_file.write("                     /note=\"" + formatNote)
                    # out_file.write("                     /codon_start=1\n")
                    # out_file.write"                     /transl_table=11\n")
                    # out_file.write("                     /product=\"" + cds + "\"\n")
                    if format_function is not None:
                        out_file.write("{}/function=\"{}".format(" " * 21, format_function))
                    else:
                        out_file.write("{}/function=\"\"\n".format(" " * 21))

                    out_file.write("{}/protein_id=\"{}\"\n".format(" " * 21, cds))

                    aliases = features[cds]['feature_aliases']

                    ###TODO handle different alias cases and types
                    if len(aliases) > 0:
                        for s in aliases:
                            if (aliases[s][0].find("Genbank ") == -1):
                                out_file.write("{}/db_xref=\"{}:{}\"\n".format(" " * 21, aliases[s][0], s))
                            else:
                                key = aliases[s][0].replace("Genbank ", "")
                                out_file.write("{}/{}=\"{}\"\n".format(" " * 21, key, s))

                    getprot = proteins.get(cds)
                    if getprot is not None:
                        protein_translation = proteins[cds]['protein_amino_acid_sequence']
                        if (protein_translation is None):
                            protein_translation_final = ""
                        else:
                            # what is 44 and 58?
                            protein_translation_final = formatString(protein_translation, 44, 58)

                        out_file.write("{}/translation=\"{}".format(" " * 21, protein_translation_final))

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

#@profile
def writeLocation(feature_locations=None, out_file=None):
    added = 0
    complement = False
    isJoin = False
    numloc = len(feature_locations)
    for n in xrange(numloc):
        now4 = feature_locations[n]
        if added == 0 and now4['strand'] == "-":
            out_file.write("complement(")
            complement = True

        if (len(feature_locations) > 1):
            if (added == 0):
                out_file.write("join(")
            isJoin = True

        ###TODO output location info
        if complement == 0:
            start = now4['start']
            stop = now4['start'] + now4['length'] - 1
        else:
            start = now4['start'] - now4['length'] + 1
            stop = now4['start']

        out_file.write("{}..{}".format(start, stop))

        if numloc > 0 and n < (numloc - 1):
            out_file.write(",")
        added += 1

    tail = "\n"

    if complement:
        tail = ")" + tail
    if isJoin:
        tail = ")" + tail

    out_file.write(tail)

#@profile
def writeContig(contig_id=None, outfile=None, asm_api=None):
    contigdata = asm_api.get_contigs([contig_id])
    # significance of 10 and 60?
    outfile.write("ORIGIN\n")
    outfile.write(formatDNASequence(contigdata[contig_id]['sequence'], 10, 60))
    outfile.write("//\n")

#@profile
def formatAnnotation(function=None, allfunction=None, first=None, nexta=None):
    format_function = ""

    isfirst = True

    if len(function) < first:
        format_function = format_function + (function + "\"\n")
    else:
        counter2 = 0
        index2 = 0
        while (index2 < len(allfunction)):
            counter2 = counter2 + len(allfunction[index2]) + 1

            if (isfirst and counter2 >= first) or counter2 >= nexta:
                if isfirst:
                    isfirst = False

                if index2 < len(allfunction):
                    format_function = format_function + ("\n")
                    format_function = format_function + ("                     ")
                    format_function = format_function + (allfunction[index2])
                    counter2 = len(allfunction[index2])
                    if index2 < len(allfunction) - 1:
                        counter2 = counter2 + 1
                        format_function = format_function + (" ")
                    else:
                        format_function = format_function + ("\"\n")
            else:
                if index2 < len(allfunction):
                    format_function = format_function + allfunction[index2]
                    if index2 < len(allfunction) - 1:
                        counter2 = counter2 + 1
                        format_function = format_function + (" ")
                    else:
                        format_function = format_function + ("\"\n")
                else:
                    format_function = format_function + ("\"\n")

            index2 = index2 + 1

    if len(format_function) == 0 or format_function is None:
        format_function = "\"\n"

    formatindex = format_function.find("\"\n")

    if formatindex != len(format_function) - 2:
        format_function = format_function + ("\"\n")

    if len(format_function) == 0:
        format_function = ""

    return format_function


###formats a string into lines of given length (first line can be different)
#@profile
def formatString(s, one, two):
    s = s.replace("\"", "")
    out = ""
    first = True
    counter = 0
    start = 0
    size = len(s)

    while start < size:
        if first:
            lista = [size, start + one]
            last = min(lista)
            isLast = last == size
            out = out + s[start: last]

            if isLast:
                out = out + ("\"\n")
            else:
                out = out + ("\n")

            first = False
            start = start + one
        else:
            lista = [size, start + two]
            last = min(lista)
            out = out + ("                     ")
            isLast = last == size
            out = out + s[start:last]
            start = start + two

            if isLast:
                out = out + ("\"\n")
            else:
                out = out + ("\n")
        counter = counter + 1


    if len(out) == 0 or out is None:
        out = "\"\n"

    return out

###@profile
def formatDNASequence(s, charnum, linenum):
    out = StringIO.StringIO()
    # out += "        1 tctcgcagag ttcttttttg tattaacaaa cccaaaaccc atagaattta atgaacccaa\n"
    # start at position 1 of the sequence
    out.write("        1 ")
    index = 0
    size = len(s)
    end = 0
    while end < size:
        for n in xrange(linenum / charnum):
            # compute the boundary of the chunk
            end = index + charnum
            # if this runs past the end of the overall sequence length, take the remainder and exit
            if end > size:
                out.write(s[index:])
                index = size
                break
            else:
                out.write("{} ".format(s[index:index + charnum]))
                index += charnum
        # add a line break
        out.write("\n")
        if index >= size:
            break
        # if we haven't reached the end, write the current index starting from 1
        indexString = str(index + 1)
        out.write("{}{} ".format(" " * (9 - len(indexString)), indexString))
    return out.getvalue()


def testGBKDownload_vs_API(services, token, ref, output_file_name):
    ga_api = GenomeAnnotationAPI(services, token, ref)
    asm_api = ga_api.get_assembly();

    feature_counts = ga_api.get_feature_type_counts()
    print feature_counts

    gene = 0
    cds = 0
    mrna = 0
    contig = 0
    with open(output_file_name, "r") as f:
        for line in f:
            if line.find("     gene            ") != -1:
                gene = gene + 1
            elif line.find("     CDS             ") != -1:
                cds = cds + 1
            elif line.find("     mRNA            ") != -1:
                mrna = mrna + 1
            elif line.find("ORIGIN") == 0:
                contig = contig + 1

    if 'mRNA' in feature_counts.keys():
        if mrna != feature_counts['mRNA']:
            print "mrna count different " + str(mrna) + " vs " + str(feature_counts['mRNA'])
        else:
            print "mrnas agree"

    if cds != feature_counts['CDS']:
        print "cds count different " + str(cds) + " vs " + str(feature_counts['CDS'])
    else:
        print "cdss agree"

    if gene != feature_counts['gene']:
        print "gene count different " + str(gene) + " vs " + str(feature_counts['gene'])
    else:
        print "genes agree"

    numcontigs = len(asm_api.get_contig_ids())
    print "numcontigs "+str(numcontigs)
    if contig != numcontigs:
        print "contig count different " + str(contig) + " vs " + str(numcontigs)
    else:
        print "contigs agree"