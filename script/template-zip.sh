#!/bin/bash

set -e # exit with error if any of this fails

script_dir="$(dirname "$(readlink -f "$0")")"
cd "${script_dir}/.."
repo_root="$(pwd)"

chapter_dir="tex/Authors/Moreno"
out_zip="${1:-moreno-chapter.zip}"

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

# \orcidlink needs hyperref+tikz loaded from a preamble, which Author.tex
# doesn't have (it's \input into the book's \begin{document}), and the
# submission guidelines ask to avoid unusual packages -- so swap the icon
# macro for a plain-text ORCID mention instead of shipping orcidlink.sty
sed -i -E 's/\\orcidlink\{([^}]*)\}/(ORCID~\1)/g' \
  "${stage}/Authors/Moreno/Author.tex"

rm -f "${out_zip}"
out_zip_abs="${repo_root}/${out_zip}"
perl - "${stage}" "${out_zip_abs}" <<'PERL_EOF'
# zip (the CLI tool) isn't guaranteed to be present in the LaTeX build
# image, but IO::Compress::Zip ships with core perl, which latexpand.pl
# already depends on -- so use that instead of shelling out.
use strict;
use warnings;
use File::Find;
use IO::Compress::Zip qw(zip $ZipError);

my ($stage, $out) = @ARGV;
my @files;
find(sub { push @files, $File::Find::name if -f }, "$stage/Authors");

my $prefix = quotemeta("$stage/");
zip(\@files, $out, FilterName => sub { s{^$prefix}{} })
  or die "could not write $out: $ZipError\n";
PERL_EOF

echo "wrote ${out_zip}"

# test-build: compile the staged chapter directory -- the exact contents
# just written into the zip -- completely on its own, standing in for what
# Springer's build will do with the submission. Reuses the real preamble
# (main.tex's \documentclass plus document.tex's packages) so this step
# tracks the live book build instead of a hand-maintained copy, swapping
# the multi-file \subincludefrom for a plain \input of the now
# self-contained Author.tex.
{
  grep -E '^\\documentclass' main.tex
  grep -E '^\\def\\nofake' main.tex
  # Author.tex no longer uses \orcidlink (see above), so drop
  # document.tex's \usepackage{orcidlink} too -- it would otherwise need
  # orcidlink.sty on the search path from this standalone compile location
  sed -e 's#\\subincludefrom{Authors/Moreno/}{Author}#\\input{Author}#' \
      -e '/^\\usepackage{orcidlink}$/d' \
      tex/document.tex
} > "${stage}/Authors/Moreno/test-build.tex"

if ! (
  cd "${stage}/Authors/Moreno"
  latexmk -pdf -silent -interaction=nonstopmode -file-line-error -halt-on-error \
    -pdflatex="pdflatex -interaction=nonstopmode -file-line-error -halt-on-error" \
    test-build.tex
); then
  echo "template zip test-build failed; dumping test-build.log:" >&2
  cat "${stage}/Authors/Moreno/test-build.log" >&2 || true
  exit 1
fi

echo "verified ${out_zip} builds standalone"
