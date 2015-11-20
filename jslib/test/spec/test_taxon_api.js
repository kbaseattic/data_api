// Run tests
define([
    'kb_data_taxon' // Taxon API
    ],
    function (Taxon, Session, config) {

    'use strict';

    var base_url = 'http://localhost:8000/localhost'
    var service_suffix = {
        object: ':9100',
        taxon: ':9101'}

    // Expected values for Taxon
    var taxon_ref = '993/674615/1'
    var taxon_data = {'GenBank_hidden_flag': 1,
                         'aliases': ['Melampsora laricis-populina 98AG31'],
                         'division_id': 4,
                         'domain': 'Eukaryota',
                         'genetic_code': 1,
                         'inherited_GC_flag': 1,
                         'inherited_MGC_flag': 1,
                         'inherited_div_flag': 1,
                         'kingdom': 'Fungi',
                         'mitochondrial_genetic_code': 4,
                         'parent_taxon_ref': '993/637363/2',
                         'rank': 'no rank',
                         'scientific_lineage': 'cellular organisms; Eukaryota; Opisthokonta; Fungi; Dikarya; Basidiomycota; Pucciniomycotina; Pucciniomycetes; Pucciniales; Melampsoraceae; Melampsora; Melampsora larici-populina',
                         'scientific_name': 'Melampsora larici-populina 98AG31',
                         'taxonomy_id': 747676
    }
    var taxon_lineage = taxon_data.scientific_lineage.split(';')
        .map(function (x) { return x.trim(' ') })

    // Taxon API tests
    describe('Taxon API', function () {
        var url = base_url + service_suffix.taxon
        console.log('Contacting Taxon API at: "' + url + '"')
            var taxon = Taxon({ ref: taxon_ref, url: url, token: '', timeout:
             6000})
        it('Gets the scientific lineage for a known taxon', function (done) {
            taxon.getScientificLineage()
                .then(function(lineage) {
                    //console.log('Got lineage: ' + lineage)
                    for (var i=0; i < taxon_lineage.length; i++) {
                        expect(lineage[i]).toBe(taxon_lineage[i])
                    }
                    done()
                    return null // not returning promise
                })
                .catch(function (err) {
                    console.error(err)
                    done.fail('Error fetching scientific lineage')
                    return null // not returning promise
                })
        }, 10000)
        it('Gets the scientific name for a known taxon', function (done) {
            taxon.getScientificName()
                .then(function(name) {
                    expect(name).toBe(taxon_data.scientific_name)
                    done()
                    return null // not returning promise
                 })
                .catch(function (err) {
                    console.error(err)
                    done.fail('Error fetching scientific name')
                    return null // not returning promise
                })
         }, 10000)
    })
})

