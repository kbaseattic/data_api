/**
 *
 */
define([
    'kb_data_taxon' // Taxon API
    ],
    function (Taxon, Session, config) {

    'use strict';

    var base_url = 'http://127.0.0.1:8000';
    var service_suffix = {object: '/object', taxon: '/taxon'} // XXX: etc.

    // Taxon API tests
    describe('Taxon API', function () {
        var url = base_url + service_suffix.taxon
        console.log('Contacting Taxon API at:', url)
        it('Gets the scientific name for a known taxon', function (done) {
            var taxon = Taxon({ ref: "993/674615/1",
                    url: url,
                    token: "",
                    timeout: 6000})
            taxon.getScientificName()
                .then(function(name) {
                    expect(name).toBe('Melampsora larici-populina 98AG31')
                    done()
                 })
                .catch(function (err) {
                    console.error(err)
                    done.fail('Error fetching scientific name')
                })
        }, 20000)
    })
})

