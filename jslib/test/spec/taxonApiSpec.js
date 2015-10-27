/*global
 define, describe, expect, it
 */
/*jslint
 browser: true,
 white: true
 */
define([
    // This is the Taxon API
    'kb_data_taxon',
    // Session module for authentication, to get token.
    'kb_common_session',
        //,
        // Require js plugin for loading a yaml file
      'yaml!config/config.yml'
], function (Taxon, Session, config) {
    'use strict';

    //var config = {
    //    username: 'eapearson',
    //    password: 'Oc3an1cWhal3',
    //    loginUrl: 'https://ci.kbase.us/services/authorization/Sessions/Login',
    //    taxonUrl: 'http://euk.kbase.us/taxon',
    //    timeout: 30000,
    //    cookieName: 'testing',
    //    objectRef: '654/7'
    //};

    describe('Taxon API', function () {
        /* Basic tests */
        it('Gets the scientific name for a known taxon', function (done) {
            var objectRef = '654/7',
                session = Session.make({
                    cookieName: config.cookieName,
                    loginUrl: config.loginUrl
                });
            session.login({
                username: config.username,
                password: config.password
            })
                .then(function (kbSession) {
                    return Taxon({
                        ref: objectRef,
                        url: config.taxonUrl,
                        token: kbSession.token,
                        timeout: config.timeout
                    });
                })
                .then(function (taxon) {
                    return taxon.getScientificName();
                })
                .then(function (scientificName) {
                    expect(scientificName).toBe('Arabidopsis thaliana');
                    done();
                })
                .catch(function (err) {
                    console.log(err);
                    done.fail('Error fetching scientific name');
                });
        }, 20000);

         it('Gets the scientific name for a known taxon', function (done) {
            var objectRef = '654/7',
                session = Session.make({
                    cookieName: config.cookieName,
                    loginUrl: config.loginUrl
                });
            session.login({
                username: config.username,
                password: config.password
            })
                .then(function (kbSession) {
                    return Taxon({
                        ref: objectRef,
                        url: config.taxonUrl,
                        token: kbSession.token,
                        timeout: config.timeout
                    });
                })
                .then(function (taxon) {
                    return taxon.getScientificName();
                })
                .then(function (scientificName) {
                    expect(scientificName).toBe('Arabidopsis thaliana');
                    done();
                })
                .catch(function (err) {
                    console.log(err);
                    done.fail('Error fetching scientific name');
                });
        }, 20000);
    });
});

//    try {
//        var session = Session.make({
//            cookieName: config.cookieName,
//            loginUrl: config.loginUrl
//        });
//        utils.showField('config', 'objectRef', objectRef);
//        utils.showField('config', 'serviceUrl', config.taxonUrl);
//        utils.showField('config', 'timeout', config.timeout);
//        utils.showField('result', 'status', 'Logging in...');
//        start = new Date();
//        session.login({
//            username: config.username,
//            password: config.password
//        })
//            .then(function (kbSession) {
//                return Taxon({
//                    ref: objectRef,
//                    url: config.taxonUrl,
//                    token: kbSession.token,
//                    timeout: config.timeout
//                });
//            })
//            .then(function (taxon) {
//                utils.showField('result', 'status', 'Loading...');
//                start = new Date();
//                return taxon.getScientificName();
//            })
//            .then(function (value) {
//                utils.showField('result', 'status', 'Success!');
//                finish = new Date();
//                elapsed = finish.getTime() - start.getTime();
//                utils.showField('result', 'time', elapsed);
//                utils.showField('result', 'value', value);
//            })
//            .catch(function (err) {
//                // console.log('ERROR'); console.log(err);
//                finish = new Date();
//                elapsed = finish.getTime() - start.getTime();
//                utils.showField('result', 'time', elapsed);
//                if (err.type) {
//                    utils.showError(err);
//                } else if (utils.findProp(err, 'name', 'TException')) {
//                    utils.showError({
//                        type: 'ThriftException',
//                        reason: err.name,
//                        message: err.getMessage()
//                    });
//                } else {
//                    console.log('ERROR');
//                    console.log(err);
//                    var message = String(err) || 'Check the browser console';
//                    utils.showError({
//                        type: 'UnknownError',
//                        name: err.name,
//                        message: err.message
//                    });
//                }
//            });
//    } catch (ex) {
//        utils.showError(ex);
//    }
