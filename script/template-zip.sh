#!/bin/bash

set -e # exit with error if any of this fails

script_dir="$(dirname "$(readlink -f "$0")")"
cd "${script_dir}/.."
repo_root="$(pwd)"

chapter_dir="tex/Authors/Moreno"
out_zip="${1:-gptp2026-template.zip}"

stage="$(mktemp -d)"
trap 'rm -rf "${stage}"' EXIT

mkdir -p "${stage}/Authors/Moreno/img"

# flatten Author.tex and its \input chain (Author-*.tex chapter sections,
# fig/*.tex figure snippets) into a single self-contained file; TEXINPUTS
# covers both the chapter-local includes and the shared tex/fig includes
TEXINPUTS="${chapter_dir}:tex:." ./script/latexpand.pl "${chapter_dir}/Author.tex" \
  > "${stage}/Authors/Moreno/Author.tex.raw"

# localize every \includegraphics dependency -- including the teeplot
# figures pulled in from sibling bindle/binder submodules -- into a flat
# img/ folder shipped alongside Author.tex, and rewrite the references
perl - "${stage}/Authors/Moreno/Author.tex.raw" "${stage}/Authors/Moreno/Author.tex" "${stage}/Authors/Moreno/img" <<'PERL_EOF'
use strict;
use warnings;
use File::Basename qw(basename);
use File::Copy qw(copy);

my ($src, $dst, $imgdir) = @ARGV;
my @exts = ("", ".pdf", ".png", ".jpg", ".jpeg", ".eps");

open(my $IN, "<", $src) or die "could not open $src: $!\n";
local $/;
my $text = <$IN>;
close($IN);

my %basename_for; # resolved path -> assigned img/ basename
my %owner_of;      # img/ basename -> resolved path

$text =~ s{
  \\includegraphics(\[[^\]]*\])?\{([^\}]*)\}
}{
  my ($opts, $path) = ($1 // "", $2);
  my $resolved;
  for my $ext (@exts) {
    my $candidate = "tex/${path}${ext}";
    if (-f $candidate) { $resolved = $candidate; last; }
  }
  die "could not resolve graphics file referenced as '$path'\n" unless $resolved;

  my $chosen = $basename_for{$resolved};
  unless (defined $chosen) {
    $chosen = basename($resolved);
    die "graphics filename collision: '$chosen' resolves to both "
      . "'$owner_of{$chosen}' and '$resolved'\n" if exists $owner_of{$chosen};
    $basename_for{$resolved} = $chosen;
    $owner_of{$chosen} = $resolved;
    copy($resolved, "$imgdir/$chosen") or die "could not copy $resolved to $imgdir/$chosen: $!\n";
  }
  "\\includegraphics${opts}{img/$chosen}"
}gex;

open(my $OUT, ">", $dst) or die "could not open $dst: $!\n";
print $OUT $text;
close($OUT);
PERL_EOF

rm "${stage}/Authors/Moreno/Author.tex.raw"

# ship the bibliography/style resources that accompany the chapter
# template, and repoint the bibliography command at the now-colocated .bib
cp "${chapter_dir}/reference.bib" "${stage}/Authors/Moreno/"
cp "${chapter_dir}/spmpsci.bst" "${stage}/Authors/Moreno/"
cp "${chapter_dir}/svmult.cls" "${stage}/Authors/Moreno/"
sed -i 's#\\bibliography{Authors/Moreno/reference}#\\bibliography{reference}#' \
  "${stage}/Authors/Moreno/Author.tex"

rm -f "${out_zip}"
(cd "${stage}" && zip -qr "${repo_root}/${out_zip}" Authors)

echo "wrote ${out_zip}"

# test-build: unzip the archive just written and compile it completely on
# its own, standing in for what Springer's build will do with the
# submission. Reuses the real preamble (main.tex's \documentclass plus
# document.tex's packages) so this step tracks the live book build instead
# of a hand-maintained copy, swapping the multi-file \subincludefrom for a
# plain \input of the now-self-contained, unzipped Author.tex.
test_build="$(mktemp -d)"
trap 'rm -rf "${stage}" "${test_build}"' EXIT

unzip -q "${out_zip}" -d "${test_build}"
{
  grep -E '^\\documentclass' main.tex
  grep -E '^\\def\\nofake' main.tex
  sed 's#\\subincludefrom{Authors/Moreno/}{Author}#\\input{Author}#' tex/document.tex
} > "${test_build}/Authors/Moreno/test-build.tex"

(
  cd "${test_build}/Authors/Moreno"
  latexmk -pdf -silent -interaction=nonstopmode -halt-on-error \
    -pdflatex="pdflatex -interaction=nonstopmode -halt-on-error" \
    test-build.tex
)

echo "verified ${out_zip} builds standalone"
