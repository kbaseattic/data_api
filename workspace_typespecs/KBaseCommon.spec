/* Common types that may be reused in multiple other modules.
*/
module KBaseCommon {

    typedef int bool;

    /* An ID used for a piece of data at its source.
      @id external
    */
    typedef string source_id;

    /* An ID used for a project encompassing a piece of data at its source.
      @id external
    */
    typedef string project_id;

    /* Information about the source of a piece of data.
      source - the name of the source (e.g. NCBI, JGI, Swiss-Prot)
      source_id - the ID of the data at the source
      project_id - the ID of a project encompassing the data at the source

      @optional source source_id project_id
    */
    typedef structure {
      string source;
      source_id source_id;
      project_id project_id;
    } SourceInfo;
    
    /* Information about a location.
      lat - latitude of the site, recorded as a decimal number. North latitudes
          are positive values and south latitudes are negative numbers.
      lon - longitude of the site, recorded as a decimal number. West
          longitudes are positive values and east longitudes are negative
          numbers.
      elevation - elevation of the site, expressed in meters above sea level.
          Negative values are allowed.
      date - date of an event at this location (for example, sample
          collection), expressed in the format YYYY-MM-DDThh:mm:ss.SSSZ
      description - a free text description of the location and, if applicable,
          the associated event.

      @optional date description
    */
    typedef structure {
      float lat;
      float lon;
      float elevation;
      string date;
      string description;
    } Location;

    /* Information about a strain.
      genetic_code - the genetic code of the strain.
          See http://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi?mode=c
      genus - the genus of the strain
      species - the species of the strain
      strain - the identifier for the strain
      source - information about the source of the strain
      organelle - the organelle of interest for the related data (e.g.
          mitochondria)
      ncbi_taxid - the NCBI taxonomy ID of the strain
      location - the location from which the strain was collected

      @optional genetic_code source ncbi_taxid organelle location
    */
    typedef structure {
      int genetic_code;
      string genus;
      string species;
      string strain;
      string organelle;
      SourceInfo source;
      int ncbi_taxid;
      Location location;
    } StrainInfo;
};

