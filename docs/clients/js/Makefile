#
# Build JavaScript documentation from Thrift specs,
# using restructured text as the output.
#
# Author: Dan Gunter <dkgunter@lbl.gov>

ROOT_DIR=../../..
SPEC_DIR=${ROOT_DIR}/thrift/specs
DOCS_DIR=${ROOT_DIR}/docs

THRIFT=thrift

RST_FILES := taxon.rst assembly.rst genome_annotation.rst

default: build

build:
	@for spec in $$( find ${SPEC_DIR} -name "*.thrift" ); do \
	    n=$$(basename $$spec .thrift); \
		j=$$n.json; r=$$n.rst; \
		echo "$$n => $$r => ${DEST_DIR}/$$r"; \
		${THRIFT} -gen json -out . $$spec; \
		echo ./build_from_json $$j $$r; \
		./build_from_json $$j $$r; \
	done

clean:
	@echo "Clean up generated files"
	rm -f *.json *.rst
