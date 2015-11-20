# Data API for Assembly entities.  This API provides methods for retrieving
# summary information such as GC content, total length, external source information
# as well as methods for retrieving individual contig sequences and gathering contig lengths and contig GC.

require 5.6.0;
use strict;
use warnings;

use Thrift;
use Thrift::BinaryProtocol;
use Thrift::HttpClient;
use Thrift::BufferedTransport;

use DOEKBase::DataAPI::sequence::assembly::thrift_service;
use DOEKBase::DataAPI::sequence::assembly::Types;

package DOEKBase::DataAPI::sequence::assembly::ClientAPI;
use Try::Tiny;
use Carp;

sub new {
  my $classname = shift;
  my $self      = {};
  my $vals      = shift || {};

  foreach my $arg ('url','token','ref')
  {
    confess "Need to provide a $arg" unless $vals->{$arg};
  }

  my $transport = new Thrift::HttpClient($vals->{'url'});
  # the default timeout is too short
  $transport->setSendTimeout(30000);
  my $protocol  = new Thrift::BinaryProtocol($transport);
  my $client    = new DOEKBase::DataAPI::sequence::assembly::thrift_serviceClient($protocol);

  $transport->open();

  $self->{'client'} = $client;
  $self->{'token'} = $vals->{'token'};
  $self->{'ref'} = $vals->{'ref'};

  return bless($self,$classname);
  
}

sub get_assembly_id {
  my $self=shift;

  my $result = try {
    $self->{'client'}->get_assembly_id($self->{'token'},$self->{'ref'});
  } catch {
    confess 'Exception thrown: code ' . $_->{'code'} . ' message ' . $_->{'message'};
  };

  return $result;
}

sub get_genome_annotations {
  my $self=shift;

  my $result = try {
    $self->{'client'}->get_genome_annotations($self->{'token'},$self->{'ref'});
  } catch {
    confess 'Exception thrown: code ' . $_->{'code'} . ' message ' . $_->{'message'};
  };

  return $result;
}

sub get_external_source_info {
  my $self=shift;

  my $result = try {
    $self->{'client'}->get_external_source_info($self->{'token'},$self->{'ref'});
  } catch {
    confess 'Exception thrown: code ' . $_->{'code'} . ' message ' . $_->{'message'};
  };

  return $result;
}

sub get_stats {
  my $self=shift;

  my $result = try {
    $self->{'client'}->get_stats($self->{'token'},$self->{'ref'});
  } catch {
    confess 'Exception thrown: code ' . $_->{'code'} . ' message ' . $_->{'message'};
  };

  return $result;
}

sub get_number_contigs {
  my $self=shift;

  my $result = try {
    $self->{'client'}->get_number_contigs($self->{'token'},$self->{'ref'});
  } catch {
    confess 'Exception thrown: code ' . $_->{'code'} . ' message ' . $_->{'message'};
  };

  return $result;
}

sub get_gc_content {
  my $self=shift;

  my $result = try {
    $self->{'client'}->get_gc_content($self->{'token'},$self->{'ref'});
  } catch {
    confess 'Exception thrown: code ' . $_->{'code'} . ' message ' . $_->{'message'};
  };

  return $result;
}

sub get_dna_size {
  my $self=shift;

  my $result = try {
    $self->{'client'}->get_dna_size($self->{'token'},$self->{'ref'});
  } catch {
    confess 'Exception thrown: code ' . $_->{'code'} . ' message ' . $_->{'message'};
  };

  return $result;
}

sub get_contig_ids {
  my $self=shift;

  my $result = try {
    $self->{'client'}->get_contig_ids($self->{'token'},$self->{'ref'});
  } catch {
    confess 'Exception thrown: code ' . $_->{'code'} . ' message ' . $_->{'message'};
  };

  return $result;
}

sub get_contig_lengths {
  my $self=shift;

  my $result = try {
    $self->{'client'}->get_contig_lengths($self->{'token'},$self->{'ref'});
  } catch {
    confess 'Exception thrown: code ' . $_->{'code'} . ' message ' . $_->{'message'};
  };

  return $result;
}

sub get_contig_gc_content {
  my $self=shift;

  my $result = try {
    $self->{'client'}->get_contig_gc_content($self->{'token'},$self->{'ref'});
  } catch {
    confess 'Exception thrown: code ' . $_->{'code'} . ' message ' . $_->{'message'};
  };

  return $result;
}

sub get_contigs {
  my $self=shift;

  my $result = try {
    $self->{'client'}->get_contigs($self->{'token'},$self->{'ref'});
  } catch {
    confess 'Exception thrown: code ' . $_->{'code'} . ' message ' . $_->{'message'};
  };

  return $result;
}

1;
