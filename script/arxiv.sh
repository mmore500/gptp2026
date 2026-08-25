#!/bin/bash

set -e # exit with error if any of this fails

script_dir="$(dirname "$(readlink -f "$0")")"
cd "${script_dir}/.."
repo_root="$(pwd)"

out_zip="${1:-arxiv.zip}"
# document.tex loads chapterbib, which gives each \subincludefrom'd
# chapter its own independent bibtex run keyed to the chapter's own file
# basename rather than \jobname -- so building gptp2026-draft.pdf leaves
# the compiled bibliography at Author.bbl, not gptp2026-draft.bbl.
bbl="${2:-${repo_root}/Author.bbl}"

if [ ! -f "${bbl}" ]; then
  echo "error: bibliography file '${bbl}' not found" >&2
  echo "build the manuscript first (e.g. 'make gptp2026-draft.pdf') to generate it" >&2
  exit 1
fi

stage="$(mktemp -d)"
trap 'rm -rf "${stage}"' EXIT

mkdir -p "${stage}/img"

# arXiv wants one self-contained submission: no external \include chain,
# and (per arXiv's own submission guidance) a pre-compiled .bbl rather
# than a .bib/.bst pair, since automated bibtex invocation on arXiv's end
# is unreliable for nonstandard styles like the Springer spmpsci.bst used
# here. So flatten the *whole* manuscript (not just the chapter, as
# moreno-chapter.zip does for the Springer submission) into one file with
# the bibliography inlined.

# assemble the top-level document the same way main.tex/draft.tex +
# document.tex do (they're identical for this purpose), swapping
# subincludefrom (the import package's \include analogue) for a plain
# \input -- latexpand.pl only expands \input/\include/\import, not the
# \includefrom family, so left as-is it would never get flattened
{
  grep -E '^\\documentclass' main.tex
  grep -E '^\\def\\nofake' main.tex
  sed 's#\\subincludefrom{Authors/Moreno/}{Author}#\\input{Authors/Moreno/Author}#' tex/document.tex
} > "${stage}/root.tex.pre"

TEXINPUTS="tex/Authors/Moreno:tex:." ./script/latexpand.pl --expand-bbl "${bbl}" \
  "${stage}/root.tex.pre" > "${stage}/arxiv.tex.raw"
rm "${stage}/root.tex.pre"

# localize every \includegraphics dependency -- including the teeplot
# figures pulled in from sibling bindle/binder submodules -- into a flat
# img/ folder shipped alongside arxiv.tex, and rewrite the references
perl - "${stage}/arxiv.tex.raw" "${stage}/arxiv.tex" "${stage}/img" <<'PERL_EOF'
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

rm "${stage}/arxiv.tex.raw"

# ship the document class -- svmult isn't part of standard TeX Live, so
# arXiv's build needs its own copy
cp svmult.cls "${stage}/"

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
find(sub { push @files, $File::Find::name if -f }, $stage);

my $prefix = quotemeta("$stage/");
zip(\@files, $out, FilterName => sub { s{^$prefix}{} })
  or die "could not write $out: $ZipError\n";
PERL_EOF

echo "wrote ${out_zip}"

# test-build: compile the exact contents just written into the zip,
# standing in for arXiv's own automated compilation. No BIBINPUTS,
# TEXINPUTS, or bibtex invocation is needed here -- the bibliography is
# already inlined into arxiv.tex and every graphic already lives in img/.
if ! (
  cd "${stage}"
  latexmk -pdf -silent -interaction=nonstopmode -file-line-error -halt-on-error \
    -pdflatex="pdflatex -interaction=nonstopmode -file-line-error -halt-on-error" \
    arxiv.tex
); then
  echo "arxiv zip test-build failed; dumping arxiv.log:" >&2
  cat "${stage}/arxiv.log" >&2 || true
  exit 1
fi

echo "verified ${out_zip} builds standalone"
