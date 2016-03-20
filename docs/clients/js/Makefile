#
# Build JavaScript documentation from Thrift specs,
# using restructured text as the output.
#
# Author: Dan Gunter <dkgunter@lbl.gov>

ROOT_DIR=../../..
SPEC_DIR=${ROOT_DIR}/thrift/specs
DOCS_DIR=${ROOT_DIR}/docs
BUILD=../build_from_json

THRIFT=thrift -I ${SPEC_DIR}/shared

RST_FILES := taxon.rst assembly.rst genome_annotation.rst

default: build

build:
	@for spec in $$( find ${SPEC_DIR} -name "*.thrift" ); do \
		leafdir=$$(basename $$(dirname $$spec)); \
		case $$leafdir in \
	        shared) echo "skipping $$leafdir" ;; \
	        *) n=$$(basename $$spec .thrift); \
		       j=$$n.json; r=$$n.rst; \
		       echo "$$n => $$j => $$r"; \
		       ${THRIFT} -gen json -out . $$spec; \
		       ${BUILD} $$j $$r; \
			   ;; \
		esac;\
	done

clean:
	@echo "Clean up generated files"
	rm -f *.json *.rst
